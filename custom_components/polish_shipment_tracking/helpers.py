"""Helper functions for Polish Shipment Tracking."""


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
    if courier == "gls":
        return _pick_gls_id(data)
    if courier == "allegro":
        return data.get("orderId")
    return None

def get_parcel_detail_id(data: dict, courier: str) -> str | None:
    """Extract parcel detail endpoint ID from data based on courier."""
    if courier == "pocztex":
        return _pick_pocztex_detail_id(data)
    return get_parcel_id(data, courier)

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

def _pick_pocztex_detail_id(parcel_data):
    if not parcel_data or not isinstance(parcel_data, dict):
        return None
    for key in ("id", "trackingId", "trackingID"):
        if key in parcel_data and parcel_data[key] is not None:
            return str(parcel_data[key])
    return None

_DHL_PROBLEM_STATUSES = {"exception", "returned", "cancelled"}
_DHL_PROGRESS = {
    "created": 0,
    "in_transport": 1,
    "handed_out_for_delivery": 2,
    "waiting_for_pickup": 3,
    "delivered": 4,
}


def get_raw_status(parcel_data: dict, courier: str) -> str | None:
    """Extract raw status from data based on courier."""
    if not parcel_data:
        return None
    if courier == "inpost":
        return parcel_data.get("status")
    if courier == "dpd":
        return (parcel_data.get("main_status") or {}).get("status")
    if courier == "dhl":
        # DHL exposes two status signals: the coarse TT_* code (`status`) and the
        # fine-grained timeline label (`menuTimelineLabel.status`). The TT_* code is
        # ambiguous around the delivery phase — e.g. TT_LK covers both "courier out
        # for delivery" and "on the way to / ready at a POP/BOX point" — while the
        # timeline label distinguishes Delivery / DeliveryToPoint / DeliveredToPoint
        # / RetrievedFromPoint. Prefer the timeline label so the status tracks the
        # DHL app, but let the TT_* code win for problem states (exception /
        # returned / cancelled), which the timeline label does not surface.
        tt = str(parcel_data.get("status") or "").strip()
        timeline = parcel_data.get("menuTimelineLabel")
        menu_status = ""
        if isinstance(timeline, dict):
            menu_status = str(timeline.get("status") or "").strip()

        # Never let one signal drag the other backwards: the timeline label can
        # lag behind the TT_* code (e.g. TT_OP/TT_AWI while the label still says
        # Delivery), so pick whichever is further along.
        tt_key = normalize_status(tt, "dhl")
        menu_key = normalize_status(menu_status, "dhl")
        if tt_key in _DHL_PROBLEM_STATUSES:
            return tt
        if menu_key in _DHL_PROBLEM_STATUSES:
            return menu_status
        if _DHL_PROGRESS.get(menu_key, -1) > _DHL_PROGRESS.get(tt_key, -1):
            return menu_status
        return tt or menu_status or None
    if courier == "pocztex":
        return _pick_pocztex_status(parcel_data)
    if courier == "gls":
        return _pick_gls_status(parcel_data)
    if courier == "allegro":
        return parcel_data.get("status")
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

def _pick_gls_id(parcel_data):
    if not parcel_data or not isinstance(parcel_data, dict):
        return None
    tracking_shipment = parcel_data.get("trackingShipment")
    if isinstance(tracking_shipment, dict):
        parcel_data = tracking_shipment
    for key in ("shipmentNo", "trackingId", "trackingUid", "packageNo", "packageUid"):
        if parcel_data.get(key) is not None:
            return str(parcel_data.get(key))
    return None

