from pathlib import Path
import json
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_TRANSLATION_CACHE = {}
_SHARED_TRANSLATION_CACHE = {}
_TRANSLATION_DIRS = {}

_LABEL_TRANSLATIONS = {
    "parcel": {
        "pl": "Paczka",
        "en": "Parcel",
    },
    "active_shipments": {
        "pl": "Aktywne przesyłki",
        "en": "Active shipments",
    },
}

_STATUS_MAP = {
    "inpost": {
        "CREATED": "created",
        "CONFIRMED": "created",
        "OFFER_SELECTED": "created",
        "OFFERS_PREPARED": "created",
        "DISPATCHED_BY_SENDER": "in_transport",
        "DISPATCHED_BY_SENDER_TO_POK": "in_transport",
        "TAKEN_BY_COURIER": "in_transport",
        "TAKEN_BY_COURIER_FROM_POK": "in_transport",
        "COLLECTED_FROM_SENDER": "in_transport",
        "ADOPTED_AT_SOURCE_BRANCH": "in_transport",
        "ADOPTED_AT_SORTING_CENTER": "in_transport",
        "SENT_FROM_SOURCE_BRANCH": "in_transport",
        "SENT_FROM_SORTING_CENTER": "in_transport",
        "ADOPTED_AT_TARGET_BRANCH": "in_transport",
        "READDRESSED": "in_transport",
        "REDIRECT_TO_BOX": "in_transport",
        "PERMANENTLY_REDIRECTED_TO_BOX_MACHINE": "in_transport",
        "PERMANENTLY_REDIRECTED_TO_CUSTOMER_SERVICE_POINT": "in_transport",
        "UNSTACK_FROM_BOX_MACHINE": "in_transport",
        "AVIZO": "in_transport",
        "OUT_FOR_DELIVERY": "handed_out_for_delivery",
        "OUT_FOR_DELIVERY_TO_ADDRESS": "handed_out_for_delivery",
        "UNSTACK_FROM_CUSTOMER_SERVICE_POINT": "handed_out_for_delivery",
        "PICKUP_REMINDER_SENT_ADDRESS": "handed_out_for_delivery",
        "READY_TO_PICKUP": "waiting_for_pickup",
        "READY_FOR_COLLECTION": "waiting_for_pickup",
        "READY_TO_PICKUP_FROM_BRANCH": "waiting_for_pickup",
        "READY_TO_PICKUP_FROM_POK": "waiting_for_pickup",
        "READY_TO_PICKUP_FROM_POK_REGISTERED": "waiting_for_pickup",
        "PICKUP_REMINDER_SENT": "waiting_for_pickup",
        "STACK_IN_BOX_MACHINE": "waiting_for_pickup",
        "STACK_IN_CUSTOMER_SERVICE_POINT": "waiting_for_pickup",
        "AVIZO_COMPLETED": "waiting_for_pickup",
        "DELIVERED": "delivered",
        "COLLECTED_BY_CUSTOMER": "delivered",
        "RETURNED_TO_SENDER": "returned",
        "RETURN_PICKUP_CONFIRMATION_TO_SENDER": "returned",
        "NOT_COLLECTED": "returned",
        "PICKUP_TIME_EXPIRED": "returned",
        "STACK_PARCEL_PICKUP_TIME_EXPIRED": "returned",
        "STACK_PARCEL_IN_BOX_MACHINE_PICKUP_TIME_EXPIRED": "returned",
        "CANCELED": "cancelled",
        "CANCELLED": "cancelled",
        "CANCELED_REDIRECT_TO_BOX": "cancelled",
        "DELAY_IN_DELIVERY": "exception",
        "DELIVERY_ATTEMPT_FAILED": "exception",
        "UNDELIVERED": "exception",
        "UNDELIVERED_COD_CASH_RECEIVER": "exception",
        "UNDELIVERED_INCOMPLETE_ADDRESS": "exception",
        "UNDELIVERED_LACK_OF_ACCESS_LETTERBOX": "exception",
        "UNDELIVERED_NO_MAILBOX": "exception",
        "UNDELIVERED_NOT_LIVE_ADDRESS": "exception",
        "UNDELIVERED_UNKNOWN_RECEIVER": "exception",
        "UNDELIVERED_WRONG_ADDRESS": "exception",
        "REJECTED_BY_RECEIVER": "exception",
        "MISSING": "exception",
        "OVERSIZED": "exception",
        "CLAIMED": "exception",
        "COD_REJECTED": "exception",
        "C2X_REJECTED": "exception",
        "AVIZO_REJECTED": "exception",
        "COD_COMPLETED": "in_transport",
        "C2X_COMPLETED": "in_transport",
        "OTHER": "unknown",
    },
    "dpd": {
        "READY_TO_SEND": "created",
        "RECEIVED_FROM_SENDER": "in_transport",
        "SENT": "in_transport",
        "IN_TRANSPORT": "in_transport",
        "RECEIVED_IN_DEPOT": "in_transport",
        "REDIRECTED": "in_transport",
        "RESCHEDULED": "in_transport",
        "HANDED_OVER_FOR_DELIVERY": "handed_out_for_delivery",
        "READY_TO_PICK_UP": "waiting_for_pickup",
        "SELF_PICKUP": "waiting_for_pickup",
        "HARD_RESERVED": "waiting_for_pickup",
        "DELIVERED": "delivered",
        "PICKED_UP": "delivered",
        "RETURNED_TO_SENDER": "returned",
        "EXPIRED_PICKUP": "returned",
        "UNSUCCESSFUL_DELIVERY": "exception",
    },
    "dhl": {
        "NONE": "created",
        "SHIPMENTINPREPARATION": "created",
        "INPREPARATION": "created",
        "WAITINGFORCOURIERPICKUP": "created",
        "POSTED": "in_transport",
        "SENT": "in_transport",
        "POSTEDATPOINT": "in_transport",
        "PICKEDUPBYCOURIER": "in_transport",
        "ROUTE": "in_transport",
        "REDIRECTED": "in_transport",
        "REDIRECTEDTOPOINT": "in_transport",
        "DELIVERY": "handed_out_for_delivery",
        "FOR_DELIVERY": "handed_out_for_delivery",
        "DELIVERYTOPOINT": "handed_out_for_delivery",
        "DELIVERYTOLOCKER": "handed_out_for_delivery",
        "READY": "waiting_for_pickup",
        "DELIVEREDTOPOINT": "waiting_for_pickup",
        "DELIVEREDTOLOCKER": "waiting_for_pickup",
        "DELIVEREDTOPARCELLOCKER": "waiting_for_pickup",
        "DELIVEREDTOPICKUPPOINT": "waiting_for_pickup",
        "RETRIEVEDFROMPOINT": "delivered",
        "RETRIEVEDFROMLOCKER": "delivered",
        "DELIVERED": "delivered",
        "ROUTETOSENDER": "returned",
        "PARCELRETURNSTOSENDER": "returned",
        "PARCELRETURNEDTOSENDER": "returned",
        "RETURN": "returned",
        "RESIGNATED": "cancelled",
        "ERROR": "exception",
        "DELIVERYDELAY": "exception",
        "DELIVERYPROBLEM": "exception",
        "UNSUCCESSFULATTEMPTATDELIVERY": "exception",
        "SECONDUNSUCCESSFULATTEMPTATDELIVERY": "exception",
        "REFUSAL": "exception",
        "LOST": "exception",
        "DISPOSED": "exception",
    },
    "pocztex": {
        "PRZYGOTOWANA": "created",
        "NADANA": "in_transport",
        "W TRANSPORCIE": "in_transport",
        "W DORĘCZENIU": "handed_out_for_delivery",
        "W DORECZENIU": "handed_out_for_delivery",
        "AWIZOWANA": "waiting_for_pickup",
        "P_KWD": "waiting_for_pickup",
        "ODEBRANA W PUNKCIE": "delivered",
        "P_OWU": "delivered",
    },
}

