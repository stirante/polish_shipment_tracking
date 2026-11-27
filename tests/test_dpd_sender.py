"""Check the DPD sender label built from the sender's name and company."""

import ast
import unittest
from pathlib import Path


SENSOR_FILE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "polish_shipment_tracking"
    / "sensor.py"
)


class DpdSenderLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load only the helper: Home Assistant is not installed in this
        # repository's lightweight test environment.
        tree = ast.parse(SENSOR_FILE.read_text())
        selected = [
            node for node in tree.body
            if getattr(node, "name", None) == "_dpd_sender_label"
        ]
        module = ast.Module(body=selected, type_ignores=[])
        namespace = {}
        exec(compile(module, str(SENSOR_FILE), "exec"), namespace)
        cls.label = staticmethod(namespace["_dpd_sender_label"])

    def test_company_only(self):
        self.assertEqual(
            self.label({"name": "", "company": "Example Furniture S.A."}),
            "Example Furniture S.A.",
        )

    def test_name_only(self):
        self.assertEqual(
            self.label({"name": "Jan Kowalski", "company": ""}), "Jan Kowalski"
        )

    def test_company_and_name(self):
        self.assertEqual(
            self.label({"name": "Jan Kowalski", "company": "Example Sp. z o.o."}),
            "Example Sp. z o.o. (Jan Kowalski)",
        )

    def test_same_name_and_company_shown_once(self):
        self.assertEqual(
            self.label({"name": "EXAMPLE SHOP", "company": "Example Shop"}),
            "Example Shop",
        )

    def test_missing_fields(self):
        self.assertEqual(self.label({"name": None}), "")


if __name__ == "__main__":
    unittest.main()
