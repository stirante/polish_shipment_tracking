"""Checks for InPost multi-compartment metadata extraction and sensor attributes."""

import ast
import runpy
import unittest
from pathlib import Path


COMPONENT = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "polish_shipment_tracking"
)
HELPERS = runpy.run_path(str(COMPONENT / "helpers.py"))
get_inpost_multicompartment = HELPERS["get_inpost_multicompartment"]


def _load_add_inpost_attributes():
    tree = ast.parse((COMPONENT / "sensor.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ShipmentSensor":
            method = next(
                n
                for n in node.body
                if isinstance(n, ast.FunctionDef) and n.name == "_add_inpost_attributes"
            )
            module = ast.Module(body=[method], type_ignores=[])
            namespace = {"get_inpost_multicompartment": get_inpost_multicompartment}
            exec(compile(module, "sensor.py", "exec"), namespace)
            return namespace["_add_inpost_attributes"]
    raise AssertionError("_add_inpost_attributes not found")


class FakeShipmentSensor:
    def __init__(self, parcel_data: dict) -> None:
        self.parcel_data = parcel_data


class InPostMulticompartmentTests(unittest.TestCase):
    def test_extracts_active_multicompartment(self):
        parcel = {
            "shipmentNumber": "620012345678",
            "parcelSize": "B",
            "multiCompartment": {
                "uuid": "mc-uuid-123",
                "presentation": True,
                "collected": False,
                "shipmentNumbers": ["620012345678", "620087654321"],
            },
        }
        self.assertEqual(
            get_inpost_multicompartment(parcel),
            {
                "uuid": "mc-uuid-123",
                "presentation": True,
                "shipment_numbers": ["620012345678", "620087654321"],
            },
        )

    def test_ignores_collected_or_missing_uuid(self):
        self.assertIsNone(
            get_inpost_multicompartment(
                {
                    "multiCompartment": {
                        "uuid": "mc-uuid-123",
                        "collected": True,
                    }
                }
            )
        )
        self.assertIsNone(
            get_inpost_multicompartment({"multiCompartment": {"uuid": "  "}})
        )
        self.assertIsNone(get_inpost_multicompartment({"multiCompartment": None}))

    def test_sensor_exposes_multicompartment_and_size_attributes(self):
        add_attrs = _load_add_inpost_attributes()
        sensor = FakeShipmentSensor(
            {
                "shipmentNumber": "620012345678",
                "openCode": "123456",
                "parcelSize": "A",
                "multiCompartment": {
                    "uuid": "mc-uuid-999",
                    "presentation": False,
                    "collected": False,
                    "shipmentNumbers": ["620012345678", "620087654321"],
                },
            }
        )
        attrs = {}
        add_attrs(sensor, attrs)
        self.assertEqual(attrs["open_code"], "123456")
        self.assertEqual(attrs["parcel_size"], "A")
        self.assertTrue(attrs["is_multi_compartment"])
        self.assertEqual(attrs["multi_compartment_uuid"], "mc-uuid-999")
        self.assertFalse(attrs["multi_compartment_presentation"])
        self.assertEqual(
            attrs["multi_compartment_shipments"],
            ["620012345678", "620087654321"],
        )

    def test_sensor_omits_multicompartment_when_collected(self):
        add_attrs = _load_add_inpost_attributes()
        sensor = FakeShipmentSensor(
            {
                "shipmentNumber": "620012345678",
                "multiCompartment": {
                    "uuid": "mc-uuid-999",
                    "collected": True,
                },
            }
        )
        attrs = {}
        add_attrs(sensor, attrs)
        self.assertNotIn("is_multi_compartment", attrs)
        self.assertNotIn("multi_compartment_uuid", attrs)


if __name__ == "__main__":
    unittest.main()
