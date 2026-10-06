"""Checks for normalized ready-for-pickup counts."""

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
count_ready_for_pickup = HELPERS["count_ready_for_pickup"]


class ReadyForPickupCountTests(unittest.TestCase):
    def test_count_uses_normalized_pickup_status(self):
        parcels = [
            {"shipmentNumber": "ready", "status": "READY_TO_PICKUP"},
            {"shipmentNumber": "created", "status": "CONFIRMED"},
            {"shipmentNumber": "collected", "status": "COLLECTED_BY_CUSTOMER"},
        ]
        self.assertEqual(count_ready_for_pickup(parcels, "inpost"), 1)
        self.assertEqual(
            count_ready_for_pickup(
                [{"waybill": "dpd-1", "main_status": {"status": "READY_TO_PICK_UP"}}],
                "dpd",
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
