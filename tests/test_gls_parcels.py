"""GLS parcel list endpoint and token persistence after a failed fetch."""

import ast
import asyncio
import importlib.util
import logging
import sys
import types
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"


def _load_api_gls():
    if "aiohttp" not in sys.modules and importlib.util.find_spec("aiohttp") is None:
        sys.modules.setdefault("aiohttp", types.ModuleType("aiohttp"))
    spec = importlib.util.spec_from_file_location("gls_api_gls", COMPONENT / "api_gls.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateFailed(Exception):
    pass


class ConfigEntryAuthFailed(Exception):
    pass


class InPostAuthError(Exception):
    pass


def _load_update_data():
    # Home Assistant is not installed here: load only the one method.
    tree = ast.parse((COMPONENT / "coordinator.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_async_update_data":
            namespace = {
                "UpdateFailed": UpdateFailed,
                "ConfigEntryAuthFailed": ConfigEntryAuthFailed,
                "InPostAuthError": InPostAuthError,
                "_LOGGER": logging.getLogger("test_gls_parcels"),
            }
            module = ast.Module(body=[node], type_ignores=[])
            exec(compile(module, "coordinator.py", "exec"), namespace)
            return namespace["_async_update_data"]
    raise AssertionError("_async_update_data not found")


class FailingCoordinator:
    courier = "gls"

    def __init__(self, error):
        self.error = error
        self.persisted = 0

    async def _fetch_parcels_with_retry(self):
        raise self.error

    def _persist_auth_if_changed(self):
        self.persisted += 1


class GlsParcelListTests(unittest.TestCase):
    def test_parcel_list_uses_the_paged_endpoint(self):
        api_gls = _load_api_gls()
        api = api_gls.GlsApi(session=None, session_id="session")
        calls = []

        async def fake_request(method, url):
            calls.append((method, url))
            return {"content": []}

        api.request = fake_request
        self.assertEqual(asyncio.run(api.get_parcels()), {"content": []})

        method, url = calls[0]
        parsed = urlparse(url)
        self.assertEqual(method, "GET")
        self.assertTrue(parsed.path.endswith("/mygls-tracking/tracking/shipment/paged"))
        self.assertEqual(
            parse_qs(parsed.query),
            {"size": ["100"], "page": ["0"], "archive": ["false"]},
        )


class FakeResponse:
    def __init__(self, status, text):
        self.status = status
        self._text = text

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    """Answers like GLS: only registered session ids may read the parcel list."""

    def __init__(self, known_sessions, list_status=200):
        self.known = set(known_sessions)
        self.list_status = list_status
        self.calls = []

    def request(self, method, url, headers, json):
        session_id = headers["SessionId"]
        self.calls.append((method, url.rsplit("/", 1)[-1].split("?")[0], session_id))
        if url.endswith("/user/session"):
            self.known.add(json["sessionId"])
            return FakeResponse(200, "")
        if session_id not in self.known:
            return FakeResponse(500, "404 page not found\n")
        if self.list_status != 200:
            return FakeResponse(self.list_status, "boom")
        return FakeResponse(200, '{"content": []}')


def _api(session, session_id="old"):
    api = _load_api_gls().GlsApi(session=session, session_id=session_id)
    api._token = "token"
    api._expires_at = 2**31
    api._session_registered = session_id
    return api


class GlsSessionTests(unittest.TestCase):
    def test_dropped_session_is_replaced_and_the_request_retried(self):
        session = FakeSession(known_sessions=[])
        api = _api(session)

        with self.assertLogs(level="INFO"):
            self.assertEqual(asyncio.run(api.get_parcels()), {"content": []})

        new_id = api.export_auth_data()["session_id"]
        self.assertNotEqual(new_id, "old")
        self.assertEqual(api.export_auth_data()["session_registered"], new_id)
        self.assertEqual(
            session.calls,
            [("GET", "paged", "old"), ("POST", "session", new_id), ("GET", "paged", new_id)],
        )

    def test_known_session_is_kept(self):
        session = FakeSession(known_sessions=["old"])
        api = _api(session)

        asyncio.run(api.get_parcels())

        self.assertEqual(api.export_auth_data()["session_id"], "old")
        self.assertEqual(session.calls, [("GET", "paged", "old")])

    def test_other_errors_do_not_replace_the_session(self):
        session = FakeSession(known_sessions=["old"], list_status=500)
        api = _api(session)

        with self.assertRaisesRegex(Exception, "GLS API Error: 500 - boom"):
            asyncio.run(api.get_parcels())

        self.assertEqual(api.export_auth_data()["session_id"], "old")
        self.assertEqual(len(session.calls), 1)

    def test_gives_up_when_a_new_session_does_not_help(self):
        session = FakeSession(known_sessions=[])
        session.request_session = session.request

        def never_registers(method, url, headers, json):
            if url.endswith("/user/session"):
                session.calls.append((method, "session", headers["SessionId"]))
                return FakeResponse(200, "")
            return session.request_session(method, url, headers, json)

        session.request = never_registers
        api = _api(session)

        with self.assertLogs(level="INFO"):
            with self.assertRaisesRegex(Exception, "404 page not found"):
                asyncio.run(api.get_parcels())

        self.assertEqual([call[1] for call in session.calls], ["paged", "session", "paged"])


class TokenPersistenceTests(unittest.TestCase):
    def test_failed_fetch_saves_a_refreshed_token(self):
        update_data = _load_update_data()
        coordinator = FailingCoordinator(Exception("GLS API Error: 500 - 404 page not found"))

        with self.assertLogs("test_gls_parcels", level="ERROR"):
            with self.assertRaises(UpdateFailed):
                asyncio.run(update_data(coordinator))

        self.assertEqual(coordinator.persisted, 1)

    def test_inpost_auth_failure_does_not_save_tokens(self):
        update_data = _load_update_data()
        coordinator = FailingCoordinator(InPostAuthError("rejected"))

        with self.assertRaises(ConfigEntryAuthFailed):
            asyncio.run(update_data(coordinator))

        self.assertEqual(coordinator.persisted, 0)


if __name__ == "__main__":
    unittest.main()
