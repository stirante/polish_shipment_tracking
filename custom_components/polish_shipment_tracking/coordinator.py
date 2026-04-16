from datetime import timedelta
import asyncio
import logging
import json
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    CONF_REFRESH_EXPIRES_AT,
    CONF_COURIER,
    CONF_DEVICE_UID,
)
from .helpers import get_parcel_detail_id, get_parcel_id
from .helpers import is_delivered

_LOGGER = logging.getLogger(__name__)

class ShipmentCoordinator(DataUpdateCoordinator):
    """Class to manage fetching shipment data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the coordinator."""
        self.entry = entry
        self.courier = entry.data[CONF_COURIER]
        self.known_parcels = set()
        self.add_entities_callback = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"Shipment Tracking {self.courier}",
            update_interval=timedelta(minutes=15),
        )
        
        self.session = async_get_clientsession(hass)
        self.api = self._get_api_instance()

    def _get_api_instance(self):
        """Get API instance based on courier."""
        data = self.entry.data
        token = data.get(CONF_TOKEN)
        refresh_token = data.get(CONF_REFRESH_TOKEN)
        device_uid = data.get(CONF_DEVICE_UID)
        
        if self.courier == "inpost":
            from .api_inpost import InPostApi
            api = InPostApi(self.session, device_uid=device_uid)
            api._token = token
            api._refresh_token = refresh_token
            return api
            
        elif self.courier == "dpd":
            from .api_dpd import DpdApi
            api = DpdApi(self.session)
            api._token = token
            api._refresh_token = refresh_token
            api._expires_at = data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            return api
            
        elif self.courier == "dhl":
            from .api_dhl import DhlApi
            api = DhlApi(self.session, device_id=device_uid)
            api._token = token
            
            cookies_json = data.get("cookies")
            if cookies_json:
                try:
                    api._cookies = json.loads(cookies_json)
                except Exception as e:
                    _LOGGER.warning("Failed to restore DHL cookies: %s", e)
            
            return api

        elif self.courier == "pocztex":
            from .api_pocztex import PocztexApi
            api = PocztexApi(self.session)
            api._token = token
            api._refresh_token = refresh_token
            api._expires_at = data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            api._refresh_expires_at = data.get(CONF_REFRESH_EXPIRES_AT, 0) or 0
            return api
        return None

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            parcels = await self._fetch_parcels_with_retry()
            return self._filter_active_parcels(parcels)
        except Exception as err:
            _LOGGER.error("Error fetching data for %s: %s", self.courier, err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_parcels_with_retry(self):
        """Fetch parcels and retry once if unauthorized."""
        try:
            return await self._fetch_parcels()
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                _LOGGER.info("%s token expired, refreshing...", self.courier)
                await self._refresh_token()
                return await self._fetch_parcels()
            raise e

    async def _fetch_single_parcel_with_retry(self, tracking_number: str):
        """Fetch one parcel and retry once if unauthorized."""
        try:
            return await self._fetch_single_parcel(tracking_number)
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                _LOGGER.info("%s token expired while fetching single parcel, refreshing...", self.courier)
                await self._refresh_token()
                return await self._fetch_single_parcel(tracking_number)
            raise e

    async def _fetch_parcels(self):
        """Fetch parcels from API without retry logic."""
        if self.courier == "inpost":
            data = await self.api.get_parcels()
            return data if isinstance(data, list) else data.get("parcels", [])
            
        elif self.courier == "dpd":
            data = await self.api.get_parcels()
            parcels = []
            if isinstance(data, list):
                parcels = data
            elif isinstance(data, dict):
                if "packages" in data:
                    parcels = data["packages"]
                elif "parcelList" in data:
                    parcels = data["parcelList"]
                elif "shipments" in data:
                    parcels = data["shipments"]
            if not parcels:
                return []
            return await self._enrich_dpd_parcels(parcels)
            
        elif self.courier == "dhl":
            data = await self.api.get_parcels()
            return data.get("shipments", [])

        elif self.courier == "pocztex":
            data = await self.api.get_parcels()
            parcels = []
            if isinstance(data, list):
                parcels = data
            elif isinstance(data, dict):
                for key in ("packages", "items", "tracking", "data", "content"):
                    if key in data and isinstance(data[key], list):
                        parcels = data[key]
                        break
            if not parcels:
                return []

            # Pocztex needs separate calls for details
            detail_tasks = []
            for parcel in parcels:
                detail_id = None
                if isinstance(parcel, dict):
                    detail_id = get_parcel_detail_id(parcel, self.courier)
                if detail_id is None:
                    detail_tasks.append(asyncio.sleep(0, result=None))
                else:
                    detail_tasks.append(self.api.get_parcel_details(detail_id))

            details_results = await asyncio.gather(*detail_tasks, return_exceptions=True)
            enriched = []
            for parcel, details in zip(parcels, details_results):
                if isinstance(details, Exception) or details is None:
                    enriched.append(parcel)
                    continue

                if isinstance(parcel, dict):
                    merged = dict(parcel)
                    if isinstance(details, dict):
                        merged.update(details)
                    merged["_raw_response"] = details
                    enriched.append(merged)
                else:
                    enriched.append(parcel)
            return enriched
        
        return []

    async def _enrich_dpd_parcels(self, parcels):
        """Fetch DPD parcel details to expose fields missing from the list endpoint."""
        semaphore = asyncio.Semaphore(5)

        async def _fetch_details(parcel):
            if not isinstance(parcel, dict):
                return parcel

            tracking_number = get_parcel_id(parcel, self.courier)
            if not tracking_number:
                return parcel

            try:
                async with semaphore:
                    details = await self.api.get_parcel(tracking_number)
            except Exception as err:
                _LOGGER.debug(
                    "Failed to fetch DPD parcel details for %s, keeping list payload: %s",
                    tracking_number,
                    err,
                )
                return parcel

            detail_parcel = self._extract_single_parcel(details, tracking_number)
            if not isinstance(detail_parcel, dict):
                return parcel

            merged = dict(parcel)
            merged.update(detail_parcel)
            merged["_raw_response"] = detail_parcel
            return merged

        details_results = await asyncio.gather(
            *(_fetch_details(parcel) for parcel in parcels),
            return_exceptions=True,
        )

        enriched = []
        for parcel, result in zip(parcels, details_results):
            if isinstance(result, Exception):
                enriched.append(parcel)
            else:
                enriched.append(result)
        return enriched

    async def _fetch_single_parcel(self, tracking_number: str):
        """Fetch a single parcel details for couriers that support it."""
        if self.courier in {"inpost", "dpd", "dhl"}:
            if not hasattr(self.api, "get_parcel"):
                return None
            data = await self.api.get_parcel(tracking_number)
            self._log_single_parcel_response(tracking_number, data)
            return self._extract_single_parcel(data, tracking_number)

        if self.courier == "pocztex":
            if not hasattr(self.api, "get_parcel_details"):
                return None
            detail_id = tracking_number
            current_data = self.data or []
            existing_parcel = next(
                (
                    item
                    for item in current_data
                    if str(get_parcel_id(item, self.courier) or "") == str(tracking_number)
                ),
                None,
            )
            if isinstance(existing_parcel, dict):
                detail_id = get_parcel_detail_id(existing_parcel, self.courier) or tracking_number

            data = await self.api.get_parcel_details(detail_id)
            self._log_single_parcel_response(detail_id, data)
            if not isinstance(data, dict):
                return None
            merged = dict(existing_parcel) if isinstance(existing_parcel, dict) else {}
            merged.update(data)
            merged["_raw_response"] = data
            return merged

        return None

    def _extract_single_parcel(self, data, tracking_number: str):
        """Extract a single parcel dict from varied courier response formats."""
        if isinstance(data, dict):
            candidate_dicts = [data]
            for key in ("parcel", "shipment", "package", "data", "item"):
                nested = data.get(key)
                if isinstance(nested, dict):
                    candidate_dicts.append(nested)
                elif isinstance(nested, list):
                    candidate_dicts.extend([x for x in nested if isinstance(x, dict)])
            for candidate in candidate_dicts:
                if str(get_parcel_id(candidate, self.courier) or "") == str(tracking_number):
                    return candidate
            return data

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and str(get_parcel_id(item, self.courier) or "") == str(tracking_number):
                    return item
            return None

        return None

    def _log_single_parcel_response(self, tracking_number: str, data) -> None:
        """Log raw single-parcel response as JSON at WARNING level for local testing."""
        try:
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str)
        except Exception:
            payload = str(data)
        _LOGGER.debug(
            "Single parcel raw response [%s][%s]: %s",
            self.courier,
            tracking_number,
            payload,
        )

    def _filter_active_parcels(self, parcels):
        """Keep only active parcels in coordinator data."""
        if not isinstance(parcels, list):
            return []
        return [
            parcel
            for parcel in parcels
            if isinstance(parcel, dict) and not is_delivered(parcel, self.courier)
        ]

    async def async_refresh_parcel(self, tracking_number: str) -> None:
        """Refresh a single parcel when courier API supports it.

        Falls back to full coordinator refresh if single fetch fails or returns unknown shape.
        """
        try:
            parcel = await self._fetch_single_parcel_with_retry(tracking_number)
        except Exception as err:
            _LOGGER.debug(
                "Single parcel refresh failed for %s %s, falling back to full refresh: %s",
                self.courier,
                tracking_number,
                err,
            )
            await self.async_request_refresh()
            return

        if not isinstance(parcel, dict):
            await self.async_request_refresh()
            return

        current_data = list(self.data or [])
        replaced = False
        for idx, item in enumerate(current_data):
            if str(get_parcel_id(item, self.courier) or "") == str(tracking_number):
                current_data[idx] = parcel
                replaced = True
                break

        if not replaced:
            current_data.append(parcel)

        self.async_set_updated_data(self._filter_active_parcels(current_data))

    async def _refresh_token(self):
        """Refresh API token and update config entry."""
        if self.courier == "inpost":
            await self.api.refresh_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
            }
        elif self.courier == "dpd":
            await self.api.refresh_access_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
            }
        elif self.courier == "dhl":
            await self.api.refresh_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                "cookies": json.dumps(self.api._cookies),
            }
        elif self.courier == "pocztex":
            await self.api.refresh_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
                CONF_REFRESH_EXPIRES_AT: self.api._refresh_expires_at,
            }
        else:
            return

        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
