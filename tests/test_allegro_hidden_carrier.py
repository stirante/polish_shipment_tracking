"""Parcels hidden in a carrier account must stay hidden in Allegro."""

import ast
import logging
import runpy
import unittest
from pathlib import Path


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"
HELPERS = runpy.run_path(str(COMPONENT / "helpers.py"))


class ShipmentCoordinator:
    pass


def _load_carrier_tracking_numbers():
    # Home Assistant is not installed here: load only the one method.
    tree = ast.parse((COMPONENT / "coordinator.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_carrier_tracking_numbers":
            module = ast.Module(body=[node], type_ignores=[])
            namespace = {
                "DOMAIN": "polish_shipment_tracking",
                "ShipmentCoordinator": ShipmentCoordinator,
                "get_parcel_tracking_numbers": HELPERS["get_parcel_tracking_numbers"],
            }
            exec(compile(module, "coordinator.py", "exec"), namespace)
            return namespace["_carrier_tracking_numbers"]
    raise AssertionError("_carrier_tracking_numbers not found")


class FakeHass:
    def __init__(self):
        self.data = {}


def _load_filter():
    tree = ast.parse((COMPONENT / "coordinator.py").read_text(encoding="utf-8"))
    node = next(n for n in ast.walk(tree) if getattr(n, "name", None) == "_filter_active_parcels")
    namespace = {
        **HELPERS,
        "is_dead_label": lambda parcel, courier: bool(parcel.get("stale")),
        "_LOGGER": logging.getLogger(__name__),
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), "coordinator.py", "exec"), namespace)
    return namespace["_filter_active_parcels"]


def _coordinator(courier, data, hidden=(), delivered=()):
    coordinator = ShipmentCoordinator()
    coordinator.courier = courier
    coordinator.data = data
    coordinator.hidden_tracking_numbers = set(hidden)
    coordinator.delivered_tracking_numbers = set(delivered)
    return coordinator


class AllegroHiddenCarrierTests(unittest.TestCase):
    def setUp(self):
        self.carrier_tracking_numbers = _load_carrier_tracking_numbers()
        self.allegro = _coordinator("allegro", [])
        self.allegro.hass = FakeHass()

    def test_hidden_carrier_number_counts_as_tracked(self):
        inpost = _coordinator("inpost", [], hidden={"620012345678"})
        self.allegro.hass.data["polish_shipment_tracking"] = {"inpost": inpost}
        self.assertIn("620012345678", self.carrier_tracking_numbers(self.allegro))

    def test_visible_carrier_parcel_still_counts(self):
        inpost = _coordinator("inpost", [{"shipmentNumber": "620099999999"}])
        self.allegro.hass.data["polish_shipment_tracking"] = {"inpost": inpost}
        self.assertIn("620099999999", self.carrier_tracking_numbers(self.allegro))

    def test_delivered_carrier_parcel_counts_after_restart(self):
        # DHL already dropped the delivered parcel from its data while
        # Allegro still lists the order as under way.
        dhl = _coordinator("dhl", [], delivered={"JJD000000000000001"})
        self.allegro.hass.data["polish_shipment_tracking"] = {"dhl": dhl}
        self.assertIn("JJD000000000000001", self.carrier_tracking_numbers(self.allegro))

    def test_only_delivered_parcels_are_remembered(self):
        inpost = _coordinator("inpost", [])
        inpost._hidden_shipments = set()
        inpost._include_recipients = []
        inpost._exclude_recipients = ["600111222"]
        parcels = [
            {"shipmentNumber": "620000000001", "status": "DELIVERED"},
            {
                "shipmentNumber": "620000000002",
                "status": "OUT_FOR_DELIVERY",
                "receiver": {"phoneNumber": {"value": "600111222"}},
            },
            {"shipmentNumber": "620000000003", "status": "CONFIRMED", "stale": True},
        ]
        self.assertEqual(_load_filter()(inpost, parcels), [])
        # The other two are shown nowhere unless Allegro still lists them.
        self.assertEqual(inpost.delivered_tracking_numbers, {"620000000001"})

    def test_dpd_parcel_counts_under_its_allegro_number(self):
        dpd = _coordinator(
            "dpd", [{"waybill": "1000000000002U", "display_waybill": "AD00000000000001A"}]
        )
        self.allegro.hass.data["polish_shipment_tracking"] = {"dpd": dpd}
        self.assertIn("AD00000000000001A", self.carrier_tracking_numbers(self.allegro))


if __name__ == "__main__":
    unittest.main()
