from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, CoreState, EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers import config_validation as cv
from homeassistant.components import websocket_api
import voluptuous as vol

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

    # Schedule frontend registration based on HA state.
    if hass.state == CoreState.running:
        await async_register_frontend()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_register_frontend)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up from a config entry."""
    coordinator = ShipmentCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    # If no more entries, unregister frontend? 
    # Actually, keep it for now as there might be other entries.
    # The original code did some logic here for global sensor.
    
    return unload_ok

