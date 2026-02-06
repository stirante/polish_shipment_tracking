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
            return await self._fetch_parcels_with_retry()
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

    async def _fetch_parcels(self):
        """Fetch parcels from API without retry logic."""
        if self.courier == "inpost":
            data = await self.api.get_parcels()
            return data if isinstance(data, list) else data.get("parcels", [])
            
        elif self.courier == "dpd":
            data = await self.api.get_parcels()
            if isinstance(data, list): return data
            if "packages" in data: return data["packages"]
            if "parcelList" in data: return data["parcelList"]
            if "shipments" in data: return data["shipments"]
            return []
            
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
                    detail_id = (
                        parcel.get("id")
                        or parcel.get("trackingId")
                        or parcel.get("trackingID")
                    )
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
