from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from demo import govee_ble


class TestPacket(unittest.TestCase):
    def test_power_on_checksum(self) -> None:
        pkt = govee_ble._packet(0x01, [0x01])
        self.assertEqual(len(pkt), 20)
        xor = 0
        for b in pkt[:-1]:
            xor ^= b
        self.assertEqual(pkt[-1], xor)

    def test_power_off_checksum(self) -> None:
        pkt = govee_ble._packet(0x01, [0x00])
        self.assertEqual(len(pkt), 20)
        xor = 0
        for b in pkt[:-1]:
            xor ^= b
        self.assertEqual(pkt[-1], xor)

    def test_power_on_payload(self) -> None:
        pkt = govee_ble._packet(0x01, [0x01])
        self.assertEqual(pkt[0], 0x33)
        self.assertEqual(pkt[1], 0x01)
        self.assertEqual(pkt[2], 0x01)

    def test_power_off_payload(self) -> None:
        pkt = govee_ble._packet(0x01, [0x00])
        self.assertEqual(pkt[0], 0x33)
        self.assertEqual(pkt[1], 0x01)
        self.assertEqual(pkt[2], 0x00)


def _settings_no_ble() -> MagicMock:
    s = MagicMock()
    s.govee_ble_address = ""
    return s


class TestListDevices(unittest.IsolatedAsyncioTestCase):
    async def test_filters_h617c_only(self) -> None:
        govee_ble._cache = []
        govee_ble._cache_time = 0.0

        mock_h617c = MagicMock()
        mock_h617c.name = "ihoment_H617C_1234"
        mock_h617c.address = "AA:BB:CC:DD:EE:FF"

        mock_other = MagicMock()
        mock_other.name = "SomeOtherDevice"
        mock_other.address = "11:22:33:44:55:66"

        mock_discover = AsyncMock(return_value=[mock_h617c, mock_other])
        with (
            patch("demo.govee_ble.get_settings", return_value=_settings_no_ble()),
            patch("demo.govee_ble.BleakScanner.discover", new=mock_discover),
        ):
            devices = await govee_ble.list_devices()

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["device"], "AA:BB:CC:DD:EE:FF")
        self.assertEqual(devices[0]["model"], "ble")

    async def test_returns_cached_result(self) -> None:
        govee_ble._cache = [{"device": "cached", "model": "ble"}]
        govee_ble._cache_time = 9999999999.0

        mock_discover = AsyncMock(return_value=[])
        with (
            patch("demo.govee_ble.get_settings", return_value=_settings_no_ble()),
            patch("demo.govee_ble.BleakScanner.discover", new=mock_discover) as mock_scan,
        ):
            devices = await govee_ble.list_devices()

        mock_scan.assert_not_awaited()
        self.assertEqual(devices[0]["device"], "cached")


if __name__ == "__main__":
    unittest.main()
