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
get_orlen_pickup_code = HELPERS["get_orlen_pickup_code"]


def _load_api_orlen():
    # Load the module alone: Home Assistant and async_timeout are not
    # installed in this repository's lightweight test environment.
    sys.modules.setdefault("async_timeout", types.ModuleType("async_timeout"))
    if "aiohttp" not in sys.modules and importlib.util.find_spec("aiohttp") is None:
        aiohttp = types.ModuleType("aiohttp")
        aiohttp.ClientSession = object
        aiohttp.ClientTimeout = lambda **kwargs: None
        sys.modules["aiohttp"] = aiohttp
    # api_helpers imports aiohttp, so it loads only after the stub is in place.
    api_helpers = runpy.run_path(str(PACKAGE_DIR / "api_helpers.py"))
    package = types.ModuleType("orlen_pkg")
    package.__path__ = []
    helpers = types.ModuleType("orlen_pkg.api_helpers")
    helpers.request_json = None
    helpers.normalize_phone = api_helpers["normalize_phone"]
    for name, module in {"orlen_pkg": package, "orlen_pkg.api_helpers": helpers}.items():
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



# Shape of the per-shipment response, made-up values (list leaves "events" null).
_LIST_ITEM = {
    "id": "100000001",
    "barcode": "1000000000001",
    "statusid": "intransit",
    "statusname": "Paczka w drodze do punktu odbioru",
    "events": None,
    "receiver": {"phone": "600100200"},
    "pincollection": {"pin": "123456"},
}
_DETAILS = {
    **_LIST_ITEM,
    "events": [
        {"time": "2026-01-01T10:00:00", "typeid": "created", "typename": "Paczka w trakcie przygotowania", "comments": None},
        {"time": "2026-01-03T10:00:00", "typeid": "intransit", "typename": "Paczka w drodze do punktu odbioru", "comments": ""},
        {"time": "2026-01-02T10:00:00", "typeid": "sent", "typename": "Paczka nadana", "comments": ""},
    ],
}


class OrlenHistoryTests(unittest.TestCase):
    def _parcels(self, details=_DETAILS, list_item=_LIST_ITEM):
        api = OrlenApi(None, phone="600100200", device_id="dev")
        calls = []

        async def fake_request(method, path, body=None):
            calls.append(path)
            if path.endswith("/shipments"):
                return {"data": [list_item]}
            if isinstance(details, Exception):
                raise details
            return {"data": [details]}

        api._request = fake_request
        return asyncio.run(api.get_parcels()), calls

    def test_history_comes_from_shipment_details(self):
        parcels, calls = self._parcels()
        self.assertIn("customers/600100200/dev/shipments/100000001", calls)
        self.assertEqual(
            [event["status"] for event in parcels[0]["events"]],
            ["intransit", "sent", "created"],
        )
        self.assertEqual(parcels[0]["events"][0]["label"], "Paczka w drodze do punktu odbioru")
        self.assertIsNone(parcels[0]["events"][0]["comment"])

    def test_failed_details_keep_the_parcel(self):
        parcels, _ = self._parcels(details=Exception("boom"))
        self.assertEqual(parcels[0]["barcode"], "1000000000001")
        self.assertEqual(parcels[0]["events"], [])

    def test_archived_parcel_skips_details(self):
        _, calls = self._parcels(list_item={**_LIST_ITEM, "archiveshipment": True})
        self.assertEqual(len(calls), 1)


class OrlenPickupCodeTests(unittest.TestCase):
    def test_no_code_while_in_transit(self):
        parcel = {"statusid": "intransit", "pickup_code": "123456"}
        self.assertIsNone(get_orlen_pickup_code(parcel))

    def test_code_once_in_the_box(self):
        parcel = {"statusid": "deposited", "pickup_code": "123456"}
        self.assertEqual(get_orlen_pickup_code(parcel), "123456")


if __name__ == "__main__":
    unittest.main()
