"""DHL login without HA's shared cookie jar: DhlApi carries its own cookies."""

import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"


class FakeHeaders(dict):
    def getall(self, name, default=None):
        return self.get(name, default or [])


class FakeDhl:
    """Records the Cookie header of each call and sets cookies like mojdhl.pl."""

    SET_COOKIES = {
        "auth/captcha/challenge": [],
        "auth/generate-code": ["TS012c8f70=edge; Path=/"],
        "auth/validate-code": ["access-token=new-token; Path=/", "access-remember=remember; Path=/"],
    }

    def __init__(self):
        self.cookies_sent = {}

    async def request_json(self, session, method, url, *, json_data=None, headers=None, on_response=None, **kwargs):
        path = url.split("/public/", 1)[1]
        self.cookies_sent[path] = headers.get("Cookie", "")
        resp = types.SimpleNamespace(headers=FakeHeaders({"Set-Cookie": self.SET_COOKIES[path]}))
        on_response(resp)
        return {}


def _load_api_dhl(fake):
    package = types.ModuleType("dhl_pkg")
    package.__path__ = []
    helpers = types.ModuleType("dhl_pkg.api_helpers")
    helpers.request_json = fake.request_json
    helpers.normalize_phone = lambda phone: str(phone)[-9:]
    sys.modules["dhl_pkg"] = package
    sys.modules["dhl_pkg.api_helpers"] = helpers
    if "aiohttp" not in sys.modules and importlib.util.find_spec("aiohttp") is None:
        sys.modules["aiohttp"] = types.ModuleType("aiohttp")
    spec = importlib.util.spec_from_file_location("dhl_pkg.api_dhl", COMPONENT / "api_dhl.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DhlLoginTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeDhl()
        self.api = _load_api_dhl(self.fake).DhlApi(session=None)

        async def no_captcha():
            return "solved"

        self.api._solve_altcha = no_captcha

    def test_one_api_carries_cookies_from_code_request_to_code_check(self):
        async def login():
            await self.api.generate_code("518343101")
            await self.api.validate_code("518343101", "123456", "device")

        asyncio.run(login())

        self.assertEqual(self.fake.cookies_sent["auth/generate-code"], "")
        self.assertEqual(self.fake.cookies_sent["auth/validate-code"], "TS012c8f70=edge")
        self.assertEqual(self.api._cookies["access-token"], "new-token")

    def test_new_api_starts_without_another_accounts_cookies(self):
        asyncio.run(self.api.validate_code("518343101", "123456", "device"))
        second = type(self.api)(session=None)
        second._solve_altcha = self.api._solve_altcha

        asyncio.run(second.generate_code("791519155"))

        self.assertNotIn("access-token", self.fake.cookies_sent["auth/generate-code"])


if __name__ == "__main__":
    unittest.main()
