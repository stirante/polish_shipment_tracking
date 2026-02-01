from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, CoreState, EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import config_validation as cv
from homeassistant.components import websocket_api
import voluptuous as vol

from .const import DOMAIN, LEGACY_DOMAIN, PLATFORMS, INTEGRATION_VERSION
from .frontend import JSModuleRegistration
from .coordinator import ShipmentCoordinator
from .sensor import ShipmentSensor, _pick_pocztex_id, _pick_pocztex_status, _normalize_status

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Shipment Tracking integration and register frontend resources."""
    hass.data.setdefault(DOMAIN, {})
    await _async_import_legacy_entries(hass)

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

    # Register the websocket command.
    websocket_api.async_register_command(hass, websocket_get_version)

    # Schedule frontend registration based on HA state.
    if hass.state == CoreState.running:
        await async_register_frontend()
    else:
        # Wait for Home Assistant to start before registering.
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_register_frontend)

    return True


async def _async_import_legacy_entries(hass: HomeAssistant) -> None:
    """Import legacy config entries from shipment_tracking domain."""
    legacy_entries: list[ConfigEntry] = [
        e for e in hass.config_entries.async_entries(LEGACY_DOMAIN)
        if not e.disabled_by
    ]

    if not legacy_entries:
        return

    _LOGGER.warning(
        "Found %d legacy '%s' config entries. Importing into '%s'...",
        len(legacy_entries), LEGACY_DOMAIN, DOMAIN
    )

    existing_new = hass.config_entries.async_entries(DOMAIN)

    # simple dedupe based on courier+phone+email
    def _fingerprint(entry: ConfigEntry) -> tuple:
        d = entry.data or {}
        return (
            d.get("courier"),
            d.get("phone"),
            d.get("email"),
        )

    existing_fps = {_fingerprint(e) for e in existing_new}

    ent_reg = er.async_get(hass)

    for legacy in legacy_entries:
        fp = _fingerprint(legacy)
        if fp in existing_fps:
            _LOGGER.info("Legacy entry %s seems already imported (fp=%s). Skipping.", legacy.entry_id, fp)
            continue

        new_entry = hass.config_entries.async_add(
            hass.config_entries.async_create_entry(
                domain=DOMAIN,
                title=legacy.title,
                data=dict(legacy.data),
                options=dict(legacy.options),
            )
        )

        _LOGGER.info("Imported legacy entry %s -> new entry %s", legacy.entry_id, new_entry.entry_id)

        await _async_retarget_entities(ent_reg, legacy.entry_id, new_entry.entry_id)

        await hass.config_entries.async_remove(legacy.entry_id)
        _LOGGER.warning("Removed legacy entry %s after import", legacy.entry_id)


async def _async_retarget_entities(ent_reg: er.EntityRegistry, old_entry_id: str, new_entry_id: str) -> None:
    """Keep entity_id/history by moving entities from old config_entry_id to new one."""
    updates = 0
    for entity_entry in list(ent_reg.entities.values()):
        if entity_entry.config_entry_id != old_entry_id:
            continue
        # Move only entities from the legacy component
        if entity_entry.platform != LEGACY_DOMAIN:
            continue

        ent_reg.async_update_entity(
            entity_entry.entity_id,
            platform=DOMAIN,
            config_entry_id=new_entry_id,
        )
        updates += 1

    if updates:
        _LOGGER.info("Retargeted %d entities from legacy entry %s -> %s", updates, old_entry_id, new_entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = ShipmentCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register the sensor platform, while managing entities manually.
    coordinator.add_entities_callback = None
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(
        coordinator.async_add_listener(
            lambda: hass.async_create_task(_update_entities(hass, entry, coordinator))
        )
    )
    
    return True

async def _update_entities(hass, entry, coordinator):
    """Check for new parcels and add sensors."""
    if not hasattr(coordinator, "known_parcels"):
        coordinator.known_parcels = set()
    
    new_entities = []
    current_data = coordinator.data or []
    current_ids = set()
    
    for parcel in current_data:
        pid = _get_parcel_id(parcel, coordinator.courier)
        
        if not pid:
            continue

        if _is_delivered(parcel, coordinator.courier):
            continue

        current_ids.add(pid)
        if pid not in coordinator.known_parcels:
            coordinator.known_parcels.add(pid)
            new_entities.append(ShipmentSensor(coordinator, parcel, coordinator.courier))
    
    if new_entities and coordinator.add_entities_callback:
        coordinator.add_entities_callback(new_entities)

    # Remove entities that are no longer present in the API response.
    current_unique_ids = {f"{coordinator.courier}_{pid}" for pid in current_ids}
    registry = er.async_get(hass)
    remove_entity_ids = []

    for entity_entry in registry.entities.values():
        if entity_entry.domain != "sensor":
            continue
        if entity_entry.platform != DOMAIN:
            continue
        if entity_entry.config_entry_id != entry.entry_id:
            continue
        if not entity_entry.unique_id:
            continue
        if entity_entry.unique_id not in current_unique_ids:
            remove_entity_ids.append(entity_entry.entity_id)

    if remove_entity_ids:
        for entity_id in remove_entity_ids:
            registry.async_remove(entity_id)

    # Keep in sync with the latest parcel list.
    coordinator.known_parcels.intersection_update(current_ids)

def _get_parcel_id(data, courier):
    if courier == "inpost": return data.get("shipmentNumber")
    if courier == "dpd": return data.get("waybill")
    if courier == "dhl": return data.get("shipmentNumber")
    if courier == "pocztex": return _pick_pocztex_id(data)
    return None

def _is_delivered(data, courier):
    status = ""
    if courier == "inpost":
        status = data.get("status") or ""
    elif courier == "dpd":
        status = (data.get("main_status") or {}).get("status") or ""
    elif courier == "dhl":
        status = data.get("status") or ""
    elif courier == "pocztex":
        status = _pick_pocztex_status(data) or ""

    status_norm = str(status).strip().lower()
    if not status_norm:
        return False

    delivered_markers = {
        "delivered",
        "delivered_to_pickup_point",
        "delivered_to_boxmachine",
        "delivered_to_address",
        "delivered_to_machine",
        "delivered_to_parcel_locker",
        "delivered_to_shop",
        "delivered_to_branch",
    }
    if status_norm in delivered_markers:
        return True

    if courier == "pocztex":
        return _normalize_status(status, courier) == "delivered"

    return "delivered" in status_norm

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not hass.data.get(DOMAIN):
            await JSModuleRegistration(hass).async_unregister()
    return unload_ok
