"""Sensor platform for Polish Shipment Tracking."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INTEGRATION_VERSION, CONF_PHONE, CONF_EMAIL
from .coordinator import ShipmentCoordinator
from .helpers import (
    get_parcel_id,
    get_raw_status,
    is_delivered,
    normalize_status,
)

_LOGGER = logging.getLogger(__name__)

ACTIVE_SHIPMENTS_UNIQUE_ID = f"{DOMAIN}_active_shipments"

@callback
def _ensure_pending_events_listener(hass: HomeAssistant) -> None:
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("_pending_events_listener"):
        return

    domain_data["_pending_events_listener"] = True

    @callback
    def _flush_pending_events(_: Any) -> None:
        pending = domain_data.pop("_pending_events", [])
        domain_data.pop("_pending_events_listener", None)
        for event_type, event_data in pending:
            hass.bus.async_fire(event_type, event_data)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _flush_pending_events)

@callback
def _queue_or_fire_event(hass: HomeAssistant, event_type: str, event_data: dict[str, Any]) -> None:
    if hass.is_running:
        hass.bus.async_fire(event_type, event_data)
        return

    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data.setdefault("_pending_events", []).append((event_type, event_data))
    _ensure_pending_events_listener(hass)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the sensor platform."""
    coordinator: ShipmentCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Handle global active shipments sensor
    if "_active_shipments_sensor" not in hass.data[DOMAIN]:
        global_sensor = ActiveShipmentsSensor(hass)
        hass.data[DOMAIN]["_active_shipments_sensor"] = global_sensor
        async_add_entities([global_sensor])
    
    global_sensor = hass.data[DOMAIN]["_active_shipments_sensor"]
    global_sensor.attach_coordinator(coordinator)
    entry.async_on_unload(lambda: global_sensor.detach_coordinator(coordinator))

    @callback
    def _build_new_shipment_event_data(sensor: "ShipmentSensor") -> dict[str, Any]:
        raw_status = get_raw_status(sensor.parcel_data, coordinator.courier)
        return {
            "courier": coordinator.courier,
            "shipment_id": sensor._tracking_number,
            "entity_id": getattr(sensor, "entity_id", None),
            "status_raw": raw_status,
            "status_key": normalize_status(raw_status, coordinator.courier),
        }


    @callback
    def async_update_parcels() -> None:
        """Add new sensors and remove old ones."""
        current_data = coordinator.data or []
        new_entities = []
        
        current_ids = set()
        for parcel in current_data:
            pid = get_parcel_id(parcel, coordinator.courier)
            if not pid or is_delivered(parcel, coordinator.courier):
                continue
            
            current_ids.add(pid)
            if pid not in coordinator.known_parcels:
                coordinator.known_parcels.add(pid)
                new_entities.append(ShipmentSensor(coordinator, parcel, pid))
        
        if new_entities:
            async_add_entities(new_entities)
            # Fire events for newly detected shipments.
            # If HA isn't running yet, queue and flush after startup.
            for new_sensor in new_entities:
                _queue_or_fire_event(
                    hass,
                    f"{DOMAIN}_new_shipment",
                    _build_new_shipment_event_data(new_sensor),
                )

        # Remove entities that are no longer present
        _async_remove_old_entities(hass, entry, coordinator, current_ids)
        
        # Keep track of active parcels for this coordinator
        coordinator.known_parcels.intersection_update(current_ids)

    entry.async_on_unload(coordinator.async_add_listener(async_update_parcels))
    async_update_parcels()

def _async_remove_old_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: ShipmentCoordinator,
    current_ids: set[str],
) -> None:
    """Remove entities that are no longer in the active parcels list."""
    registry = async_get_entity_registry(hass)
    current_unique_ids = {f"{coordinator.courier}_{pid}" for pid in current_ids}
    
    entities_to_remove = []
    for entity_entry in registry.entities.values():
        if (
            entity_entry.platform == DOMAIN
            and entity_entry.config_entry_id == entry.entry_id
            and entity_entry.unique_id != ACTIVE_SHIPMENTS_UNIQUE_ID
            and entity_entry.unique_id not in current_unique_ids
        ):
            entities_to_remove.append(entity_entry.entity_id)
            
    for entity_id in entities_to_remove:
        registry.async_remove(entity_id)

