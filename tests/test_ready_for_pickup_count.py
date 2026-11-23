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
get_counted_parcels = HELPERS["get_counted_parcels"]


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

    def test_parcel_shared_with_another_account_is_counted_once(self):
        shared = {"shipmentNumber": "shared", "status": "READY_TO_PICKUP"}
        own = {"shipmentNumber": "own", "status": "OUT_FOR_DELIVERY"}
        delivered = {"shipmentNumber": "done", "status": "DELIVERED"}
        # The shared parcel's sensor belongs to the owner account only.
        owner = get_counted_parcels([shared, delivered], "inpost", {"shared", "done"})
        recipient = get_counted_parcels([own, shared], "inpost", {"own"})
        self.assertEqual(len(owner) + len(recipient), 2)
        self.assertEqual(
            count_ready_for_pickup(owner, "inpost") + count_ready_for_pickup(recipient, "inpost"),
            1,
        )


if __name__ == "__main__":
    unittest.main()
