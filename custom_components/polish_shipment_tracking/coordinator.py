from datetime import timedelta
import asyncio
import logging
import json
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    CONF_REFRESH_EXPIRES_AT,
    CONF_COURIER,
    CONF_DEVICE_UID,
)

_LOGGER = logging.getLogger(__name__)

class ShipmentCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry: ConfigEntry):
        self.entry = entry
        self.entry_data = entry.data
        self.courier = self.entry_data[CONF_COURIER]
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"Shipment Tracking {self.courier}",
            update_interval=timedelta(minutes=15),
        )
        
        self.session = async_get_clientsession(hass)
        self.api = self._get_api_instance()

    def _get_api_instance(self):
        token = self.entry_data.get(CONF_TOKEN)
        refresh_token = self.entry_data.get(CONF_REFRESH_TOKEN)
        device_uid = self.entry_data.get(CONF_DEVICE_UID)
        
        if self.courier == "inpost":
            from .api import InPostApi
            api = InPostApi(self.session, device_uid=device_uid)
            api._token = token
            api._refresh_token = refresh_token
            return api
            
        elif self.courier == "dpd":
            from .api import DpdApi
            api = DpdApi(self.session)
            api._token = token
            api._refresh_token = refresh_token
            return api
            
        elif self.courier == "dhl":
            from .api import DhlApi
            api = DhlApi(self.session, device_id=device_uid)
            api._token = token
            
            cookies_json = self.entry_data.get("cookies")
            if cookies_json:
                try:
                    api._cookies = json.loads(cookies_json)
                except Exception as e:
                    _LOGGER.warning("Failed to restore DHL cookies: %s", e)
            
            return api
        elif self.courier == "pocztex":
            from .api import PocztexApi
            api = PocztexApi(self.session)
            api._token = token
            api._refresh_token = refresh_token
            api._expires_at = self.entry_data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            api._refresh_expires_at = self.entry_data.get(CONF_REFRESH_EXPIRES_AT, 0) or 0
            return api
        return None

    async def _async_update_data(self):
        try:
            if self.courier == "inpost":
                try:
                    data = await self.api.get_parcels()
                except Exception as e:
                    # Handle 401 errors for InPost.
                    if "401" in str(e):
                        _LOGGER.info("InPost token expired, refreshing...")
                        await self.api.refresh_token()
                        
                        # Persist refreshed tokens.
                        new_data = {**self.entry_data}
                        new_data[CONF_TOKEN] = self.api._token
                        if self.api._refresh_token:
                            new_data[CONF_REFRESH_TOKEN] = self.api._refresh_token
                        
                        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                        self.entry_data = new_data
                        
                        # Retry the request.
                        data = await self.api.get_parcels()
                    else:
                        raise e

                return data if isinstance(data, list) else data.get("parcels", [])
                
            elif self.courier == "dpd":
                try:
                    data = await self.api.get_parcels()
                except Exception as e:
                    if "401" in str(e):
                        _LOGGER.info("DPD token expired, refreshing...")
                        await self.api.refresh_access_token()

                        new_data = {**self.entry_data}
                        new_data[CONF_TOKEN] = self.api._token
                        if self.api._refresh_token:
                            new_data[CONF_REFRESH_TOKEN] = self.api._refresh_token

                        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                        self.entry_data = new_data

                        data = await self.api.get_parcels()
                    else:
                        raise e
                if isinstance(data, list): return data
                if "packages" in data: return data["packages"]
                if "parcelList" in data: return data["parcelList"]
                if "shipments" in data: return data["shipments"]
                return []
                
            elif self.courier == "dhl":
                try:
                    data = await self.api.get_parcels()
                except Exception as e:
                    # Handle 401 errors for DHL.
                    if "401" in str(e):
                        _LOGGER.info("DHL token expired, refreshing...")
                        await self.api.refresh_token()
                        
                        # Persist refreshed data (token + cookies).
                        new_data = {**self.entry_data}
                        new_data[CONF_TOKEN] = self.api._token
                        new_data["cookies"] = json.dumps(self.api._cookies)
                        
                        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                        self.entry_data = new_data
                        
                        # Retry the request.
                        data = await self.api.get_parcels()
                    else:
                        raise e
                        
                return data.get("shipments", [])

            elif self.courier == "pocztex":
                try:
                    data = await self.api.get_parcels()
                except Exception as e:
                    if "401" in str(e):
                        _LOGGER.info("Pocztex token expired, refreshing...")
                        await self.api.refresh_token()

                        new_data = {**self.entry_data}
                        new_data[CONF_TOKEN] = self.api._token
                        new_data[CONF_REFRESH_TOKEN] = self.api._refresh_token
                        new_data[CONF_TOKEN_EXPIRES_AT] = self.api._expires_at
                        new_data[CONF_REFRESH_EXPIRES_AT] = self.api._refresh_expires_at

                        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                        self.entry_data = new_data

                        data = await self.api.get_parcels()
                    else:
                        raise e

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
                    if isinstance(details, Exception):
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
                
        except Exception as err:
            _LOGGER.error(f"Error fetching data for {self.courier}: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")