class ShipmentSensor(CoordinatorEntity[ShipmentCoordinator], SensorEntity):
    """Sensor for a single shipment."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:package-variant-closed"

    def __init__(
        self,
        coordinator: ShipmentCoordinator,
        parcel_data: dict,
        tracking_number: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._tracking_number = tracking_number
        self._courier = coordinator.courier
        
        # User requested including courier name in the entity name
        # We also add "Parcel" (Paczka) as in the example
        parcel_word = "Paczka" if coordinator.hass.config.language == "pl" else "Parcel"
        self._attr_name = f"{self._courier.title()} {parcel_word} {tracking_number}"
        self._attr_unique_id = f"{self._courier}_{tracking_number}"
        self._attr_translation_key = "shipment_status"
        self.parcel_data = parcel_data

        account_id = coordinator.entry.data.get(CONF_PHONE) or coordinator.entry.data.get(CONF_EMAIL)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"{self._courier.title()} ({account_id})",
            manufacturer="Polish Shipment Tracking",
            model=self._courier.title(),
            sw_version=INTEGRATION_VERSION,
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        raw_status = get_raw_status(self.parcel_data, self._courier)
        return normalize_status(raw_status, self._courier)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {
            "courier": self._courier,
            "tracking_number": self._tracking_number,
            "integration_domain": DOMAIN,
        }
        
        raw_status = get_raw_status(self.parcel_data, self._courier)
        attrs["status_raw"] = raw_status
        attrs["status_key"] = normalize_status(raw_status, self._courier)
        
        # Include raw response for the custom card
        if "_raw_response" in self.parcel_data:
            attrs["raw_response"] = json.dumps(self.parcel_data["_raw_response"], ensure_ascii=False)
        else:
            attrs["raw_response"] = json.dumps(self.parcel_data, ensure_ascii=False)
            
        # Add courier specific attributes
        if self._courier == "inpost":
            self._add_inpost_attributes(attrs)
        elif self._courier == "dpd":
            self._add_dpd_attributes(attrs)
        elif self._courier == "pocztex":
            self._add_pocztex_attributes(attrs)
            
        return attrs

    def _add_inpost_attributes(self, attrs: dict) -> None:
        """Add InPost specific attributes."""
        sender = self.parcel_data.get("sender")
        if isinstance(sender, dict):
            attrs["sender"] = sender.get("name")
            
        pickup_point = self.parcel_data.get("pickUpPoint")
        if isinstance(pickup_point, dict):
            address = pickup_point.get("addressDetails") or {}
            street = address.get("street") or ""
            building = address.get("buildingNumber") or ""
            city = address.get("city") or ""
            parts = [p for p in [street, building, city] if p]
            attrs["location"] = ", ".join(parts)
            
        attrs["open_code"] = self.parcel_data.get("openCode")
        
        receiver = self.parcel_data.get("receiver")
        if isinstance(receiver, dict):
            phone = receiver.get("phoneNumber")
            if isinstance(phone, dict):
                attrs["phone_number"] = phone.get("value")

    def _add_dpd_attributes(self, attrs: dict) -> None:
        """Add DPD specific attributes."""
        sender = self.parcel_data.get("sender")
        if isinstance(sender, dict):
            attrs["sender"] = sender.get("name")

    def _add_pocztex_attributes(self, attrs: dict) -> None:
        """Add Pocztex specific attributes."""
        attrs["sender_name"] = self.parcel_data.get("senderName")
        attrs["recipient_name"] = self.parcel_data.get("recipientName")
        attrs["state_date"] = self.parcel_data.get("stateDate")
        attrs["direction"] = self.parcel_data.get("direction")
        attrs["pickup_date"] = self.parcel_data.get("pickupDate")
        history = self.parcel_data.get("history")
        if isinstance(history, list):
            attrs["history"] = history

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Find our parcel in the new data
        current_data = self.coordinator.data or []
        my_parcel = next(
            (p for p in current_data if get_parcel_id(p, self._courier) == self._tracking_number),
            None
        )
        
        if my_parcel:
            old_raw_status = get_raw_status(self.parcel_data, self._courier)
            old_status_key = normalize_status(old_raw_status, self._courier)

            new_raw_status = get_raw_status(my_parcel, self._courier)
            new_status_key = normalize_status(new_raw_status, self._courier)

            if old_status_key != new_status_key:
                event_data = {
                    "courier": self._courier,
                    "shipment_id": self._tracking_number,
                    "entity_id": getattr(self, "entity_id", None),
                    "old_status_raw": old_raw_status,
                    "old_status_key": old_status_key,
                    "new_status_raw": new_raw_status,
                    "new_status_key": new_status_key,
                }
                _queue_or_fire_event(
                    self.coordinator.hass,
                    f"{DOMAIN}_shipment_status_changed",
                    event_data,
                )
            self.parcel_data = my_parcel
            self.async_write_ha_state()
        else:
            # If not found, it might be delivered or removed. 
            # The async_update_parcels listener will handle removal.
            pass

class ActiveShipmentsSensor(SensorEntity):
    """Sensor that counts active shipments across all accounts."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_icon = "mdi:package-variant"
    _attr_translation_key = "active_shipments"
    _attr_unique_id = ACTIVE_SHIPMENTS_UNIQUE_ID
    _attr_suggested_object_id = f"{DOMAIN}_active_shipments"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._coordinators: dict[ShipmentCoordinator, Any] = {}

    def attach_coordinator(self, coordinator: ShipmentCoordinator) -> None:
        """Attach a coordinator to this sensor."""
        if coordinator not in self._coordinators:
            self._coordinators[coordinator] = coordinator.async_add_listener(
                self.async_write_ha_state
            )

    def detach_coordinator(self, coordinator: ShipmentCoordinator) -> None:
        """Detach a coordinator from this sensor."""
        if coordinator in self._coordinators:
            unregister = self._coordinators.pop(coordinator)
            unregister()
            self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return the total count of active shipments."""
        total = 0
        for coordinator in self._coordinators:
            data = coordinator.data or []
            for parcel in data:
                if not is_delivered(parcel, coordinator.courier):
                    total += 1
        return total
