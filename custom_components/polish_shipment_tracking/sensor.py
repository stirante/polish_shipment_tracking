import json
import logging
from pathlib import Path

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_TRANSLATION_CACHE = {}
_SHARED_TRANSLATION_CACHE = {}
_TRANSLATION_DIRS = {}

_LABEL_TRANSLATIONS = {
    "parcel": {"pl": "Paczka", "en": "Parcel"}
}

_STATUS_MAP = {
    "inpost": {
        "CREATED": "created", "CONFIRMED": "created", "OFFER_SELECTED": "created", "OFFERS_PREPARED": "created",
        "DISPATCHED_BY_SENDER": "in_transport", "DISPATCHED_BY_SENDER_TO_POK": "in_transport",
        "TAKEN_BY_COURIER": "in_transport", "TAKEN_BY_COURIER_FROM_POK": "in_transport",
        "COLLECTED_FROM_SENDER": "in_transport", "ADOPTED_AT_SOURCE_BRANCH": "in_transport",
        "ADOPTED_AT_SORTING_CENTER": "in_transport", "SENT_FROM_SOURCE_BRANCH": "in_transport",
        "SENT_FROM_SORTING_CENTER": "in_transport", "ADOPTED_AT_TARGET_BRANCH": "in_transport",
        "READDRESSED": "in_transport", "REDIRECT_TO_BOX": "in_transport",
        "PERMANENTLY_REDIRECTED_TO_BOX_MACHINE": "in_transport",
        "PERMANENTLY_REDIRECTED_TO_CUSTOMER_SERVICE_POINT": "in_transport",
        "UNSTACK_FROM_BOX_MACHINE": "in_transport", "AVIZO": "in_transport",
        "OUT_FOR_DELIVERY": "handed_out_for_delivery", "OUT_FOR_DELIVERY_TO_ADDRESS": "handed_out_for_delivery",
        "UNSTACK_FROM_CUSTOMER_SERVICE_POINT": "handed_out_for_delivery",
        "PICKUP_REMINDER_SENT_ADDRESS": "handed_out_for_delivery",
        "READY_TO_PICKUP": "waiting_for_pickup", "READY_FOR_COLLECTION": "waiting_for_pickup",
        "READY_TO_PICKUP_FROM_BRANCH": "waiting_for_pickup", "READY_TO_PICKUP_FROM_POK": "waiting_for_pickup",
        "READY_TO_PICKUP_FROM_POK_REGISTERED": "waiting_for_pickup", "PICKUP_REMINDER_SENT": "waiting_for_pickup",
        "STACK_IN_BOX_MACHINE": "waiting_for_pickup", "STACK_IN_CUSTOMER_SERVICE_POINT": "waiting_for_pickup",
        "AVIZO_COMPLETED": "waiting_for_pickup", "DELIVERED": "delivered", "COLLECTED_BY_CUSTOMER": "delivered",
        "RETURNED_TO_SENDER": "returned", "RETURN_PICKUP_CONFIRMATION_TO_SENDER": "returned",
        "NOT_COLLECTED": "returned", "PICKUP_TIME_EXPIRED": "returned",
        "STACK_PARCEL_PICKUP_TIME_EXPIRED": "returned",
        "STACK_PARCEL_IN_BOX_MACHINE_PICKUP_TIME_EXPIRED": "returned",
        "CANCELED": "cancelled", "CANCELLED": "cancelled", "CANCELED_REDIRECT_TO_BOX": "cancelled",
        "DELAY_IN_DELIVERY": "exception", "DELIVERY_ATTEMPT_FAILED": "exception", "UNDELIVERED": "exception",
        "UNDELIVERED_COD_CASH_RECEIVER": "exception", "UNDELIVERED_INCOMPLETE_ADDRESS": "exception",
        "UNDELIVERED_LACK_OF_ACCESS_LETTERBOX": "exception", "UNDELIVERED_NO_MAILBOX": "exception",
        "UNDELIVERED_NOT_LIVE_ADDRESS": "exception", "UNDELIVERED_UNKNOWN_RECEIVER": "exception",
        "UNDELIVERED_WRONG_ADDRESS": "exception", "REJECTED_BY_RECEIVER": "exception", "MISSING": "exception",
        "OVERSIZED": "exception", "CLAIMED": "exception", "COD_REJECTED": "exception", "C2X_REJECTED": "exception",
        "AVIZO_REJECTED": "exception", "COD_COMPLETED": "in_transport", "C2X_COMPLETED": "in_transport",
        "OTHER": "unknown",
    },
    "dpd": {
        "READY_TO_SEND": "created", "RECEIVED_FROM_SENDER": "in_transport", "SENT": "in_transport",
        "IN_TRANSPORT": "in_transport", "RECEIVED_IN_DEPOT": "in_transport", "REDIRECTED": "in_transport",
        "RESCHEDULED": "in_transport", "HANDED_OVER_FOR_DELIVERY": "handed_out_for_delivery",
        "READY_TO_PICK_UP": "waiting_for_pickup", "SELF_PICKUP": "waiting_for_pickup",
        "HARD_RESERVED": "waiting_for_pickup", "DELIVERED": "delivered", "PICKED_UP": "delivered",
        "RETURNED_TO_SENDER": "returned", "EXPIRED_PICKUP": "returned", "UNSUCCESSFUL_DELIVERY": "exception",
    },
    "dhl": {
        "NONE": "created", "SHIPMENTINPREPARATION": "created", "INPREPARATION": "created",
        "WAITINGFORCOURIERPICKUP": "created", "POSTED": "in_transport", "SENT": "in_transport",
        "POSTEDATPOINT": "in_transport", "PICKEDUPBYCOURIER": "in_transport", "ROUTE": "in_transport",
        "REDIRECTED": "in_transport", "REDIRECTEDTOPOINT": "in_transport", "DELIVERY": "handed_out_for_delivery",
        "FOR_DELIVERY": "handed_out_for_delivery", "DELIVERYTOPOINT": "handed_out_for_delivery",
        "DELIVERYTOLOCKER": "handed_out_for_delivery", "READY": "waiting_for_pickup",
        "DELIVEREDTOPOINT": "waiting_for_pickup", "DELIVEREDTOLOCKER": "waiting_for_pickup",
        "DELIVEREDTOPARCELLOCKER": "waiting_for_pickup", "DELIVEREDTOPICKUPPOINT": "waiting_for_pickup",
        "RETRIEVEDFROMPOINT": "delivered", "RETRIEVEDFROMLOCKER": "delivered", "DELIVERED": "delivered",
        "ROUTETOSENDER": "returned", "PARCELRETURNSTOSENDER": "returned", "PARCELRETURNEDTOSENDER": "returned",
        "RETURN": "returned", "RESIGNATED": "cancelled", "ERROR": "exception", "DELIVERYDELAY": "exception",
        "DELIVERYPROBLEM": "exception", "UNSUCCESSFULATTEMPTATDELIVERY": "exception",
        "SECONDUNSUCCESSFULATTEMPTATDELIVERY": "exception", "REFUSAL": "exception", "LOST": "exception",
        "DISPOSED": "exception",
    },
    "pocztex": {
        "PRZYGOTOWANA": "created", "NADANA": "in_transport", "W TRANSPORCIE": "in_transport",
        "W DORĘCZENIU": "handed_out_for_delivery", "W DORECZENIU": "handed_out_for_delivery",
        "AWIZOWANA": "waiting_for_pickup", "P_KWD": "waiting_for_pickup", "ODEBRANA W PUNKCIE": "delivered",
        "P_OWU": "delivered",
    },
}

