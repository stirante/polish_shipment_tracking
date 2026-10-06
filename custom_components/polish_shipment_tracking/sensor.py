"""Sensor platform for Polish Shipment Tracking."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INTEGRATION_VERSION, CONF_EMAIL, SIGNAL_ALLEGRO_ORDERS_UPDATED
from .button import _build_device_info
from .coordinator import ShipmentCoordinator
from .helpers import (
    get_shipment_entity_id,
    get_account_label,
    get_parcel_id,
    get_parcel_tracking_numbers,
    get_raw_status,
    is_delivered,
    normalize_status,
)
from .helpers import count_ready_for_pickup

_LOGGER = logging.getLogger(__name__)

ACTIVE_SHIPMENTS_UNIQUE_ID = f"{DOMAIN}_active_shipments"
READY_FOR_PICKUP_SHIPMENTS_UNIQUE_ID = f"{DOMAIN}_ready_for_pickup_shipments"
SHARED_SENSOR_KEYS = ("_active_shipments_sensor", "_ready_for_pickup_shipments_sensor")


def _account_ready_for_pickup_unique_id(entry: ConfigEntry) -> str:
    return f"{entry.entry_id}_ready_for_pickup"


@callback
def _set_shared_sensor_registry_owner(hass: HomeAssistant, entry_id: str) -> None:
    """Associate existing global sensor registry entries with their host."""
    registry = async_get_entity_registry(hass)
    for unique_id in (ACTIVE_SHIPMENTS_UNIQUE_ID, READY_FOR_PICKUP_SHIPMENTS_UNIQUE_ID):
        if entity_id := registry.async_get_entity_id("sensor", DOMAIN, unique_id):
            registry.async_update_entity(entity_id, config_entry_id=entry_id)


@callback
def _shared_sensor_host_unloaded(hass: HomeAssistant, entry_id: str) -> None:
    """Move shared sensors to a surviving entry when their owner unloads."""
    domain_data = hass.data[DOMAIN]
    hosts = domain_data["_shared_sensor_hosts"]
    hosts.pop(entry_id, None)
    if domain_data.get("_shared_sensor_owner") != entry_id:
        return

    old_sensors = [domain_data.pop(key) for key in SHARED_SENSOR_KEYS]
    domain_data.pop("_shared_sensor_owner", None)
    for sensor in old_sensors:
        sensor.release_coordinators()

    if not hosts:
        domain_data.pop("_shared_sensor_hosts", None)
        return

    new_owner, (_, add_entities) = next(iter(hosts.items()))
    replacement = (ActiveShipmentsSensor(hass), ReadyForPickupShipmentsSensor(hass))
    for key, sensor in zip(SHARED_SENSOR_KEYS, replacement):
        domain_data[key] = sensor
        for coordinator, _ in hosts.values():
            sensor.attach_coordinator(coordinator)

    # Registry ownership must follow the platform that now provides the entity.
    _set_shared_sensor_registry_owner(hass, new_owner)
    domain_data["_shared_sensor_owner"] = new_owner
    add_entities(list(replacement))


@callback
def _detach_shared_sensor(domain_data: dict, key: str, coordinator: ShipmentCoordinator) -> None:
    """Detach from the current shared entity, if one is still registered."""
    if sensor := domain_data.get(key):
        sensor.detach_coordinator(coordinator)

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
    domain_data = hass.data[DOMAIN]
    domain_data.setdefault("_shared_sensor_hosts", {})[entry.entry_id] = (
        coordinator, async_add_entities
    )

    # Shared count sensors aggregate all configured couriers and accounts.
    global_entities = []
    if "_shared_sensor_owner" not in domain_data:
        global_sensor = ActiveShipmentsSensor(hass)
        domain_data["_active_shipments_sensor"] = global_sensor
        global_entities.append(global_sensor)
        ready_global_sensor = ReadyForPickupShipmentsSensor(hass)
        domain_data["_ready_for_pickup_shipments_sensor"] = ready_global_sensor
        global_entities.append(ready_global_sensor)
        domain_data["_shared_sensor_owner"] = entry.entry_id
        _set_shared_sensor_registry_owner(hass, entry.entry_id)
    global_entities.append(ReadyForPickupAccountSensor(coordinator))
    async_add_entities(global_entities)

    for key in SHARED_SENSOR_KEYS:
        global_sensor = domain_data[key]
        global_sensor.attach_coordinator(coordinator)
        entry.async_on_unload(
            lambda key=key: _detach_shared_sensor(domain_data, key, coordinator)
        )
    entry.async_on_unload(lambda: _shared_sensor_host_unloaded(hass, entry.entry_id))

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

    has_initialized = False

    @callback
    def async_update_parcels() -> None:
        """Add new sensors and remove old ones."""
        nonlocal has_initialized
        current_data = coordinator.data or []
        _LOGGER.debug(
            "async_update_parcels [%s]: coordinator.data has %d items, known_parcels=%s",
            coordinator.courier,
            len(current_data),
            coordinator.known_parcels,
        )
        new_entities = []
        registry = async_get_entity_registry(hass)

        # Terminal parcels have already been filtered out of coordinator.data.
        # Publish their transitions while the old entity ID still exists.
        pending_events = coordinator.pending_lifecycle_events
        coordinator.pending_lifecycle_events = []
        for event_name, event_data in pending_events:
            parcel_id = event_data["shipment_id"]
            entity_id = get_shipment_entity_id(
                registry, DOMAIN, coordinator.courier, entry.entry_id, parcel_id
            )
            _queue_or_fire_event(
                hass,
                f"{DOMAIN}_{event_name}",
                {**event_data, "entity_id": entity_id},
            )
        
        current_ids = set()
        for parcel in current_data:
            pid = get_parcel_id(parcel, coordinator.courier)
            delivered = is_delivered(parcel, coordinator.courier)
            _LOGGER.debug(
                "async_update_parcels [%s]: parcel pid=%s delivered=%s",
                coordinator.courier,
                pid,
                delivered,
            )
            if not pid or delivered:
                continue
            
            current_ids.add(pid)
            if pid not in coordinator.known_parcels:
                unique_id = f"{coordinator.courier}_{pid}"
                existing_entity_id = registry.async_get_entity_id("sensor", DOMAIN, unique_id)
                if existing_entity_id is not None:
                    existing_entry = registry.async_get(existing_entity_id)
                    if existing_entry and existing_entry.config_entry_id == entry.entry_id:
                        # Entity belongs to this config entry - still create runtime entity.
                        coordinator.known_parcels.add(pid)
                        new_entities.append(ShipmentSensor(coordinator, parcel, pid))
                        continue
                    _LOGGER.debug(
                        "Skipping duplicate shipment entity for %s (already exists as %s)",
                        unique_id,
                        existing_entity_id,
                    )
                    continue
                coordinator.known_parcels.add(pid)
                new_entities.append(ShipmentSensor(coordinator, parcel, pid))
        
        if new_entities:
            async_add_entities(new_entities)
            # Fire events for newly detected shipments.
            # If HA isn't running yet, queue and flush after startup.
            if has_initialized:
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
        has_initialized = True

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
    current_unique_ids.update({
        ACTIVE_SHIPMENTS_UNIQUE_ID,
        READY_FOR_PICKUP_SHIPMENTS_UNIQUE_ID,
        _account_ready_for_pickup_unique_id(entry),
    })

    entities_to_remove = []
    for entity_entry in registry.entities.values():
        if (
            entity_entry.platform == DOMAIN
            and entity_entry.config_entry_id == entry.entry_id
            # Buttons have their own lifecycle in button.py; their unique_ids
            # never match sensor ones, so they would be removed every cycle.
            and entity_entry.domain == "sensor"
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
        if self._courier == "allegro":
            # Order ids are long UUIDs; the first item title says far more.
            offers = parcel_data.get("offers") or []
            title = (offers[0].get("title") if offers and isinstance(offers[0], dict) else None) or tracking_number
            self._attr_name = str(title)[:60]
        self._attr_unique_id = f"{self._courier}_{tracking_number}"
        self._attr_translation_key = "shipment_status"
        self.parcel_data = parcel_data

        account_id = get_account_label(coordinator.entry.data)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"{self._courier.title()} ({account_id})" if account_id else self._courier.title(),
            manufacturer="Polish Shipment Tracking",
            model=self._courier.title(),
            sw_version=INTEGRATION_VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Also refresh when Allegro learns which order this parcel belongs to."""
        await super().async_added_to_hass()
        if self._courier != "allegro":
            self.async_on_remove(
                async_dispatcher_connect(
                    self.hass, SIGNAL_ALLEGRO_ORDERS_UPDATED, self.async_write_ha_state
                )
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
            "account_contact": self._get_account_contact(),
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
        elif self._courier == "dhl":
            self._add_dhl_attributes(attrs)
        elif self._courier == "pocztex":
            self._add_pocztex_attributes(attrs)
        elif self._courier == "gls":
            self._add_gls_attributes(attrs)
        elif self._courier == "allegro":
            self._add_allegro_attributes(attrs)

        if self._courier != "allegro":
            self._add_allegro_order_attributes(attrs)

        return attrs

    def _get_account_contact(self) -> str | None:
        """Return the integration account identifier shown to the carrier."""
        entry_data = self.coordinator.entry.data
        if self._courier == "pocztex":
            return entry_data.get(CONF_EMAIL)
        # get_account_label drops Allegro's generated "client:<id>" login.
        return get_account_label(entry_data)

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

        # When the parcel is delivered to a pickup point (PUDO), expose the
        # point details so they show up in the list and dialog like InPost.
        point = None
        delivery = self.parcel_data.get("delivery")
        if isinstance(delivery, dict) and isinstance(delivery.get("point"), dict):
            point = delivery["point"]
        elif isinstance(self.parcel_data.get("delivery_point"), dict):
            point = self.parcel_data["delivery_point"]

        if isinstance(point, dict):
            address = point.get("address") or {}
            parts = [
                point.get("name"),
                address.get("address"),
                address.get("postal_code"),
                address.get("city"),
            ]
            location = ", ".join(str(part) for part in parts if part)
            if location:
                attrs["location"] = location
            if point.get("pudo_type_group"):
                attrs["parcel_shop_type"] = point.get("pudo_type_group")

        # Pickup PIN shown when the parcel is ready for collection at a PUDO.
        pin = self.parcel_data.get("pick_up_pin")
        if not pin and isinstance(delivery, dict):
            pin = delivery.get("pick_up_pin")
        if pin:
            attrs["pickup_code"] = pin

    def _add_dhl_attributes(self, attrs: dict) -> None:
        """Add DHL specific attributes."""
        data = self.parcel_data

        # sender/receiver are plain strings on both the list and details payload.
        sender = data.get("sender")
        if isinstance(sender, dict):
            sender = sender.get("name")
        if sender:
            attrs["sender"] = sender

        courier_info = data.get("courierDeliveryShipmentInfo")
        if not isinstance(courier_info, dict):
            courier_info = {}

        # "receiver" stays null for incoming parcels; the real name sits in the
        # courier delivery block.
        receiver = data.get("receiver") or courier_info.get("name")
        if receiver:
            attrs["recipient_name"] = receiver

        if data.get("customTitle"):
            attrs["custom_title"] = data["customTitle"]
        if data.get("packageType"):
            attrs["package_type"] = data["packageType"]
        if data.get("parcelExpirationDate"):
            attrs["expiration_date"] = data["parcelExpirationDate"]
        if data.get("timelineStep"):
            attrs["timeline_step"] = data["timelineStep"]
        if data.get("step"):
            attrs["current_step"] = data["step"]
        if data.get("description"):
            attrs["current_step_description"] = data["description"]

        # PIN doubles as the code shown at lockers and DHL POP points, but it is
        # only worth showing once it is actually needed - DHL returns it from
        # the moment the shipment is registered.
        pin = data.get("pin") or data.get("qrCode")
        if pin and attrs.get("status_key") in {"handed_out_for_delivery", "waiting_for_pickup"}:
            attrs["pickup_code"] = str(pin)

        for attr_name, key in (
            ("posting_date", "dateOfPostingUtc"),
            ("delivery_date", "deliveryDateUtc"),
            ("receipt_date", "receiptDateUtc"),
            ("planned_delivery_date", "planOfDeliveryFromUtc"),
            ("planned_delivery_date_to", "planOfDeliveryToUtc"),
            ("delivery_up_to", "deliveryUpToUtc"),
        ):
            if data.get(key):
                attrs[attr_name] = data[key]

        # Before the parcel ships the only date hint is menuTimelineLabel, and
        # even that stays null until the sender hands the parcel over.
        timeline = data.get("menuTimelineLabel")
        if isinstance(timeline, dict):
            if not attrs.get("planned_delivery_date") and timeline.get("dateUtc"):
                attrs["planned_delivery_date"] = timeline["dateUtc"]
            if not attrs.get("planned_delivery_date_to") and timeline.get("dateToUtc"):
                attrs["planned_delivery_date_to"] = timeline["dateToUtc"]
            if timeline.get("status"):
                attrs["timeline_status"] = timeline["status"]

        # Only a real collection point belongs under "location"; a courier
        # delivery address is the home address and gets its own attribute so it
        # never shows up as a pickup point (or in the list view).
        point = self._pick_dhl_point(data)
        if point:
            attrs["location"] = point
        else:
            delivery_address = self._pick_dhl_delivery_address(courier_info)
            if delivery_address:
                attrs["delivery_address"] = delivery_address

        cod = data.get("cod")
        if isinstance(cod, dict):
            if cod.get("packagePaymentStatus"):
                attrs["cod_payment_status"] = cod["packagePaymentStatus"]
            if cod.get("paymentValue"):
                attrs["cod_amount"] = cod["paymentValue"]
            if cod.get("currency"):
                attrs["cod_currency"] = cod["currency"]

    @staticmethod
    def _pick_dhl_point(data: dict) -> str | None:
        """Return the locker or DHL POP point address, when the parcel goes there."""
        for key in ("lockerInfo", "dhlPointInfo"):
            info = data.get(key)
            if not isinstance(info, dict):
                continue
            street = " ".join(
                str(part)
                for part in (info.get("street"), info.get("houseNumber") or info.get("streetNumber"))
                if part
            ).strip()
            parts = [info.get("name"), street or None, info.get("zipCode"), info.get("city")]
            address = ", ".join(str(part) for part in parts if part)
            if address:
                return address
        return None

    @staticmethod
    def _pick_dhl_delivery_address(courier_info: dict) -> str | None:
        """Return the courier delivery address."""
        street = " ".join(
            str(part) for part in (courier_info.get("street"), courier_info.get("streetNumber")) if part
        ).strip()
        parts = [street or None, courier_info.get("city")]
        return ", ".join(str(part) for part in parts if part) or None

    def _add_allegro_attributes(self, attrs: dict) -> None:
        """Add Allegro order attributes."""
        data = self.parcel_data
        _set_allegro_order_attrs(attrs, data, prefix="")
        if data.get("seller"):
            attrs["sender"] = data["seller"]
        if data.get("statusLabel"):
            attrs["status_label"] = data["statusLabel"]
        if data.get("deliveryName"):
            attrs["delivery_method"] = data["deliveryName"]
        if data.get("pickupCode"):
            attrs["pickup_code"] = data["pickupCode"]
        if data.get("deliveryEstimate"):
            attrs["delivery_estimate"] = data["deliveryEstimate"]
        if data.get("timeline"):
            attrs["timeline"] = data["timeline"]
        if data.get("pickupPointLocation"):
            attrs["pickup_point_location"] = data["pickupPointLocation"]
        if data.get("pickupPointHours"):
            attrs["pickup_point_hours"] = data["pickupPointHours"]
        recipient = data.get("recipient")
        if isinstance(recipient, dict) and recipient.get("name"):
            attrs["recipient_name"] = recipient["name"]

        waybills = [w for w in data.get("waybills") or [] if isinstance(w, dict)]
        if waybills:
            attrs["waybill"] = waybills[0].get("number")
            attrs["carrier"] = waybills[0].get("carrier_name") or waybills[0].get("carrier_id")
            attrs["tracking_url"] = waybills[0].get("url")
            attrs["waybills"] = waybills

        point = data.get("pickupPoint")
        if isinstance(point, dict):
            address = point.get("address") if isinstance(point.get("address"), dict) else {}
            parts = [point.get("name"), address.get("street"), address.get("code"), address.get("city")]
            location = ", ".join(str(part) for part in parts if part)
            if location:
                attrs["location"] = location

    def _add_allegro_order_attributes(self, attrs: dict) -> None:
        """Show what was bought when an Allegro order ships with this parcel."""
        numbers = get_parcel_tracking_numbers(self.parcel_data, self._courier)
        if not numbers:
            return
        for coordinator in self.coordinator.hass.data.get(DOMAIN, {}).values():
            if not isinstance(coordinator, ShipmentCoordinator) or coordinator.courier != "allegro":
                continue
            for order in coordinator.allegro_orders:
                if get_parcel_tracking_numbers(order, "allegro") & numbers:
                    _set_allegro_order_attrs(attrs, order, prefix="allegro_")
                    return

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

    def _add_gls_attributes(self, attrs: dict) -> None:
        """Add GLS specific attributes."""
        data = self.parcel_data
        tracking_shipment = data.get("trackingShipment")
        if isinstance(tracking_shipment, dict):
            data = tracking_shipment

        attrs["tracking_uid"] = data.get("trackingUid")
        attrs["shipment_no"] = data.get("shipmentNo")
        attrs["tracking_id"] = data.get("trackingId")
        attrs["state_date"] = data.get("stateDate")
        attrs["package_amount"] = data.get("packageAmount")
        attrs["weight"] = data.get("weight")
        attrs["pin"] = data.get("pin")
        attrs["reference"] = data.get("reference")
        attrs["courier_phone_number"] = data.get("courierPhoneNumber")
        attrs["delivery_method"] = data.get("deliveryMethod")
        attrs["payment_flag"] = data.get("paymentFlag")
        attrs["delivery_flag"] = data.get("deliveryFlag")

        sender = data.get("sender")
        if isinstance(sender, dict):
            attrs["sender_name"] = sender.get("shipmentName")
        elif data.get("senderName") is not None:
            attrs["sender_name"] = data.get("senderName")

        receiver = data.get("receiver")
        if isinstance(receiver, dict):
            attrs["receiver_name"] = receiver.get("shipmentName")
        elif data.get("receiverName") is not None:
            attrs["receiver_name"] = data.get("receiverName")

        parcel_shop = data.get("parcelShop")
        if isinstance(parcel_shop, dict):
            attrs["parcel_shop_name"] = parcel_shop.get("shipmentName")
            attrs["parcel_shop_type"] = parcel_shop.get("parcelShopType")
            address = [
                parcel_shop.get("street"),
                parcel_shop.get("postalCode"),
                parcel_shop.get("city"),
            ]
            attrs["location"] = ", ".join(str(part) for part in address if part)
        elif data.get("parcelShopType") is not None:
            attrs["parcel_shop_type"] = data.get("parcelShopType")

        packages = self.parcel_data.get("trackingShipmentPackages") or data.get("shipmentPackages")
        if isinstance(packages, list):
            attrs["packages"] = packages
            attrs["package_count"] = len(packages)
            history = []
            for pkg in packages:
                if isinstance(pkg, dict):
                    statuses = pkg.get("packageStatuses")
                    if isinstance(statuses, list):
                        history.extend(statuses)
            if history:
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

def _set_allegro_order_attrs(attrs: dict, order: dict, prefix: str) -> None:
    """Order details shared by Allegro sensors and carrier parcels they link to."""
    attrs[f"{prefix}order_id"] = order.get("orderId")
    attrs[f"{prefix}order_date"] = order.get("orderDate")
    attrs[f"{prefix}seller"] = order.get("seller")
    attrs[f"{prefix}items"] = [
        offer.get("title") for offer in order.get("offers") or [] if isinstance(offer, dict) and offer.get("title")
    ]
    attrs[f"{prefix}offers"] = [offer for offer in order.get("offers") or [] if isinstance(offer, dict)]
    total = order.get("totalCost")
    if isinstance(total, dict) and total.get("amount"):
        attrs[f"{prefix}total_cost"] = total.get("amount")
        attrs[f"{prefix}currency"] = total.get("currency")
    images = [
        offer.get("image_url") for offer in order.get("offers") or [] if isinstance(offer, dict) and offer.get("image_url")
    ]
    if images:
        attrs[f"{prefix}image_url"] = images[0]


class ActiveShipmentsSensor(SensorEntity):
    """Sensor that counts active shipments across all accounts."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_icon = "mdi:package-variant"
    _attr_state_class = SensorStateClass.MEASUREMENT
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
            if self._coordinators:
                self.async_write_ha_state()

    def release_coordinators(self) -> None:
        """Stop listeners when this platform's shared entity is removed."""
        for unregister in self._coordinators.values():
            unregister()
        self._coordinators.clear()

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


class ReadyForPickupShipmentsSensor(ActiveShipmentsSensor):
    """Count ready parcels across all configured accounts and couriers."""

    _attr_icon = "mdi:package-variant"
    _attr_translation_key = "ready_for_pickup_shipments"
    _attr_unique_id = READY_FOR_PICKUP_SHIPMENTS_UNIQUE_ID
    _attr_suggested_object_id = f"{DOMAIN}_ready_for_pickup_shipments"

    @property
    def native_value(self) -> int:
        return sum(
            count_ready_for_pickup(coordinator.data or [], coordinator.courier)
            for coordinator in self._coordinators
        )


class ReadyForPickupAccountSensor(CoordinatorEntity[ShipmentCoordinator], SensorEntity):
    """Count ready parcels for one courier account/config entry."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:package-variant"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "ready_for_pickup_account"

    def __init__(self, coordinator: ShipmentCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = _account_ready_for_pickup_unique_id(coordinator.entry)
        self._attr_device_info = _build_device_info(coordinator)

    @property
    def native_value(self) -> int:
        return count_ready_for_pickup(self.coordinator.data or [], self.coordinator.courier)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose account identity without marking the count as a parcel."""
        return {
            "courier": self.coordinator.courier,
            "account_contact": get_account_label(self.coordinator.entry.data),
        }
