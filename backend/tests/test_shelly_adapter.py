"""Unit tests for the Shelly local adapter (mocked — no device required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_ROOT / "src"))

from integrations.shelly.adapter import ShellyAdapter, to_spire_device  # noqa: E402
from spire import VendorAdapter  # noqa: E402

_STATE = {"on": True, "power": 42.0, "voltage": 238.0, "current": 0.18, "energy": 1.2}


class TestNormaliser(unittest.TestCase):
    def test_maps_state_to_device(self) -> None:
        device = to_spire_device(
            device_id="d1", vendor_id="192.168.0.5", name="Boiler Plug", state=_STATE
        )
        api = device.to_api()
        self.assertEqual(api["vendor"], "shelly")
        self.assertEqual(api["type"], "plug")
        self.assertTrue(device.online)
        self.assertTrue(api["state"]["on"])
        self.assertEqual(api["power_draw"], 42.0)
        self.assertIn("turn_on", api["supported_commands"])


class TestShellyAdapter(unittest.IsolatedAsyncioTestCase):
    def test_conforms_to_base_adapter(self) -> None:
        self.assertIsInstance(ShellyAdapter({}), VendorAdapter)

    async def test_send_command_routes_to_controller(self) -> None:
        with patch("integrations.shelly.adapter.ShellyController") as mock_ctrl:
            inst = mock_ctrl.return_value
            inst.turn_on = AsyncMock(return_value=True)
            inst.turn_off = AsyncMock(return_value=True)
            adapter = ShellyAdapter({"d1": "192.168.0.5"})

            self.assertTrue(await adapter.send_command("d1", {"action": "turn_on"}))
            inst.turn_on.assert_awaited_once()
            self.assertTrue(await adapter.send_command("d1", {"action": "turn_off"}))
            self.assertFalse(await adapter.send_command("d1", {"action": "nope"}))

    async def test_get_device_state_normalises(self) -> None:
        with patch("integrations.shelly.adapter.ShellyController") as mock_ctrl:
            mock_ctrl.return_value.get_state = AsyncMock(return_value=_STATE)
            adapter = ShellyAdapter({"d1": "10.0.0.9"}, names={"d1": "Boiler Plug"})

            device = await adapter.get_device_state("d1")
            api = device.to_api()
            self.assertEqual(api["name"], "Boiler Plug")
            self.assertEqual(api["power_draw"], 42.0)

    async def test_list_devices_marks_unreachable_offline(self) -> None:
        with patch("integrations.shelly.adapter.ShellyController") as mock_ctrl:
            mock_ctrl.return_value.get_state = AsyncMock(side_effect=OSError("no route"))
            adapter = ShellyAdapter({"d1": "10.0.0.9"})

            devices = await adapter.list_devices()
            self.assertEqual(len(devices), 1)
            self.assertFalse(devices[0].online)


if __name__ == "__main__":
    unittest.main()