def _pick_gls_status(parcel_data):
    if not parcel_data or not isinstance(parcel_data, dict):
        return None
    tracking_shipment = parcel_data.get("trackingShipment")
    if isinstance(tracking_shipment, dict):
        return _pick_gls_status(tracking_shipment)
    # progressBarIdent is always the English machine-readable code (e.g. INDELIVERY),
    # while state may be a localized Polish string (e.g. "W doręczeniu") which breaks mapping.
    ident = parcel_data.get("progressBarIdent")
    if isinstance(ident, str) and ident:
        return ident
    status = parcel_data.get("state") or parcel_data.get("status")
    if status is not None:
        return str(status)
    statuses = parcel_data.get("packageStatuses")
    if isinstance(statuses, list) and statuses:
        latest = statuses[0]
        if isinstance(latest, dict):
            for key in ("state", "status", "code", "name"):
                if latest.get(key) is not None:
                    return str(latest.get(key))
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
        "HANDED_OVER_FOR_DELIVERY_PUDO": "handed_out_for_delivery",
        "HANDED_OVER_FOR_DELIVERY_SP": "handed_out_for_delivery",
        "READY_TO_PICK_UP": "waiting_for_pickup",
        "READY_TO_PICK_UP_PUDO": "waiting_for_pickup",
        "READY_TO_PICK_UP_SP": "waiting_for_pickup",
        "SELF_PICKUP": "waiting_for_pickup",
        "HARD_RESERVED": "waiting_for_pickup",
        "DELIVERED": "delivered",
        "PICKED_UP": "delivered",
        "RETURNED_TO_SENDER": "returned",
        "EXPIRED_PICKUP": "returned",
        "UNSUCCESSFUL_DELIVERY": "exception",
    },
    "dhl": {
        "TT_MAG": "in_transport",
        # EDWP = the sender still has the parcel; DHL shows "Nadawca
        # przygotowuje przesyłkę do wysyłki" and leaves the timeline at step 0.
        "TT_EDWP": "created",
        "TT_DWP_PUNKT": "handed_out_for_delivery",
        "TT_DWP_INT": "handed_out_for_delivery",
        "TT_DWP": "handed_out_for_delivery",
        "TT_MAG_INT": "in_transport",
        # LK = handed to the courier for delivery (internalStatus MAGLK, timeline
        # "Delivery", "Kurier już jedzie z przesyłką") - not yet collectable.
        "TT_LK": "handed_out_for_delivery",
        "TT_AWI": "waiting_for_pickup",
        "TT_OP": "delivered",
        "TT_DELAY_KUR": "exception",
        "TT_DELAY_MAG": "exception",
        "TT_OWL": "exception",
        "TT_DOR": "delivered",
        "TT_CS": "in_transport",
        "TT_ZWN": "returned",
        "TT_ZGN": "exception",
        "TT_LIK": "exception",
        "TT_DOR_ZWN": "returned",
        "SP_DSP": "in_transport",
        "TT_PRZEKIERUJ": "in_transport",
        "SP_CN": "cancelled",
        "ERR": "exception",
        "NONE": "created",
        "SHIPMENTINPREPARATION": "created",
        "INPREPARATION": "created",
        "WAITINGFORCOURIERPICKUP": "created",
        "ALLSTATUSES": "in_transport",
        "INDELIVERY": "handed_out_for_delivery",
        "ONTHEROAD": "in_transport",
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
        "DELIVEREDTOSENDER": "returned",
        "RETURNTOSENDER": "returned",
        "ROUTETOSENDER": "returned",
        "PARCELRETURNSTOSENDER": "returned",
        "PARCELRETURNEDTOSENDER": "returned",
        "RETURN": "returned",
        "RESIGNED": "cancelled",
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
    "gls": {
        "PREADVICE": "created",
        "PROCESSING": "created",
        "INTRANSIT": "in_transport",
        "INWAREHOUSE": "in_transport",
        "INPICKUP": "in_transport",
        "INDELIVERY": "handed_out_for_delivery",
        "READY_FOR_PICKUP": "waiting_for_pickup",
        "DELIVEREDPS": "waiting_for_pickup",
        "DELIVERED": "delivered",
        "RETURNED": "returned",
        "CANCELLED": "cancelled",
        "CANCELED": "cancelled",
        "NOTDELIVERED": "exception",
        "NOTPICKEDUP": "returned",
        "MULTIPACK": "in_transport",
        "UNAVAILABLE": "exception",
    },
    "allegro": {
        "NEW": "created",
        "IN_PREPARATION": "created",
        "PROCESSING": "created",
        "READY_FOR_PROCESSING": "created",
        "READY_FOR_SHIPMENT": "created",
        "SENT": "in_transport",
        "IN_TRANSIT": "in_transport",
        "IN_DELIVERY": "handed_out_for_delivery",
        "AVAILABLE_FOR_PICKUP": "waiting_for_pickup",
        "DELIVERED": "delivered",
        "PICKED_UP": "delivered",
        "COMPLETED": "delivered",
        "RETURNED": "returned",
        "ORDER_CANCELLED": "cancelled",
        "CANCELLED": "cancelled",
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

    # Allegro lists orders before they ship (paid, being packed...) under
    # codes we have not seen yet; those are still orders to wait for.
    if courier == "allegro":
        return "created"

    return "unknown"

def count_ready_for_pickup(parcels: list[dict], courier: str) -> int:
    """Count parcels whose normalized status means they await collection."""
    return sum(
        normalize_status(get_raw_status(parcel, courier), courier) == "waiting_for_pickup"
        for parcel in parcels
        if isinstance(parcel, dict)
    )


def is_delivered(data: dict, courier: str) -> bool:
    """Check if parcel is delivered."""
    # Pocztex archives parcels with state/stateCode nulled out, which would
    # otherwise normalize to "unknown" and resurface the parcel as active.
    # Parcels that merely lack a state (e.g. still awaiting the first scan)
    # keep archived=false and must stay active.
    if courier == "pocztex" and data.get("archived") is True:
        return True
    status_key = normalize_status(get_raw_status(data, courier), courier)
    return status_key in {"delivered", "returned", "cancelled"}


def reconcile_departed_parcels(
    previous: list[dict] | None,
    current: list[dict],
    courier: str,
    missing_counts: dict[str, int],
) -> tuple[list[tuple[str, dict]], list[dict], dict[str, int]]:
    """Describe terminal parcels and confirm missing parcels on a second poll.

    The coordinator exposes only active parcels, so this comparison must happen
    against the fresh, unfiltered response before terminal parcels are dropped.
    Keep a parcel active through its first missing response so a transiently
    incomplete feed cannot remove its entity or fire a false removal event.
    """
    if previous is None or not isinstance(current, list):
        return [], [], {}

    current_by_id = {}
    for parcel in current:
        if isinstance(parcel, dict):
            parcel_id = get_parcel_id(parcel, courier)
            if parcel_id is not None:
                current_by_id[str(parcel_id)] = parcel

    events = []
    retained = []
    next_missing_counts = {}
    for old_parcel in previous:
        if not isinstance(old_parcel, dict):
            continue
        parcel_id = get_parcel_id(old_parcel, courier)
        if parcel_id is None:
            continue

        parcel_id = str(parcel_id)
        new_parcel = current_by_id.get(parcel_id)
        if new_parcel is not None and not is_delivered(new_parcel, courier):
            continue

        if new_parcel is None:
            missed = missing_counts.get(parcel_id, 0) + 1
            if missed < 2:
                retained.append(old_parcel)
                next_missing_counts[parcel_id] = missed
                continue

        old_raw_status = get_raw_status(old_parcel, courier)
        event_data = {
            "courier": courier,
            "shipment_id": parcel_id,
            "old_status_raw": old_raw_status,
            "old_status_key": normalize_status(old_raw_status, courier),
        }
        if new_parcel is not None:
            new_raw_status = get_raw_status(new_parcel, courier)
            new_status_key = normalize_status(new_raw_status, courier)
            if new_status_key in {"delivered", "returned", "cancelled"}:
                events.append(
                    (
                        "shipment_status_changed",
                        {
                            **event_data,
                            "new_status_raw": new_raw_status,
                            "new_status_key": new_status_key,
                        },
                    )
                )
                continue
            reason = "archived"
        else:
            reason = "missing_from_feed"

        events.append(("shipment_removed", {**event_data, "reason": reason}))

    return events, retained, next_missing_counts


def get_shipment_entity_id(
    registry, domain: str, courier: str, entry_id: str, parcel_id: str
) -> str | None:
    """Find this account's parcel entity across old and account-scoped IDs."""
    for unique_id in (
        f"{courier}_{entry_id}_{parcel_id}",
        f"{courier}_{parcel_id}",
    ):
        entity_id = registry.async_get_entity_id("sensor", domain, unique_id)
        if entity_id is None:
            continue
        entity = registry.async_get(entity_id)
        if entity is not None and entity.config_entry_id == entry_id:
            return entity_id
    return None


def normalize_allegro_orders(payload) -> list[dict]:
    """Flatten the Allegro myorders response into one parcel dict per order.

    A group bundles orders from one checkout; every order inside has its own
    seller, delivery and status, so each becomes a separate parcel.
    """
    if not isinstance(payload, dict):
        return []
    parcels = []
    for group in payload.get("orderGroups") or []:
        if not isinstance(group, dict):
            continue
        for order in group.get("myorders") or []:
            if not isinstance(order, dict) or not order.get("id"):
                continue
            if order.get("hiddenInMyOrders"):
                continue
            status = order.get("status") if isinstance(order.get("status"), dict) else {}
            primary = status.get("primary") if isinstance(status.get("primary"), dict) else {}
            custom = status.get("primaryCustom") if isinstance(status.get("primaryCustom"), dict) else {}
            delivery = order.get("delivery") if isinstance(order.get("delivery"), dict) else {}
            waybills_data = delivery.get("waybillsData") if isinstance(delivery.get("waybillsData"), dict) else {}

            waybills = []
            pickup_code = None
            for waybill in waybills_data.get("waybills") or []:
                if not isinstance(waybill, dict) or not waybill.get("waybillId"):
                    continue
                carrier = waybill.get("carrier") if isinstance(waybill.get("carrier"), dict) else {}
                waybills.append({
                    "number": str(waybill["waybillId"]),
                    "carrier_id": carrier.get("id"),
                    "carrier_name": carrier.get("name"),
                    "url": carrier.get("url"),
                })
                code = waybill.get("pickupCode")
                if isinstance(code, dict) and code.get("code") and not pickup_code:
                    pickup_code = code.get("code")

            raw_status = primary.get("status") or delivery.get("status")
            if order.get("cancelled"):
                raw_status = "ORDER_CANCELLED"

            seller = order.get("seller") if isinstance(order.get("seller"), dict) else {}
            offers = []
            for offer in order.get("offers") or []:
                if not isinstance(offer, dict):
                    continue
                unit_price = offer.get("unitPrice") if isinstance(offer.get("unitPrice"), dict) else {}
                offers.append({
                    "title": offer.get("title"),
                    "quantity": offer.get("quantity"),
                    "url": offer.get("friendlyUrl"),
                    "image_url": offer.get("imageUrl"),
                    "unit_price": unit_price.get("amount"),
                    "currency": unit_price.get("currency"),
                })

            parcels.append({
                "orderId": str(order["id"]),
                "groupId": group.get("groupId"),
                "status": raw_status,
                "statusLabel": custom.get("label"),
                "orderDate": order.get("orderDate"),
                "seller": seller.get("login"),
                "offers": offers,
                "deliveryName": delivery.get("name"),
                "deliveredBy": delivery.get("deliveredBy"),
                "deliveryStatusDate": delivery.get("timestamp"),
                "pickupPoint": delivery.get("generalDelivery"),
                "pickupCode": pickup_code,
                "waybills": waybills,
                "totalCost": order.get("totalCost"),
                "_raw_response": order,
            })
    return parcels


def merge_allegro_details(parcel: dict, details) -> dict:
    """Add recipient, timeline and point coordinates from the order details call."""
    if not isinstance(details, dict):
        return parcel
    order = next(
        (
            item
            for item in details.get("myorders") or []
            if isinstance(item, dict) and str(item.get("id")) == parcel.get("orderId")
        ),
        None,
    )
    if order is None:
        return parcel
    merged = dict(parcel)
    delivery = order.get("delivery") if isinstance(order.get("delivery"), dict) else {}

    # Only the delivery address describes the recipient; the details also carry
    # the seller's address and phone, which must never reach the filters.
    address = delivery.get("address") if isinstance(delivery.get("address"), dict) else {}
    name = " ".join(part for part in (address.get("firstName"), address.get("lastName")) if part)
    recipient = {
        "name": name or None,
        "street": address.get("street"),
        "zipCode": address.get("zipCode"),
        "city": address.get("city"),
        "phoneNumber": address.get("phoneNumber"),
    }
    merged["recipient"] = {key: value for key, value in recipient.items() if value}

    timelines = [item for item in order.get("timelines") or [] if isinstance(item, dict)]
    if timelines:
        timeline = timelines[0]
        merged["timeline"] = [
            {
                "label": step.get("label"),
                "hint": step.get("hint"),
                "active": bool(step.get("active")),
                "error": bool(step.get("error")),
            }
            for step in timeline.get("steps") or []
            if isinstance(step, dict)
        ]
        estimate = [
            detail.get("value")
            for detail in timeline.get("details") or []
            if isinstance(detail, dict) and detail.get("type") == "TEXT" and detail.get("value")
        ]
        if estimate:
            merged["deliveryEstimate"] = " ".join(estimate)
        point = (timeline.get("pickup") or {}).get("point") if isinstance(timeline.get("pickup"), dict) else None
        if isinstance(point, dict):
            coordinates = point.get("coordinates") if isinstance(point.get("coordinates"), dict) else {}
            if coordinates.get("lat") and coordinates.get("lon"):
                merged["pickupPointLocation"] = {"lat": coordinates["lat"], "lon": coordinates["lon"]}
            hours = [
                item.get("value")
                for item in point.get("openingTimes") or []
                if isinstance(item, dict) and item.get("value")
            ]
            if hours:
                merged["pickupPointHours"] = ", ".join(hours)
    return merged


def get_account_label(entry_data: dict) -> str | None:
    """Human account identifier used in device and entity names."""
    label = entry_data.get("phone") or entry_data.get("email") or entry_data.get("login")
    # Allegro accounts without a nickname log in as "client:<id>", which only
    # clutters entity ids.
    if isinstance(label, str) and label.lower().startswith("client:"):
        return None
    return label


def normalize_tracking_number(value) -> str:
    """Canonical form used to match one parcel across accounts."""
    return "".join(ch for ch in str(value or "").upper() if ch.isalnum())


def get_parcel_tracking_numbers(parcel: dict, courier: str) -> set[str]:
    """Every tracking number a parcel is known under, normalized.

    Carriers expose a few aliases (GLS shipmentNo/trackingId, Pocztex
    consignment number), and Allegro may reference any of them.
    """
    if not isinstance(parcel, dict):
        return set()
    if courier == "allegro":
        values = [waybill.get("number") for waybill in parcel.get("waybills") or []]
    else:
        values = [get_parcel_id(parcel, courier)]
        sources = [parcel]
        if isinstance(parcel.get("trackingShipment"), dict):
            sources.append(parcel["trackingShipment"])
        for source in sources:
            for key in (
                "shipmentNumber",
                "shipmentNo",
                "trackingId",
                "trackingNumber",
                "consignmentNumber",
                "waybill",
                "parcelNumber",
            ):
                if isinstance(source.get(key), (str, int)):
                    values.append(source[key])
    return {number for number in map(normalize_tracking_number, values) if len(number) >= 6}


# Keys whose subtree describes who receives the parcel or where it goes.
_RECIPIENT_KEYS = (
    "receiver",
    "recipient",
    "courierdeliveryshipmentinfo",
    "deliveryaddress",
    "delivery_address",
    "consignee",
    "pickuppoint",
    "lockerinfo",
    "dhlpointinfo",
    "parcelshop",
    "point",
)


def _fold_text(value) -> str:
    text = str(value or "").lower()
    text = text.translate(str.maketrans("ąćęłńóśżź", "acelnoszz"))
    return " ".join(text.split())


def _collect_strings(value, out: list[str]) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _collect_strings(item, out)
    elif isinstance(value, list):
        for item in value:
            _collect_strings(item, out)
    elif isinstance(value, (str, int)) and not isinstance(value, bool):
        out.append(str(value))


def get_recipient_texts(parcel: dict) -> list[str]:
    """Collect recipient name, phone and address strings from any carrier payload."""
    texts: list[str] = []

    def _walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                folded = str(key).lower()
                if any(marker in folded for marker in _RECIPIENT_KEYS):
                    _collect_strings(item, texts)
                elif isinstance(item, (dict, list)):
                    _walk(item)
        elif isinstance(value, list):
            for item in value:
                _walk(item)

    _walk(parcel)
    return texts


def get_recipient_contacts(parcel: dict) -> tuple[list[str], list[str]]:
    """Recipient phone numbers (last 9 digits) and e-mail addresses, for the card filter."""
    phones: list[str] = []
    emails: list[str] = []
    for text in get_recipient_texts(parcel):
        if "@" in text and "." in text.split("@")[-1]:
            email = text.strip().lower()
            if email not in emails:
                emails.append(email)
            continue
        digits = _digits(text)
        # Phone numbers only: tracking and point ids are longer or shorter.
        if 9 <= len(digits) <= 12 and digits[-9:] not in phones:
            phones.append(digits[-9:])
    return phones, emails


def parse_recipient_patterns(value) -> list[str]:
    """Split the options text (lines or commas) into patterns."""
    if not value:
        return []
    if isinstance(value, list):
        parts = value
    else:
        parts = str(value).replace(",", "\n").splitlines()
    return [part.strip() for part in parts if part and part.strip()]


def _digits(text: str) -> str:
    return "".join(ch for ch in str(text) if ch.isdigit())


def _pattern_matches(pattern: str, texts: list[str]) -> bool | None:
    """True/False for a match, None when the parcel has no data to decide on."""
    digits = _digits(pattern)
    if len(digits) >= 6 and not any(ch.isalpha() for ch in pattern):
        # Phone numbers: compare the last 9 digits so +48 / spaces don't matter.
        phones = [_digits(text) for text in texts if len(_digits(text)) >= 9]
        if not phones:
            return None
        wanted = digits[-9:]
        return any(wanted in phone for phone in phones)
    if not texts:
        return None
    folded = _fold_text(pattern)
    return any(folded in _fold_text(text) for text in texts)


def matches_recipient_filters(parcel: dict, include: list[str], exclude: list[str]) -> bool:
    """Return False when the parcel is filtered out by the account options.

    A parcel is only hidden on evidence: when the carrier gives no phone
    number (Allegro lists only the pickup point, for example), phone patterns
    cannot rule it out and the parcel stays visible.
    """
    if not include and not exclude:
        return True
    texts = get_recipient_texts(parcel)
    if any(_pattern_matches(pattern, texts) for pattern in exclude):
        return False
    if include:
        results = [_pattern_matches(pattern, texts) for pattern in include]
        if not any(results) and None not in results:
            return False
    return True
