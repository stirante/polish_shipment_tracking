"""Delivery time records and arrival prediction."""

import runpy
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

DT = runpy.run_path(
    str(
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "polish_shipment_tracking"
        / "delivery_times.py"
    )
)
RECORDS = DT["RECORDS"]
parse_hint = DT["parse_hint"]
record = DT["record"]
record_allegro_timeline = DT["record_allegro_timeline"]
predict = DT["predict"]
handed_out_at = DT["handed_out_at"]
delivery_place = DT["delivery_place"]
is_home = DT["is_home"]
record_home_delivery = DT["record_home_delivery"]

TZ = timezone(timedelta(hours=1))
NOW = datetime(2026, 11, 17, 9, 30, tzinfo=TZ)
POINT = "Automat ORLEN Paczka, Przykładowa 1, 00-001, Miasto"


def at(day, hour, minute):
    return datetime(2026, 11, day, hour, minute, tzinfo=TZ)


class ParseHintTests(unittest.TestCase):
    def test_allegro_hint_with_nbsp(self):
        self.assertEqual(parse_hint("Od wt.\xa017\xa0lis\xa009:05", NOW), at(17, 9, 5))

    def test_hint_with_year(self):
        self.assertEqual(parse_hint("16 lis. 2026, 09:24", NOW), at(16, 9, 24))

    def test_december_hint_read_in_january_is_last_year(self):
        january = datetime(2027, 1, 3, 10, 0, tzinfo=TZ)
        self.assertEqual(parse_hint("Od pon. 28 gru 11:00", january).year, 2026)

    def test_unreadable_hints(self):
        self.assertIsNone(parse_hint(None, NOW))
        self.assertIsNone(parse_hint("dzisiaj w punkcie", NOW))
        self.assertIsNone(parse_hint("Od pt. 31 lis 10:00", NOW))


class RecordTests(unittest.TestCase):
    def setUp(self):
        RECORDS.clear()

    def test_needs_location_and_known_status(self):
        self.assertFalse(record("A", "inpost", None, "waiting_for_pickup", NOW))
        self.assertFalse(record("A", "inpost", POINT, "in_transport", NOW))
        self.assertEqual(RECORDS, {})

    def test_same_time_is_not_a_change_and_overwrite_can_be_refused(self):
        self.assertTrue(record("A", "allegro", POINT, "waiting_for_pickup", at(17, 8, 13)))
        self.assertFalse(record("A", "allegro", POINT, "waiting_for_pickup", at(17, 8, 13)))
        self.assertFalse(record("A", "allegro", POINT, "waiting_for_pickup", at(17, 8, 30), overwrite=False))
        self.assertEqual(RECORDS["A"]["arrived"], at(17, 8, 13).isoformat())

    def test_allegro_timeline_steps(self):
        timeline = [
            {"type": "IN_TRANSIT", "hint": "Od pon. 16 lis 17:45"},
            {"type": "IN_DELIVERY", "hint": "Od wt. 17 lis 09:05"},
            {"type": "DELIVERED", "hint": None},
            "junk",
        ]
        self.assertTrue(record_allegro_timeline("W1", POINT, timeline, NOW))
        self.assertEqual(handed_out_at("W1"), at(17, 9, 5))
        self.assertNotIn("arrived", RECORDS["W1"])
        self.assertIsNone(handed_out_at("missing"))


class HomeDeliveryTests(unittest.TestCase):
    def setUp(self):
        RECORDS.clear()

    def test_place_is_the_point_or_the_courier_route(self):
        self.assertEqual(delivery_place("dpd", POINT), POINT)
        self.assertEqual(delivery_place("dpd", None), "home:dpd")
        self.assertEqual(delivery_place("dhl", "", "Długa 1, Miasto"), "home:dhl:Długa 1, Miasto")
        self.assertTrue(is_home("Home:DPD"))
        self.assertFalse(is_home(POINT))

    def test_delivered_parcel_arrives_at_the_door(self):
        record("W1", "dpd", "home:dpd", "handed_out_for_delivery", at(17, 8, 0), shipment_id="S1")
        self.assertTrue(record_home_delivery("S1", at(17, 13, 15)))
        self.assertEqual(RECORDS["W1"]["arrived"], at(17, 13, 15).isoformat())
        # Only the first delivery report counts.
        self.assertFalse(record_home_delivery("S1", at(17, 13, 30)))

    def test_door_parcel_waiting_for_pickup_is_not_an_arrival(self):
        record("W1", "dpd", "home:dpd", "handed_out_for_delivery", at(17, 8, 0))
        self.assertFalse(record("W1", "dpd", "home:dpd", "waiting_for_pickup", at(17, 9, 0)))
        self.assertNotIn("arrived", RECORDS["W1"])

    def test_delivery_of_unknown_or_point_parcel_is_ignored(self):
        self.assertFalse(record_home_delivery("nothing", at(17, 13, 0)))
        record("P1", "inpost", POINT, "handed_out_for_delivery", at(17, 8, 0), shipment_id="P1")
        self.assertFalse(record_home_delivery("P1", at(17, 18, 0)))
        self.assertNotIn("arrived", RECORDS["P1"])

    def test_door_prediction_uses_this_courier_only(self):
        for i, (h, m) in enumerate([(12, 10), (13, 0), (14, 20)]):
            record(f"D{i}", "dpd", "home:dpd", "handed_out_for_delivery", at(1 + i, 8, 0), shipment_id=f"D{i}")
            record_home_delivery(f"D{i}", at(1 + i, h, m))
        record("G1", "gls", "home:gls", "handed_out_for_delivery", at(5, 8, 0), shipment_id="G1")
        record_home_delivery("G1", at(5, 9, 0))
        result = predict("home:dpd", at(17, 8, 30))
        self.assertEqual(result["samples"], 3)
        self.assertEqual(result["expected"], at(17, 13, 0))
        self.assertIsNone(predict("home:gls", at(17, 8, 30)))


class PredictTests(unittest.TestCase):
    def setUp(self):
        RECORDS.clear()

    def test_no_data(self):
        self.assertIsNone(predict(POINT, at(17, 9, 0)))
        self.assertIsNone(predict(None, at(17, 9, 0)))

    def test_from_arrival_hours_at_this_point(self):
        for i, (h, m) in enumerate([(10, 3), (11, 38), (11, 13), (10, 55), (11, 24), (8, 13)]):
            record(f"P{i}", "allegro", POINT, "waiting_for_pickup", at(1 + i, h, m))
        record("other", "allegro", "Paczkomat ABC01M", "waiting_for_pickup", at(10, 9, 30))
        result = predict(POINT, at(17, 9, 5))
        self.assertEqual(result["samples"], 5)
        self.assertEqual(result["expected"], at(17, 11, 13))
        self.assertEqual(result["earliest"], at(17, 10, 3))
        self.assertEqual(result["latest"], at(17, 11, 38))

    def test_falls_back_to_delay_after_late_hand_out(self):
        for i, (out, arrived) in enumerate([((7, 30), (8, 13)), ((9, 0), (11, 0)), ((8, 0), (9, 0))]):
            record(f"D{i}", "allegro", POINT, "handed_out_for_delivery", at(1 + i, *out))
            record(f"D{i}", "allegro", POINT, "waiting_for_pickup", at(1 + i, *arrived))
        result = predict(POINT, at(17, 14, 0))
        self.assertEqual(result["samples"], 3)
        self.assertEqual(result["expected"], at(17, 15, 0))
        self.assertEqual(result["earliest"], at(17, 14, 43))
        self.assertEqual(result["latest"], at(17, 16, 0))


if __name__ == "__main__":
    unittest.main()
