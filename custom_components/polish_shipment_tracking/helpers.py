"""Helper functions for Polish Shipment Tracking."""
from .const import DOMAIN

def get_parcel_id(data: dict, courier: str) -> str | None:
    """Extract parcel ID from data based on courier."""
    if courier == "inpost":
        return data.get("shipmentNumber")
    if courier == "dpd":
        return data.get("waybill")
    if courier == "dhl":
        return data.get("shipmentNumber")
    if courier == "pocztex":
        return _pick_pocztex_id(data)
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

def get_raw_status(parcel_data: dict, courier: str) -> str | None:
    """Extract raw status from data based on courier."""
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

def normalize_status(raw_status, courier):
    """Normalize status to one of the predefined keys."""
    status_text = str(raw_status or "").strip()
    if not status_text:
        return "unknown"

    status_upper = status_text.upper()
    courier_map = _STATUS_MAP.get(courier, {})
    if status_upper in courier_map:
        return courier_map[status_upper]

    status_lower = status_text.lower()
    status_ascii = status_lower.translate(str.maketrans("ąćęłńóśżź", "acelnoszz"))
    
    # Generic fallbacks
    if status_lower in {"ready"}:
        return "waiting_for_pickup"
    if any(x in status_lower for x in ["delivered to locker", "delivered to point", "delivered to parcel locker", "delivered to pickup point"]):
        return "waiting_for_pickup"
    if any(x in status_lower for x in ["picked up", "collected by", "collected"]):
        return "delivered"
    if any(x in status_lower for x in ["ready for collection", "ready to pick", "ready for pick"]):
        return "waiting_for_pickup"
    if any(x in status_lower for x in ["pickup", "collection", "locker"]):
        return "waiting_for_pickup"
    if "delivered" in status_lower:
        return "delivered"
    if "awizo" in status_ascii:
        return "waiting_for_pickup"
    if any(x in status_ascii for x in ["odebr", "wydan", "odebrane"]):
        return "delivered"
    if any(x in status_ascii for x in ["dorecz", "dostarcz"]):
        return "delivered"
    if any(x in status_ascii for x in ["zwrot", "odesl"]):
        return "returned"
    if any(x in status_ascii for x in ["anul", "rezygn"]):
        return "cancelled"
    if any(x in status_ascii for x in ["problem", "niedorecz", "odmow"]):
        return "exception"
    if any(x in status_lower for x in ["out for delivery", "handed over for delivery"]):
        return "handed_out_for_delivery"
    if any(x in status_lower for x in ["return", "returned"]):
        return "returned"
    if any(x in status_lower for x in ["cancel", "canceled", "cancelled"]):
        return "cancelled"
    if any(x in status_lower for x in ["fail", "failed", "delay", "exception", "undeliver", "missing", "rejected"]):
        return "exception"
    if any(x in status_lower for x in ["transit", "in transport", "departed", "arrived", "processed", "received", "adopted"]):
        return "in_transport"
    if any(x in status_lower for x in ["created", "pre-transit", "label", "confirmed", "info received", "ready to send"]):
        return "created"

    return "unknown"

def is_delivered(data: dict, courier: str) -> bool:
    """Check if parcel is delivered."""
    status_key = normalize_status(get_raw_status(data, courier), courier)
    return status_key in {"delivered", "returned", "cancelled"}
