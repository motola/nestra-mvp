from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from demo.ble_general import detect_type, scan


class TestDetectType(unittest.TestCase):
    def test_govee_is_light(self) -> None:
        self.assertEqual(detect_type("Govee_H617C_475E"), "light")

    def test_ihoment_is_light(self) -> None:
        self.assertEqual(detect_type("ihoment_H6008_1234"), "light")

    def test_jbl_is_speaker(self) -> None:
        self.assertEqual(detect_type("JBL Flip 6"), "speaker")

    def test_bose_is_speaker(self) -> None:
        self.assertEqual(detect_type("Bose SoundLink Mini II"), "speaker")

    def test_iphone_is_phone(self) -> None:
        self.assertEqual(detect_type("Akinola's iPhone"), "phone")

    def test_unknown_device(self) -> None:
        self.assertEqual(detect_type("TY"), "unknown")

    def test_none_name(self) -> None:
        self.assertEqual(detect_type(None), "unknown")

    def test_case_insensitive(self) -> None:
        self.assertEqual(detect_type("SONY WH-1000XM5"), "speaker")


class TestScan(unittest.IsolatedAsyncioTestCase):
    async def test_filters_unnamed_devices(self) -> None:
        named = MagicMock()
        named.name = "Govee_H617C_475E"
        named.address = "AA:BB:CC:DD:EE:FF"

        unnamed = MagicMock()
        unnamed.name = None
        unnamed.address = "11:22:33:44:55:66"

        mock_discover = AsyncMock(return_value=[named, unnamed])
        with patch("demo.ble_general.BleakScanner.discover", new=mock_discover):
            results = await scan()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Govee_H617C_475E")
        self.assertEqual(results[0].device_type, "light")

    async def test_filters_ghost_devices_below_rssi_floor(self) -> None:
        strong = MagicMock()
        strong.name = "Govee_H617C_475E"
        strong.address = "AA:BB:CC:DD:EE:FF"
        strong.rssi = -55

        ghost = MagicMock()
        ghost.name = "Mystery Device"
        ghost.address = "11:22:33:44:55:66"
        ghost.rssi = -95

        mock_discover = AsyncMock(return_value=[strong, ghost])
        with patch("demo.ble_general.BleakScanner.discover", new=mock_discover):
            results = await scan()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].address, "AA:BB:CC:DD:EE:FF")

    async def test_returns_correct_types(self) -> None:
        govee = MagicMock()
        govee.name = "Govee_H617C"
        govee.address = "AA:00:00:00:00:01"

        jbl = MagicMock()
        jbl.name = "JBL Charge 5"
        jbl.address = "AA:00:00:00:00:02"

        mock_discover = AsyncMock(return_value=[govee, jbl])
        with patch("demo.ble_general.BleakScanner.discover", new=mock_discover):
            results = await scan()

        types = {r.name: r.device_type for r in results}
        self.assertEqual(types["Govee_H617C"], "light")
        self.assertEqual(types["JBL Charge 5"], "speaker")


if __name__ == "__main__":
    unittest.main()
