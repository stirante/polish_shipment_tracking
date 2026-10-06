"""Check shared count sensors survive a config-entry owner unload."""

import ast
import unittest
from pathlib import Path


SENSOR_FILE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "polish_shipment_tracking"
    / "sensor.py"
)


class FakeSensorEntity:
    def async_write_ha_state(self):
        pass


class FakeCoordinator:
    def __init__(self):
        self.listeners = []

    def async_add_listener(self, listener):
        self.listeners.append(listener)

        def unregister():
            self.listeners.remove(listener)

        return unregister


class FakeRegistry:
    def __init__(self):
        self.updated = []

    def async_get_entity_id(self, domain, platform, unique_id):
        return f"sensor.{unique_id}"

    def async_update_entity(self, entity_id, **changes):
        self.updated.append((entity_id, changes))


class SharedSensorOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load only the relevant definitions: Home Assistant is not installed
        # in this repository's lightweight test environment.
        tree = ast.parse(SENSOR_FILE.read_text())
        names = {
            "_set_shared_sensor_registry_owner",
            "_shared_sensor_host_unloaded",
            "_detach_shared_sensor",
            "ActiveShipmentsSensor",
            "ReadyForPickupShipmentsSensor",
        }
        selected = [node for node in tree.body if getattr(node, "name", None) in names]
        module = ast.Module(
            body=[
                ast.ImportFrom(
                    module="__future__", names=[ast.alias(name="annotations")], level=0
                ),
                *selected,
            ],
            type_ignores=[],
        )
        ast.fix_missing_locations(module)
        cls.registry = FakeRegistry()
        cls.scope = {
            "callback": lambda fn: fn,
            "SensorEntity": FakeSensorEntity,
            "SensorStateClass": type("SensorStateClass", (), {"MEASUREMENT": "measurement"}),
            "DOMAIN": "polish_shipment_tracking",
            "ACTIVE_SHIPMENTS_UNIQUE_ID": "polish_shipment_tracking_active_shipments",
            "READY_FOR_PICKUP_SHIPMENTS_UNIQUE_ID": "polish_shipment_tracking_ready_for_pickup_shipments",
            "SHARED_SENSOR_KEYS": (
                "_active_shipments_sensor",
                "_ready_for_pickup_shipments_sensor",
            ),
            "async_get_entity_registry": lambda hass: cls.registry,
        }
        exec(compile(module, str(SENSOR_FILE), "exec"), cls.scope)

    def setUp(self):
        self.registry.updated.clear()
        self.hass = type("Hass", (), {"data": {"polish_shipment_tracking": {}}})()
        self.data = self.hass.data["polish_shipment_tracking"]
        self.first = FakeCoordinator()
        self.second = FakeCoordinator()
        self.added = []
        self.data["_shared_sensor_hosts"] = {
            "first": (self.first, lambda entities: self.added.append(("first", entities))),
            "second": (self.second, lambda entities: self.added.append(("second", entities))),
        }
        self.data["_shared_sensor_owner"] = "first"
        self.old = [
            self.scope["ActiveShipmentsSensor"](self.hass),
            self.scope["ReadyForPickupShipmentsSensor"](self.hass),
        ]
        for key, sensor in zip(self.scope["SHARED_SENSOR_KEYS"], self.old):
            self.data[key] = sensor
            sensor.attach_coordinator(self.first)
            sensor.attach_coordinator(self.second)

    def test_owner_unload_rehomes_both_sensors_and_registry_entries(self):
        # ConfigEntry unload callbacks run last-in-first-out.
        self.scope["_shared_sensor_host_unloaded"](self.hass, "first")
        for key in self.scope["SHARED_SENSOR_KEYS"]:
            self.scope["_detach_shared_sensor"](self.data, key, self.first)

        self.assertEqual(self.data["_shared_sensor_owner"], "second")
        self.assertEqual(len(self.added), 1)
        self.assertEqual(self.added[0][0], "second")
        self.assertEqual(len(self.added[0][1]), 2)
        self.assertEqual(len(self.registry.updated), 2)
        self.assertTrue(all(change == {"config_entry_id": "second"} for _, change in self.registry.updated))
        for key, old_sensor in zip(self.scope["SHARED_SENSOR_KEYS"], self.old):
            self.assertIsNot(self.data[key], old_sensor)
            self.assertEqual(old_sensor._coordinators, {})
            self.assertEqual(set(self.data[key]._coordinators), {self.second})
        self.assertEqual(len(self.second.listeners), 2)

        self.scope["_shared_sensor_host_unloaded"](self.hass, "second")
        for key in self.scope["SHARED_SENSOR_KEYS"]:
            self.scope["_detach_shared_sensor"](self.data, key, self.second)
        self.assertNotIn("_shared_sensor_owner", self.data)
        self.assertNotIn("_shared_sensor_hosts", self.data)
        self.assertEqual(self.second.listeners, [])

    def test_non_owner_unload_keeps_the_shared_sensors(self):
        self.scope["_shared_sensor_host_unloaded"](self.hass, "second")
        for key in self.scope["SHARED_SENSOR_KEYS"]:
            self.scope["_detach_shared_sensor"](self.data, key, self.second)
        self.assertEqual(self.data["_shared_sensor_owner"], "first")
        self.assertEqual(self.added, [])
        self.assertEqual(self.registry.updated, [])
        for key, sensor in zip(self.scope["SHARED_SENSOR_KEYS"], self.old):
            self.assertIs(self.data[key], sensor)
            self.assertEqual(set(sensor._coordinators), {self.first})

    def test_last_host_unload_clears_cache_before_detach_callbacks(self):
        self.data["_shared_sensor_hosts"].pop("second")
        for sensor in self.old:
            sensor.detach_coordinator(self.second)
        self.scope["_shared_sensor_host_unloaded"](self.hass, "first")
        for key in self.scope["SHARED_SENSOR_KEYS"]:
            self.scope["_detach_shared_sensor"](self.data, key, self.first)
            self.assertNotIn(key, self.data)
        self.assertEqual(self.first.listeners, [])


if __name__ == "__main__":
    unittest.main()
