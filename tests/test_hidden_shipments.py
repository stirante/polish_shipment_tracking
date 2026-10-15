"""Checks for shipments hidden by hand in the account options."""

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
parse_hidden_shipments = HELPERS["parse_hidden_shipments"]
add_hidden_shipment = HELPERS["add_hidden_shipment"]
is_hidden_shipment = HELPERS["is_hidden_shipment"]


class HiddenShipmentsTests(unittest.TestCase):
    def test_parse_normalizes_lines_and_commas(self):
        self.assertEqual(
            parse_hidden_shipments("6200 1234 5678 9012 3456 78\n abc123456, \n"),
            {"6200123456789012345678", "ABC123456"},
        )

    def test_parse_empty(self):
        self.assertEqual(parse_hidden_shipments(None), set())
        self.assertEqual(parse_hidden_shipments(""), set())

    def test_add_appends_once(self):
        value = add_hidden_shipment("", "620012345678")
        self.assertEqual(value, "620012345678")
        self.assertEqual(add_hidden_shipment(value, "6200 1234 5678"), value)
        self.assertEqual(
            add_hidden_shipment(value, "999999999"), "620012345678\n999999999"
        )

    def test_inpost_parcel_is_hidden_by_number(self):
        parcel = {"shipmentNumber": "620012345678", "status": "READY_TO_PICKUP"}
        hidden = parse_hidden_shipments("620012345678")
        self.assertTrue(is_hidden_shipment(parcel, "inpost", hidden))
        self.assertFalse(
            is_hidden_shipment({"shipmentNumber": "620099999999"}, "inpost", hidden)
        )

    def test_nothing_hidden_keeps_parcel(self):
        parcel = {"shipmentNumber": "620012345678"}
        self.assertFalse(is_hidden_shipment(parcel, "inpost", set()))


if __name__ == "__main__":
    unittest.main()