_SHARED_STATUS_FALLBACK = {
    "pl": {
        "created": "Utworzona", "in_transport": "W transporcie", "handed_out_for_delivery": "Wydana do doręczenia",
        "waiting_for_pickup": "Gotowa do odbioru", "delivered": "Doręczona", "returned": "Zwrócona do nadawcy",
        "cancelled": "Anulowana", "exception": "Problem z doręczeniem", "unknown": "Nieznany status",
    },
    "en": {
        "created": "Created", "in_transport": "In transit", "handed_out_for_delivery": "Out for delivery",
        "waiting_for_pickup": "Ready for pickup", "delivered": "Delivered", "returned": "Returned to sender",
        "cancelled": "Cancelled", "exception": "Delivery issue", "unknown": "Unknown status",
    },
}

def _normalize_language(language):
    if not language:
        return "en"
    return str(language).replace("_", "-").split("-")[0].lower()

def _get_hass_language(hass):
    if not hass:
        return None
    return getattr(hass.config, "language", None)

def _translate_label(key, language):
    lang = _normalize_language(language)
    labels = _LABEL_TRANSLATIONS.get(key, {})
    return labels.get(lang) or labels.get("en") or key

def _normalize_status(raw_status, courier):
    status_text = str(raw_status or "").strip()
    if not status_text:
        return "unknown"

    status_upper = status_text.upper()
    if courier_map := _STATUS_MAP.get(courier):
        if mapped := courier_map.get(status_upper):
            return mapped

    status_lower = status_text.lower()
    status_ascii = status_lower.translate(str.maketrans("ąćęłńóśżź", "acelnoszz"))

    if any(x in status_lower for x in ["locker", "point", "ready", "awizo", "pickup", "collection"]):
        return "waiting_for_pickup"
    if any(x in status_lower for x in ["picked up", "collected", "delivered", "odebr", "dostarcz"]):
        return "delivered"
    if any(x in status_lower for x in ["return", "zwrot", "odesl"]):
        return "returned"
    if any(x in status_lower for x in ["cancel", "anul", "rezygn"]):
        return "cancelled"
    if any(x in status_lower for x in ["fail", "error", "problem", "niedorecz", "miss", "reject"]):
        return "exception"
    if any(x in status_lower or x in status_ascii for x in ["out for delivery", "w doreczeniu", "wydana kurierowi"]):
        return "handed_out_for_delivery"
    if any(x in status_lower for x in ["transit", "transport", "depart", "arrive", "process", "adopt"]):
        return "in_transport"
    if any(x in status_lower for x in ["created", "label", "info received", "prepared"]):
        return "created"

    return "unknown"