_FINAL_STATUS_KEYS = {"delivered", "returned", "cancelled"}
ACTIVE_SHIPMENTS_OBJECT_ID = f"{DOMAIN}_active_shipments"
ACTIVE_SHIPMENTS_UNIQUE_ID = ACTIVE_SHIPMENTS_OBJECT_ID

_SHARED_STATUS_FALLBACK = {
    "pl": {
        "created": "Utworzona",
        "in_transport": "W transporcie",
        "handed_out_for_delivery": "Wydana do doręczenia",
        "waiting_for_pickup": "Gotowa do odbioru",
        "delivered": "Doręczona",
        "returned": "Zwrócona do nadawcy",
        "cancelled": "Anulowana",
        "exception": "Problem z doręczeniem",
        "unknown": "Nieznany status",
    },
    "en": {
        "created": "Created",
        "in_transport": "In transit",
        "handed_out_for_delivery": "Out for delivery",
        "waiting_for_pickup": "Ready for pickup",
        "delivered": "Delivered",
        "returned": "Returned to sender",
        "cancelled": "Cancelled",
        "exception": "Delivery issue",
        "unknown": "Unknown status",
    },
}


def _normalize_language(language):
    if not language:
        return "en"
    return str(language).replace("_", "-").split("-")[0].lower()


