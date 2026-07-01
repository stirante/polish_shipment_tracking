from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, CoreState, EVENT_HOMEASSISTANT_STARTED, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.components import websocket_api
import voluptuous as vol

from .const import DOMAIN, PLATFORMS, INTEGRATION_VERSION, CONF_COURIER
from .frontend import JSModuleRegistration
from .coordinator import ShipmentCoordinator

_LOGGER = logging.getLogger(__name__)


async def _async_migrate_unique_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Account-scope per-parcel entity unique_ids.

    Old scheme `{courier}_{number}` (and `_refresh`/`_manage` variants) was not
    scoped per account, so two accounts of the same courier collided. Rewrite to
    `{courier}_{entry_id}_{number}`. Idempotent and per-entry; the refresh-all
    button already carries the entry_id so it is left untouched.
    """
    courier = entry.data.get(CONF_COURIER)
    if not courier:
        return
    prefix = f"{courier}_"
    scoped_prefix = f"{courier}_{entry.entry_id}"

    @callback
    def _migrator(entity_entry: er.RegistryEntry) -> dict | None:
        uid = entity_entry.unique_id or ""
        if not uid.startswith(prefix) or uid.startswith(scoped_prefix):
            return None
        rest = uid[len(prefix):]
        return {"new_unique_id": f"{courier}_{entry.entry_id}_{rest}"}

    await er.async_migrate_entries(hass, entry.entry_id, _migrator)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Shipment Tracking integration."""
    hass.data.setdefault(DOMAIN, {})
    
    async def async_register_frontend(_event=None) -> None:
        """Register the JavaScript modules after Home Assistant startup."""
        module_register = JSModuleRegistration(hass)
        await module_register.async_register()

    # Websocket handler to expose the integration version to the frontend.
    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/version"})
    @websocket_api.async_response
    async def websocket_get_version(
        hass: HomeAssistant,
        connection: websocket_api.ActiveConnection,
        msg: dict,
    ) -> None:
        """Handle version requests from the frontend."""
        connection.send_result(msg["id"], {"version": INTEGRATION_VERSION})

    websocket_api.async_register_command(hass, websocket_get_version)

    # Schedule frontend registration based on HA state.
    if hass.state == CoreState.running:
        await async_register_frontend()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_register_frontend)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up from a config entry."""
    await _async_migrate_unique_ids(hass, entry)

    coordinator = ShipmentCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        # Don't leak the DHL-owned aiohttp session if first refresh fails.
        await coordinator.async_close()
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
        if coordinator is not None:
            await coordinator.async_close()

    # If no more entries, unregister frontend? 
    # Actually, keep it for now as there might be other entries.
    # The original code did some logic here for global sensor.
    
    return unload_ok