def _get_shared_translations(language):
    lang = _normalize_language(language)
    if lang in _SHARED_TRANSLATION_CACHE:
        return _SHARED_TRANSLATION_CACHE[lang]

    fallback = _SHARED_STATUS_FALLBACK.get(lang, _SHARED_STATUS_FALLBACK["en"])
    shared = {key.upper(): value for key, value in fallback.items()}
    _SHARED_TRANSLATION_CACHE[lang] = shared
    return shared

def _translate_status(raw_status, courier, language):
    status_text = str(raw_status or "").strip()
    if not status_text:
        return _get_shared_translations(language).get("UNKNOWN", "Unknown")

    normalized = _normalize_status(status_text, courier)
    shared_translations = _get_shared_translations(language)
    return shared_translations.get(normalized.upper(), status_text)

def _get_raw_status(parcel_data, courier):
    if not parcel_data:
        return None
    if courier in ["inpost", "dhl"]:
        return parcel_data.get("status")
    if courier == "dpd":
        return (parcel_data.get("main_status") or {}).get("status")
    if courier == "pocztex":
        if not isinstance(parcel_data, dict): return None
        for key in ["status", "state", "statusName", "statusLabel"]:
            val = parcel_data.get(key)
            if isinstance(val, str): return val
            if isinstance(val, dict): return val.get("name") or val.get("label")
    return None

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.add_entities_callback = async_add_entities
    from . import _update_entities
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
        if self._courier in ["inpost", "dhl"]:
            return data.get("shipmentNumber")
        if self._courier == "dpd":
            return data.get("waybill")
        if self._courier == "pocztex":
            return data.get("trackingId") or data.get("number")
        return "unknown"

    @property
    def native_value(self):
        raw_status = _get_raw_status(self.parcel_data, self._courier)
        return _translate_status(raw_status, self._courier, self._language)

    @property
    def extra_state_attributes(self):
        raw_status = _get_raw_status(self.parcel_data, self._courier)
        attrs = {
            "courier": self._courier,
            "tracking_number": self._tracking_number,
            "status_raw": raw_status,
            "status_key": _normalize_status(raw_status, self._courier),
        }
        if self._courier == "inpost":
            attrs["sender"] = self.parcel_data.get("sender", {}).get("name")
            p_point = self.parcel_data.get("pickUpPoint") or {}
            addr = p_point.get("addressDetails") or {}
            attrs["location"] = f"{addr.get('street', '')} {addr.get('buildingNumber', '')}".strip()
            attrs["open_code"] = self.parcel_data.get("openCode")
        return attrs

    def _handle_coordinator_update(self) -> None:
        parcels = self.coordinator.data
        my_parcel = next((p for p in parcels if self._get_id(p) == self._tracking_number), None)
        if my_parcel:
            self.parcel_data = my_parcel
            self._attr_available = True
        else:
            self._attr_available = False
        self.async_write_ha_state()