from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN
from .sensor import _get_raw_status, _normalize_status

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Tworzymy tylko jedną encję dla całej integracji
    if "binary_sensor_entity" not in hass.data[DOMAIN]:
        entity = AnyShipmentsBinarySensor(hass)
        hass.data[DOMAIN]["binary_sensor_entity"] = entity
        async_add_entities([entity])
    
    entity = hass.data[DOMAIN]["binary_sensor_entity"]
    entity.add_coordinator(coordinator)

class AnyShipmentsBinarySensor(BinarySensorEntity):
    """Binary sensor to track if there are any shipments out for delivery or ready for pickup."""

    def __init__(self, hass):
        self._hass = hass
        self._coordinators = []
        self._attr_name = "Any Shipments"
        self._attr_unique_id = f"{DOMAIN}_any_shipments"
        self.entity_id = "binary_sensor.any_shipments"
        self._attr_icon = "mdi:package-variant"

    def add_coordinator(self, coordinator):
        if coordinator not in self._coordinators:
            self._coordinators.append(coordinator)
            if self.hass:
                self.async_on_remove(coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def is_on(self):
        """True if any shipment is out for delivery or waiting for pickup."""
        for coordinator in self._coordinators:
            if not coordinator.data:
                continue
            for parcel in coordinator.data:
                raw_status = _get_raw_status(parcel, coordinator.courier)
                status_key = _normalize_status(raw_status, coordinator.courier)
                if status_key in ["handed_out_for_delivery", "waiting_for_pickup"]:
                    return True
        return False

    @property
    def extra_state_attributes(self):
        """Dodatkowy atrybut z liczbą paczek."""
        count = 0
        for coordinator in self._coordinators:
            if not coordinator.data:
                continue
            for parcel in coordinator.data:
                raw_status = _get_raw_status(parcel, coordinator.courier)
                status_key = _normalize_status(raw_status, coordinator.courier)
                if status_key in ["handed_out_for_delivery", "waiting_for_pickup"]:
                    count += 1
        return {"shipment_count": count}