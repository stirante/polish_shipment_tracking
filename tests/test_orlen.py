"""Checks for ORLEN Paczka status mapping and parcel identity."""

import runpy
import unittest
from pathlib import Path


HELPERS = runpy.run_path(
    str(
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "polish_shipment_tracking"
        / "helpers.py"
    )
)
get_parcel_id = HELPERS["get_parcel_id"]
get_raw_status = HELPERS["get_raw_status"]
normalize_status = HELPERS["normalize_status"]
is_delivered = HELPERS["is_delivered"]


class OrlenTests(unittest.TestCase):
    def test_parcel_id_is_barcode(self):
        self.assertEqual(get_parcel_id({"barcode": "ABC123"}, "orlen"), "ABC123")

    def test_status_mapping(self):
        cases = {
            "INTRANSIT": "in_transport",
            "DEPOSITED": "waiting_for_pickup",
            "COLLECTED": "delivered",
            "EXPIRED": "returned",
        }
        for raw, key in cases.items():
            parcel = {"barcode": "1", "statusid": raw}
            self.assertEqual(
                normalize_status(get_raw_status(parcel, "orlen"), "orlen"), key
            )

    def test_waiting_parcel_is_active(self):
        self.assertFalse(is_delivered({"barcode": "1", "statusid": "DEPOSITED"}, "orlen"))

    def test_archived_parcel_is_finished(self):
        parcel = {"barcode": "1", "statusid": None, "archived": True}
        self.assertTrue(is_delivered(parcel, "orlen"))


if __name__ == "__main__":
    unittest.main()
