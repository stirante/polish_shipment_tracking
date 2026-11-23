"""An Allegro order shipped in several parcels becomes one shipment per parcel."""

import ast
import runpy
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"
HELPERS = runpy.run_path(str(COMPONENT / "helpers.py"))
normalize_allegro_orders = HELPERS["normalize_allegro_orders"]
merge_allegro_details = HELPERS["merge_allegro_details"]
count_ready_for_pickup = HELPERS["count_ready_for_pickup"]
is_delivered = HELPERS["is_delivered"]
split_allegro_order = HELPERS["split_allegro_order"]
get_parcel_id = HELPERS["get_parcel_id"]
get_renamed_parcel = HELPERS["get_renamed_parcel"]
is_hidden_shipment = HELPERS["is_hidden_shipment"]
parse_hidden_shipments = HELPERS["parse_hidden_shipments"]
reconcile_departed_parcels = HELPERS["reconcile_departed_parcels"]
restore_allegro_parcels = HELPERS["restore_allegro_parcels"]
get_parcel_tracking_numbers = HELPERS["get_parcel_tracking_numbers"]


def _load_coordinator_helpers():
    # Home Assistant is not installed here: load only the module-level helpers.
    tree = ast.parse((COMPONENT / "coordinator.py").read_text(encoding="utf-8"))
    wanted = {"_may_have_parcel_left", "_SPLIT_ORDER_RECHECK"}
    body = [
        node
        for node in tree.body
        if (isinstance(node, ast.FunctionDef) and node.name in wanted)
        or (isinstance(node, ast.Assign) and any(getattr(t, "id", None) in wanted for t in node.targets))
    ]
    namespace = {
        "datetime": datetime,
        "timedelta": timedelta,
        "timezone": timezone,
        "get_allegro_parcel_count": HELPERS["get_allegro_parcel_count"],
    }
    exec(compile(ast.Module(body=body, type_ignores=[]), "coordinator.py", "exec"), namespace)
    return namespace


COORDINATOR = _load_coordinator_helpers()

ORDER_ID = "00000000-0000-4000-8000-000000000001"


def _waybill(number, code=None):
    waybill = {
        "waybillId": number,
        "carrier": {"id": "ALLEGRO", "name": "Allegro", "url": f"https://allegro.pl/t?numer={number}"},
    }
    if code:
        waybill["pickupCode"] = {"code": code, "qrCode": f"QR-{code}"}
    return waybill


def _order(status="READY_TO_SEND", waybills=None, order_date="2026-01-01T10:00:00.000Z"):
    waybills = waybills or [_waybill("AD00000000000001A"), _waybill("AD00000000000002B")]
    return {
        "orderGroups": [{
            "groupId": "g",
            "myorders": [{
                "id": ORDER_ID,
                "status": {"primary": {"status": status}, "primaryCustom": {"label": "Oczekuje na nadanie"}},
                "delivery": {"name": "Allegro Kurier DPD (AD)", "waybillsData": {"waybills": waybills}},
                "orderDate": order_date,
            }],
        }],
    }


def _timeline(number, status, label):
    return {
        "status": status,
        "waybillId": number,
        "label": label,
        "details": [{"type": "TEXT", "value": "Przewidywana dostawa u Ciebie do: pt. 2 sty"}],
        "carrier": {"id": "ALLEGRO", "name": "Allegro"},
        "steps": [
            {"label": "Zakup opłacony", "hint": "1 sty", "active": False},
            {"label": label, "hint": None, "active": True},
        ],
    }


def _details(*timelines):
    return {"myorders": [{"id": ORDER_ID, "delivery": {}, "timelines": list(timelines)}]}


def _parcels(order_status, first, second, waybills=None):
    order = normalize_allegro_orders(_order(order_status, waybills))[0]
    merged = merge_allegro_details(
        order,
        _details(
            _timeline("AD00000000000001A", *first),
            _timeline("AD00000000000002B", *second),
        ),
    )
    return split_allegro_order(merged)


class AllegroSplitOrderTests(unittest.TestCase):
    def test_each_parcel_is_its_own_shipment(self):
        parcels = _parcels("READY_TO_SEND", ("TO_BE_SENT", "Oczekuje na nadanie"), ("IN_TRANSIT", "W drodze"))
        self.assertEqual(
            [get_parcel_id(p, "allegro") for p in parcels], ["AD00000000000001A", "AD00000000000002B"]
        )
        self.assertEqual([p["status"] for p in parcels], ["TO_BE_SENT", "IN_TRANSIT"])
        self.assertEqual(parcels[1]["statusLabel"], "W drodze")
        self.assertEqual(parcels[1]["timeline"][-1]["label"], "W drodze")
        self.assertEqual([(p["parcelIndex"], p["parcelCount"]) for p in parcels], [(1, 2), (2, 2)])
        self.assertEqual([p["orderId"] for p in parcels], [ORDER_ID, ORDER_ID])

    def test_tracking_numbers_are_per_parcel(self):
        parcels = _parcels("READY_TO_SEND", ("TO_BE_SENT", "a"), ("TO_BE_SENT", "b"))
        self.assertEqual(get_parcel_tracking_numbers(parcels[0], "allegro"), {"AD00000000000001A"})

    def test_delivered_parcel_drops_while_the_other_stays(self):
        parcels = _parcels("DELIVERED", ("PICKED_UP", "Przesyłka odebrana"), ("IN_TRANSIT", "W drodze"))
        self.assertEqual([is_delivered(p, "allegro") for p in parcels], [True, False])

    def test_waiting_parcel_has_its_own_code(self):
        waybills = [_waybill("AD00000000000001A"), _waybill("AD00000000000002B", code="123456")]
        parcels = _parcels(
            "IN_TRANSIT", ("IN_TRANSIT", "W drodze"), ("AVAILABLE_FOR_PICKUP", "Odbierz przesyłkę"), waybills
        )
        self.assertEqual([p["pickupCode"] for p in parcels], [None, "123456"])
        self.assertEqual(parcels[1]["waybills"][0]["qr_code"], "QR-123456")
        self.assertEqual(count_ready_for_pickup(parcels, "allegro"), 1)

    def test_without_details_parcels_use_the_order_status(self):
        order = normalize_allegro_orders(_order("SENT"))[0]
        self.assertEqual([p["status"] for p in split_allegro_order(order)], ["SENT", "SENT"])

    def test_cancelled_order_cancels_every_parcel(self):
        order = normalize_allegro_orders(_order("SENT"))[0]
        order = merge_allegro_details({**order, "status": "ORDER_CANCELLED"}, _details(
            _timeline("AD00000000000001A", "IN_TRANSIT", "W drodze"),
        ))
        self.assertTrue(all(is_delivered(p, "allegro") for p in split_allegro_order(order)))

    def test_single_parcel_order_keeps_its_order_id(self):
        order = normalize_allegro_orders(_order("SENT", [_waybill("AD00000000000001A")]))[0]
        parcels = split_allegro_order(order)
        self.assertEqual(len(parcels), 1)
        self.assertEqual(get_parcel_id(parcels[0], "allegro"), ORDER_ID)