def _get_hass_language(hass):
    if not hass:
        return None
    lang = getattr(hass.config, "language", None)
    if lang:
        return lang
    locale = getattr(hass.config, "locale", None)
    if locale and getattr(locale, "language", None):
        return locale.language
    return None


def _translate_label(key, language):
    lang = _normalize_language(language)
    labels = _LABEL_TRANSLATIONS.get(key, {})
    return labels.get(lang) or labels.get("en") or key


def _get_translation_dirs(language):
    lang = _normalize_language(language)
    if lang in _TRANSLATION_DIRS:
        return _TRANSLATION_DIRS[lang]

    base = Path(__file__).resolve()
    root = base.parents[2] / "translations"
    candidates = []

    if lang == "pl":
        lang_dir = root / "pl"
        if lang_dir.exists():
            candidates.append(lang_dir)
        if root.exists():
            candidates.append(root)
    else:
        lang_dir = root / lang
        if lang_dir.exists():
            candidates.append(lang_dir)

    _TRANSLATION_DIRS[lang] = candidates
    return candidates


def _load_translation_map(filename, language):
    for base in _get_translation_dirs(language):
        path = base / filename
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return {str(key).upper(): str(value) for key, value in data.items()}
        except Exception as err:
            _LOGGER.warning("Failed to load translation file %s: %s", path, err)
            return {}
    return {}


def _get_shared_translations(language):
    lang = _normalize_language(language)
    if lang in _SHARED_TRANSLATION_CACHE:
        return _SHARED_TRANSLATION_CACHE[lang]

    shared = _load_translation_map("shared.json", lang)
    if not shared:
        fallback = _SHARED_STATUS_FALLBACK.get(lang, _SHARED_STATUS_FALLBACK["en"])
        shared = {key.upper(): value for key, value in fallback.items()}
    _SHARED_TRANSLATION_CACHE[lang] = shared
    return shared


def _get_courier_translations(courier, language):
    lang = _normalize_language(language)
    cache_key = (lang, courier)
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]
    translations = _load_translation_map(f"{courier}.json", lang)
    _TRANSLATION_CACHE[cache_key] = translations
    return translations


