"""Saving a refreshed token must not reload the entry; other changes must."""

import ast
import asyncio
import types
import unittest
from pathlib import Path


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"


def _load(filename, *names):
    # Home Assistant is not installed here: load only the functions under test.
    tree = ast.parse((COMPONENT / filename).read_text(encoding="utf-8"))
    body = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names
    ]
    for node in body:
        node.returns = None
        for arg in node.args.args:
            arg.annotation = None
    namespace = {"DOMAIN": "polish_shipment_tracking"}
    exec(compile(ast.Module(body=body, type_ignores=[]), filename, "exec"), namespace)
    return namespace


METHODS = _load("coordinator.py", "_save_auth", "entry_changed_since_setup")
LISTENER = _load("__init__.py", "_async_options_updated")["_async_options_updated"]


class Coordinator:
    _save_auth = METHODS["_save_auth"]
    entry_changed_since_setup = METHODS["entry_changed_since_setup"]


class TokenSaveReloadTests(unittest.TestCase):
    def setUp(self):
        self.entry = types.SimpleNamespace(entry_id="entry", data={"token": "old"}, options={})
        self.reloads = []

        async def reload(entry_id):
            self.reloads.append(entry_id)

        def update(entry, data):
            entry.data = data

        self.coordinator = Coordinator()
        self.coordinator.entry = self.entry
        self.coordinator._own_data = dict(self.entry.data)
        self.coordinator._own_options = {}
        self.hass = types.SimpleNamespace(
            data={"polish_shipment_tracking": {"entry": self.coordinator}},
            config_entries=types.SimpleNamespace(async_reload=reload, async_update_entry=update),
        )
        self.coordinator.hass = self.hass

    def _notify(self):
        asyncio.run(LISTENER(self.hass, self.entry))
        return self.reloads

    def test_saved_token_does_not_reload(self):
        self.coordinator._save_auth({"token": "new"})
        self.assertEqual(self._notify(), [])

    def test_external_data_change_reloads(self):
        self.entry.data = {"token": "from reauth"}
        self.assertEqual(self._notify(), ["entry"])

    def test_option_change_reloads(self):
        self.entry.options = {"hidden_shipments": "123456"}
        self.assertEqual(self._notify(), ["entry"])


if __name__ == "__main__":
    unittest.main()