class AllegroSplitOrderRecheckTests(unittest.TestCase):
    def test_recent_split_order_is_rechecked_after_delivery(self):
        may_have_parcel_left = COORDINATOR["_may_have_parcel_left"]
        recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat().replace("+00:00", "Z")
        old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat().replace("+00:00", "Z")
        split = normalize_allegro_orders(_order("DELIVERED", order_date=recent))[0]
        self.assertTrue(may_have_parcel_left(split))
        self.assertFalse(may_have_parcel_left({**split, "orderDate": old}))
        single = normalize_allegro_orders(_order("DELIVERED", [_waybill("AD00000000000001A")], recent))[0]
        self.assertFalse(may_have_parcel_left(single))


class AllegroSplitHiddenTests(unittest.TestCase):
    def test_order_hidden_by_its_id_stays_hidden_when_split(self):
        hidden = parse_hidden_shipments(ORDER_ID)
        for parcel in split_allegro_order(normalize_allegro_orders(_order("SENT"))[0]):
            self.assertTrue(is_hidden_shipment(parcel, "allegro", hidden))

    def test_hiding_one_parcel_leaves_the_other(self):
        parcels = split_allegro_order(normalize_allegro_orders(_order("SENT"))[0])
        hidden = parse_hidden_shipments(parcels[0]["parcelId"])
        self.assertEqual([is_hidden_shipment(p, "allegro", hidden) for p in parcels], [True, False])


class AllegroSplitEventTests(unittest.TestCase):
    def setUp(self):
        self.single = normalize_allegro_orders(_order("SENT", [_waybill("AD00000000000001A")]))
        self.parcels = split_allegro_order(normalize_allegro_orders(_order("SENT"))[0])

    def _reconcile(self, old, new):
        return reconcile_departed_parcels(old, new, "allegro", {})

    def test_second_waybill_does_not_remove_the_order(self):
        self.assertEqual(self._reconcile(self.single, self.parcels), ([], [], {}))
        self.assertEqual(get_renamed_parcel(self.single[0], self.parcels), self.parcels[0])

    def test_order_without_waybills_becomes_its_first_parcel(self):
        order = [{**self.single[0], "waybills": []}]
        self.assertEqual(self._reconcile(order, self.parcels), ([], [], {}))
        self.assertEqual(get_renamed_parcel(order[0], self.parcels), self.parcels[0])

    def test_status_change_while_splitting_is_reported(self):
        parcels = [{**self.parcels[0], "status": "PICKED_UP"}, self.parcels[1]]
        events, retained, _ = self._reconcile(self.single, parcels)
        self.assertEqual([name for name, _ in events], ["shipment_status_changed"])
        self.assertEqual(events[0][1]["new_status_key"], "delivered")
        self.assertEqual(retained, [])

    def test_parcel_really_dropped_from_the_order_is_still_confirmed(self):
        events, retained, _ = self._reconcile(self.parcels, self.single)
        self.assertEqual(events, [])
        self.assertEqual(retained, [self.parcels[1]])


class AllegroDetailsFailureTests(unittest.TestCase):
    def setUp(self):
        self.previous = _parcels("IN_TRANSIT", ("PICKED_UP", "a"), ("IN_TRANSIT", "b"))

    def _restored(self, status, waybills=None):
        order = normalize_allegro_orders(_order(status, waybills))[0]
        return split_allegro_order(restore_allegro_parcels(order, self.previous))

    def test_parcels_keep_their_own_status(self):
        for status in ("DELIVERED", "IN_TRANSIT"):
            self.assertEqual([p["status"] for p in self._restored(status)], ["PICKED_UP", "IN_TRANSIT"])

    def test_lagging_order_list_keeps_both_parcels(self):
        self.assertEqual(len(self._restored("SENT", [_waybill("AD00000000000001A")])), 2)

    def test_new_pickup_code_wins(self):
        waybills = [_waybill("AD00000000000001A"), _waybill("AD00000000000002B", code="123456")]
        self.assertEqual(self._restored("SENT", waybills)[1]["pickupCode"], "123456")

    def test_cancelled_order_is_not_restored(self):
        order = {**normalize_allegro_orders(_order("SENT"))[0], "status": "ORDER_CANCELLED"}
        self.assertIs(restore_allegro_parcels(order, self.previous), order)


if __name__ == "__main__":
    unittest.main()
