from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, CoreState, EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers import config_validation as cv
from homeassistant.components import websocket_api
import voluptuous as vol

from . import delivery_store
from .const import DOMAIN, PLATFORMS, INTEGRATION_VERSION
from .frontend import JSModuleRegistration
from .coordinator import ShipmentCoordinator

_LOGGER = logging.getLogger(__name__)

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

    await delivery_store.async_load(hass)

    # Schedule frontend registration based on HA state.
    if hass.state == CoreState.running:
        await async_register_frontend()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_register_frontend)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up from a config entry."""
    coordinator = ShipmentCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        # Don't leak the DHL-owned aiohttp session if first refresh fails.
        await coordinator.async_close()
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(coordinator.async_start_linking())
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload so new recipient filters (or a new Allegro cookie) apply."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator is not None and not coordinator.entry_changed_since_setup():
        # Only tokens the coordinator saved itself changed.
        return
    await hass.config_entries.async_reload(entry.entry_id)

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