def _normalize_status(raw_status, courier):
    status_text = str(raw_status or "").strip()
    if not status_text:
        return "unknown"

    status_upper = status_text.upper()
    courier_map = _STATUS_MAP.get(courier, {})
    if status_upper in courier_map:
        return courier_map[status_upper]

    status_lower = status_text.lower()
    status_ascii = status_lower.translate(str.maketrans("ąćęłńóśżź", "acelnoszz"))
    if status_lower in {"ready"}:
        return "waiting_for_pickup"
    if (
        "delivered to locker" in status_lower
        or "delivered to point" in status_lower
        or "delivered to parcel locker" in status_lower
        or "delivered to pickup point" in status_lower
    ):
        return "waiting_for_pickup"
    if "picked up" in status_lower or "collected by" in status_lower or "collected" in status_lower:
        return "delivered"
    if "ready for collection" in status_lower or "ready to pick" in status_lower or "ready for pick" in status_lower:
        return "waiting_for_pickup"
    if "pickup" in status_lower or "collection" in status_lower or "locker" in status_lower:
        return "waiting_for_pickup"
    if "delivered" in status_lower:
        return "delivered"
    if "awizo" in status_ascii:
        return "waiting_for_pickup"
    if "odebr" in status_ascii or "wydan" in status_ascii or "odebrane" in status_ascii:
        return "delivered"
    if "dorecz" in status_ascii or "dostarcz" in status_ascii:
        return "delivered"
    if "zwrot" in status_ascii or "odesl" in status_ascii:
        return "returned"
    if "anul" in status_ascii or "rezygn" in status_ascii:
        return "cancelled"
    if "problem" in status_ascii or "niedorecz" in status_ascii or "odmow" in status_ascii:
        return "exception"
    if "out for delivery" in status_lower or "handed over for delivery" in status_lower:
        return "handed_out_for_delivery"
    if "return" in status_lower or "returned" in status_lower:
        return "returned"
    if "cancel" in status_lower or "canceled" in status_lower or "cancelled" in status_lower:
        return "cancelled"
    if (
        "fail" in status_lower
        or "failed" in status_lower
        or "delay" in status_lower
        or "exception" in status_lower
        or "undeliver" in status_lower
        or "missing" in status_lower
        or "rejected" in status_lower
    ):
        return "exception"
    if (
        "transit" in status_lower
        or "in transport" in status_lower
        or "departed" in status_lower
        or "arrived" in status_lower
        or "processed" in status_lower
        or "received" in status_lower
        or "adopted" in status_lower
    ):
        return "in_transport"
    if (
        "created" in status_lower
        or "pre-transit" in status_lower
        or "label" in status_lower
        or "confirmed" in status_lower
        or "info received" in status_lower
        or "ready to send" in status_lower
    ):
        return "created"

    return "unknown"

def _ensure_json_payload(payload):
    try:
        return json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError):
        return json.dumps(payload, ensure_ascii=False, default=str)

def _is_active_status(raw_status, courier):
    return _normalize_status(raw_status, courier) not in _FINAL_STATUS_KEYS

def _count_active_parcels(parcels, courier):
    if not parcels:
        return 0
    count = 0
    for parcel in parcels:
        raw_status = _get_raw_status(parcel, courier)
        if _is_active_status(raw_status, courier):
            count += 1
    return count

def get_active_shipments_unique_id():
    return ACTIVE_SHIPMENTS_UNIQUE_ID


def _translate_status(raw_status, courier, language):
    status_text = str(raw_status or "").strip()
    if not status_text:
        fallback = _SHARED_STATUS_FALLBACK.get(_normalize_language(language), _SHARED_STATUS_FALLBACK["en"])
        return _get_shared_translations(language).get("UNKNOWN", fallback["unknown"])

    courier_translations = _get_courier_translations(courier, language)
    translated = courier_translations.get(status_text.upper())
    if translated:
        return translated

    normalized = _normalize_status(status_text, courier)
    if courier == "pocztex" and normalized == "unknown":
        return status_text
    shared_translations = _get_shared_translations(language)
    return shared_translations.get(normalized.upper(), status_text)


def _get_raw_status(parcel_data, courier):
    if not parcel_data:
        return None
    if courier == "inpost":
        return parcel_data.get("status")
    if courier == "dpd":
        return (parcel_data.get("main_status") or {}).get("status")
    if courier == "dhl":
        return parcel_data.get("status")
    if courier == "pocztex":
        return _pick_pocztex_status(parcel_data)
    return None

