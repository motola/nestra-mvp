"""Tests for the devices API response contracts and extracted helpers."""

from __future__ import annotations

import unittest

from api.v1.devices import _read_cluster_attr
from devices.schemas import DeleteResult, DeviceCommandResult, MatterDeviceState


class DeviceSchemasTest(unittest.TestCase):
    def test_command_result_shape(self) -> None:
        result = DeviceCommandResult(success=True, state=False)
        self.assertEqual(result.model_dump(), {"success": True, "state": False})

    def test_matter_state_defaults_attributes_to_none(self) -> None:
        state = MatterDeviceState(device_id="d1", node_id="n1", online=True)
        self.assertIsNone(state.on_off)
        self.assertIsNone(state.brightness)

    def test_matter_state_full_shape(self) -> None:
        state = MatterDeviceState(
            device_id="d1", node_id="n1", online=True, on_off=True, brightness=200
        )
        self.assertEqual(
            state.model_dump(),
            {
                "device_id": "d1",
                "node_id": "n1",
                "online": True,
                "on_off": True,
                "brightness": 200,
            },
        )

    def test_delete_result_shape(self) -> None:
        self.assertEqual(DeleteResult(deleted="d1").model_dump(), {"deleted": "d1"})


class MatterAttrReaderTest(unittest.TestCase):
    def test_reads_named_attribute_on_endpoint_1(self) -> None:
        attrs = {"1": {"6": {"OnOff": True}}}
        self.assertTrue(_read_cluster_attr(attrs, "6", "OnOff"))

    def test_falls_back_to_index_zero(self) -> None:
        attrs = {"1": {"8": {"0": 128}}}
        self.assertEqual(_read_cluster_attr(attrs, "8", "CurrentLevel"), 128)

    def test_missing_cluster_returns_none(self) -> None:
        self.assertIsNone(_read_cluster_attr({}, "6", "OnOff"))


if __name__ == "__main__":
    unittest.main()
