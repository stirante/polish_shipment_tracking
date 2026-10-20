"""Checks for ORLEN Paczka status mapping, parcel identity and incoming filter."""

import asyncio
import importlib.util
import runpy
import sys
import types
import unittest
from pathlib import Path


PACKAGE_DIR = (
    Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"
)
HELPERS = runpy.run_path(str(PACKAGE_DIR / "helpers.py"))
get_parcel_id = HELPERS["get_parcel_id"]
get_raw_status = HELPERS["get_raw_status"]
normalize_status = HELPERS["normalize_status"]
is_delivered = HELPERS["is_delivered"]


def _load_api_orlen():
    # Load the module alone: Home Assistant and async_timeout are not
    # installed in this repository's lightweight test environment.
    sys.modules.setdefault("async_timeout", types.ModuleType("async_timeout"))
    api_helpers = runpy.run_path(str(PACKAGE_DIR / "api_helpers.py"))
    package = types.ModuleType("orlen_pkg")
    package.__path__ = []
    helpers = types.ModuleType("orlen_pkg.api_helpers")
    helpers.request_json = None
    helpers.normalize_phone = api_helpers["normalize_phone"]
    stubs = {"orlen_pkg": package, "orlen_pkg.api_helpers": helpers}
    if importlib.util.find_spec("aiohttp") is None:
        aiohttp = types.ModuleType("aiohttp")
        aiohttp.ClientSession = object
        aiohttp.ClientTimeout = lambda **kwargs: None
        stubs["aiohttp"] = aiohttp
    for name, module in stubs.items():
        sys.modules.setdefault(name, module)
    spec = importlib.util.spec_from_file_location(
        "orlen_pkg.api_orlen", PACKAGE_DIR / "api_orlen.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OrlenApi = _load_api_orlen().OrlenApi


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


class OrlenIncomingFilterTests(unittest.TestCase):
    def _parcels(self, receiver_phones):
        api = OrlenApi(None, phone="600100200", device_id="dev")
        shipments = [
            {"barcode": str(i), "receiver": {"phone": phone}}
            for i, phone in enumerate(receiver_phones)
        ]

        async def fake_request(method, path, body=None):
            return {"data": {"data": shipments}}

        api._request = fake_request
        return asyncio.run(api.get_parcels())

    def test_receiver_phone_with_country_code_is_incoming(self):
        parcels = self._parcels(["+48 600 100 200", "48600100200", "600100200"])
        self.assertEqual([p["barcode"] for p in parcels], ["0", "1", "2"])

    def test_parcel_for_another_phone_is_skipped(self):
        self.assertEqual(self._parcels(["700100200", None]), [])


if __name__ == "__main__":
    unittest.main()