def _pick_pocztex_id(parcel_data):
    if not parcel_data or not isinstance(parcel_data, dict):
        return None
    keys = [
        "trackingId",
        "trackingNumber",
        "trackingNo",
        "parcelNumber",
        "consignmentNumber",
        "shipmentNumber",
        "number",
        "id",
    ]
    for key in keys:
        if key in parcel_data and parcel_data[key] is not None:
            return str(parcel_data[key])
    return None

def _pick_pocztex_status(parcel_data):
    if not parcel_data or not isinstance(parcel_data, dict):
        return None
    status = parcel_data.get("status")
    if isinstance(status, str):
        return status
    state = parcel_data.get("state")
    if isinstance(state, str):
        return state
    state_code = parcel_data.get("stateCode")
    if state_code is not None:
        return str(state_code)
    if isinstance(status, dict):
        for key in ("name", "label", "description", "code"):
            if status.get(key) is not None:
                return str(status.get(key))
    for key in (
        "statusName",
        "statusText",
        "statusLabel",
        "statusDescription",
        "statusCode",
        "state",
        "stateCode",
    ):
        if parcel_data.get(key) is not None:
            return str(parcel_data.get(key))
    return None

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    coordinator.add_entities_callback = async_add_entities

    global_sensor = hass.data[DOMAIN].get("_active_shipments_sensor")
    if not global_sensor:
        global_sensor = ActiveShipmentsSensor(hass)
        hass.data[DOMAIN]["_active_shipments_sensor"] = global_sensor
        async_add_entities([global_sensor])
    global_sensor.attach_coordinator(coordinator)

    from .__init__ import _update_entities
    await _update_entities(hass, entry, coordinator)


class ShipmentSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, parcel_data, courier):
        super().__init__(coordinator)
        self.parcel_data = parcel_data
        self._courier = courier
        self._tracking_number = self._get_id(parcel_data)
        
        self._attr_unique_id = f"{courier}_{self._tracking_number}"
        self._attr_has_entity_name = True
        self._language = _normalize_language(_get_hass_language(coordinator.hass))
        self._attr_name = f"{_translate_label('parcel', self._language)} {self._tracking_number}"
        self._attr_icon = "mdi:package-variant-closed"

    def _get_id(self, data):
        if self._courier == "inpost": return data.get("shipmentNumber")
        if self._courier == "dpd": return data.get("waybill")
        if self._courier == "dhl": return data.get("shipmentNumber")
        if self._courier == "pocztex": return _pick_pocztex_id(data)
        return "unknown"

    def _get_language(self):
        hass_language = _get_hass_language(self.hass)
        if hass_language:
            return _normalize_language(hass_language)
        return self._language or "en"

    @property
    def native_value(self):
        raw_status = _get_raw_status(self.parcel_data, self._courier)
        return _translate_status(raw_status, self._courier, self._get_language())

    @property
    def extra_state_attributes(self):
        attrs = {
            "courier": self._courier,
            "tracking_number": self._tracking_number,
            "integration_domain": DOMAIN,
        }
        if isinstance(self.parcel_data, dict) and "_raw_response" in self.parcel_data:
            raw_payload = self.parcel_data.get("_raw_response")
        else:
            raw_payload = self.parcel_data
        attrs["raw_response"] = _ensure_json_payload(raw_payload)
        raw_status = _get_raw_status(self.parcel_data, self._courier)
        attrs["status_raw"] = raw_status
        attrs["status_key"] = _normalize_status(raw_status, self._courier)
        if self._courier == "inpost":
            attrs["sender"] = self.parcel_data.get("sender").get("name")
            pickup_point = self.parcel_data.get("pickUpPoint", {}) or {}
            address_details = pickup_point.get("addressDetails", {}) or {}
            street = address_details.get("street") or ""
            building = address_details.get("buildingNumber") or ""
            location_desc = pickup_point.get("locationDescription") or ""
            parts = [p for p in [street, building] if p]
            location = " ".join(parts)
            if location_desc:
                location = f"{location}, {location_desc}" if location else location_desc
            attrs["location"] = location
            attrs["open_code"] = self.parcel_data.get("openCode")
            attrs["phone_number"] = self.parcel_data.get("receiver", {}).get("phoneNumber", {}).get("value")
        elif self._courier == "dpd":
            attrs["sender"] = self.parcel_data.get("sender").get("name")
        elif self._courier == "pocztex":
            attrs["sender_name"] = self.parcel_data.get("senderName")
            attrs["recipient_name"] = self.parcel_data.get("recipientName")
            attrs["direction"] = self.parcel_data.get("direction")
            attrs["state_code"] = self.parcel_data.get("stateCode")
            attrs["state_date"] = self.parcel_data.get("stateDate")
            attrs["pickup_date"] = self.parcel_data.get("pickupDate")
            history = self.parcel_data.get("history")
            if isinstance(history, list):
                attrs["history"] = history
                if history:
                    last = history[-1]
                    if isinstance(last, dict):
                        attrs["history_last_state"] = last.get("state")
                        attrs["history_last_date"] = last.get("date")
        return attrs

    def _handle_coordinator_update(self) -> None:
        parcels = self.coordinator.data
        my_parcel = next((p for p in parcels if self._get_id(p) == self._tracking_number), None)
        
        if my_parcel:
            self.parcel_data = my_parcel
            self._attr_available = True
            self.async_write_ha_state()
        else:
            self._attr_available = False
            self.async_write_ha_state()


class ActiveShipmentsSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, hass):
        self._hass = hass
        self._coordinators = {}
        self._attr_unique_id = get_active_shipments_unique_id()
        self._attr_suggested_object_id = ACTIVE_SHIPMENTS_OBJECT_ID
        self._attr_has_entity_name = True
        self._language = _normalize_language(_get_hass_language(hass))
        self._attr_name = _translate_label("active_shipments", self._language)
        self._attr_icon = "mdi:package-variant"

    async def async_added_to_hass(self):
        await self._async_ensure_entity_id()
        for coordinator in self._iter_coordinators():
            self.attach_coordinator(coordinator)

    @property
    def native_value(self):
        total = 0
        for coordinator in self._iter_coordinators():
            total += _count_active_parcels(coordinator.data or [], coordinator.courier)
        return total

    def attach_coordinator(self, coordinator):
        if coordinator in self._coordinators:
            return
        remove_listener = coordinator.async_add_listener(self._handle_coordinator_update)
        self._coordinators[coordinator] = remove_listener
        self._handle_coordinator_update()

    def detach_coordinator(self, coordinator):
        remove_listener = self._coordinators.pop(coordinator, None)
        if remove_listener:
            remove_listener()
        self._handle_coordinator_update()

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    def _iter_coordinators(self):
        if self._coordinators:
            for coordinator in list(self._coordinators.keys()):
                yield coordinator
            return
        data = self._hass.data.get(DOMAIN, {})
        for coordinator in data.values():
            if not getattr(coordinator, "courier", None):
                continue
            if not hasattr(coordinator, "data"):
                continue
            yield coordinator

    async def _async_ensure_entity_id(self):
        if not self.hass:
            return
        try:
            from homeassistant.helpers import entity_registry as er
        except Exception:
            return
        registry = er.async_get(self.hass)
        current_entity_id = registry.async_get_entity_id(
            "sensor",
            DOMAIN,
            get_active_shipments_unique_id(),
        )
        if not current_entity_id:
            return
        desired_entity_id = f"sensor.{ACTIVE_SHIPMENTS_OBJECT_ID}"
        if current_entity_id == desired_entity_id:
            return
        if registry.async_get(desired_entity_id):
            return
        deleted = getattr(registry, "deleted_entities", None)
        if deleted and desired_entity_id in deleted:
            return
        try:
            registry.async_update_entity(current_entity_id, new_entity_id=desired_entity_id)
        except (ValueError, KeyError):
            return
