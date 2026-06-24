import unittest
from uuid import uuid4

from config import get_settings


class TestBluetoothPairing(unittest.TestCase):
    """Test Bluetooth device pairing and unpairing."""

    def setUp(self) -> None:
        """Clear mock storage before each test."""
        # Import here to get fresh state
        import property.integrations.bluetooth.routes as routes

        routes._MOCK_DEVICES.clear()
        routes._MOCK_INTEGRATIONS.clear()
        self.settings = get_settings()

    def test_pair_device_success(self) -> None:
        """Test successfully pairing a new Bluetooth device."""
        import asyncio

        from property.integrations.bluetooth.routes import pair_device
        from property.integrations.bluetooth.schemas import BluetoothDeviceIn

        device_in = BluetoothDeviceIn(
            mac_address="AA:BB:CC:DD:EE:FF",
            name="Test Light",
            property_id=uuid4(),
            device_type="light",
            rssi=-45,
        )

        result = asyncio.run(pair_device(device_in, self.settings))

        self.assertIsNotNone(result.device_id)
        self.assertEqual(result.status, "paired")
        self.assertIn("success", result.message.lower())

    def test_pair_duplicate_device_fails(self) -> None:
        """Test that pairing same MAC twice fails."""
        import asyncio

        from fastapi import HTTPException

        from property.integrations.bluetooth.routes import pair_device
        from property.integrations.bluetooth.schemas import BluetoothDeviceIn

        mac = "AA:BB:CC:DD:EE:FF"
        device_in = BluetoothDeviceIn(
            mac_address=mac,
            name="Test Light",
            property_id=uuid4(),
            device_type="light",
        )

        asyncio.run(pair_device(device_in, self.settings))

        # Try to pair same device again
        with self.assertRaises(HTTPException) as context:
            asyncio.run(pair_device(device_in, self.settings))

        self.assertEqual(context.exception.status_code, 409)  # Conflict

    def test_unpair_device_success(self) -> None:
        """Test successfully unpairing a device."""
        import asyncio

        from property.integrations.bluetooth.routes import pair_device, unpair_device
        from property.integrations.bluetooth.schemas import BluetoothDeviceIn

        device_in = BluetoothDeviceIn(
            mac_address="AA:BB:CC:DD:EE:FF",
            name="Test Light",
            property_id=uuid4(),
        )

        pair_result = asyncio.run(pair_device(device_in, self.settings))
        device_id = pair_result.device_id

        unpair_result = asyncio.run(unpair_device(device_id, self.settings))

        self.assertEqual(unpair_result.status, "unpaired")

    def test_unpair_nonexistent_device_fails(self) -> None:
        """Test that unpairing a nonexistent device fails."""
        import asyncio

        from fastapi import HTTPException

        from property.integrations.bluetooth.routes import unpair_device

        with self.assertRaises(HTTPException) as context:
            asyncio.run(unpair_device(uuid4(), self.settings))

        self.assertEqual(context.exception.status_code, 404)

    def test_list_devices_empty(self) -> None:
        """Test listing devices when none are paired."""
        import asyncio

        from property.integrations.bluetooth.routes import list_devices

        devices = asyncio.run(list_devices(None, self.settings))

        self.assertEqual(len(devices), 0)

    def test_list_devices_filters_by_property(self) -> None:
        """Test that list_devices filters by property_id when provided."""
        import asyncio

        from property.integrations.bluetooth.routes import list_devices, pair_device
        from property.integrations.bluetooth.schemas import BluetoothDeviceIn

        property_id_1 = uuid4()
        property_id_2 = uuid4()

        device1 = BluetoothDeviceIn(
            mac_address="AA:BB:CC:DD:EE:01",
            name="Light 1",
            property_id=property_id_1,
        )
        device2 = BluetoothDeviceIn(
            mac_address="AA:BB:CC:DD:EE:02",
            name="Light 2",
            property_id=property_id_2,
        )

        asyncio.run(pair_device(device1, self.settings))
        asyncio.run(pair_device(device2, self.settings))

        all_devices = asyncio.run(list_devices(None, self.settings))
        self.assertEqual(len(all_devices), 2)

        devices_p1 = asyncio.run(list_devices(property_id_1, self.settings))
        self.assertEqual(len(devices_p1), 1)
        self.assertEqual(devices_p1[0].property_id, property_id_1)

    def test_paired_device_has_valid_data(self) -> None:
        """Test that paired device contains all expected fields."""
        import asyncio

        from property.integrations.bluetooth.routes import list_devices, pair_device
        from property.integrations.bluetooth.schemas import BluetoothDeviceIn

        property_id = uuid4()
        device_in = BluetoothDeviceIn(
            mac_address="AA:BB:CC:DD:EE:FF",
            name="Test Sensor",
            property_id=property_id,
            device_type="sensor",
            rssi=-55,
            battery_level=85,
        )

        asyncio.run(pair_device(device_in, self.settings))
        devices = asyncio.run(list_devices(property_id, self.settings))

        self.assertEqual(len(devices), 1)
        device = devices[0]
        self.assertEqual(device.mac_address, "AA:BB:CC:DD:EE:FF")
        self.assertEqual(device.name, "Test Sensor")
        self.assertEqual(device.device_type, "sensor")
        self.assertEqual(device.rssi, -55)
        self.assertEqual(device.battery_level, 85)
        self.assertTrue(device.is_paired)


class TestBluetoothIntegration(unittest.TestCase):
    """Integration tests for Bluetooth feature."""

    def setUp(self) -> None:
        import property.integrations.bluetooth.routes as routes

        routes._MOCK_DEVICES.clear()
        routes._MOCK_INTEGRATIONS.clear()
        self.settings = get_settings()

    def test_full_pairing_workflow(self) -> None:
        """Test complete: discover → pair → list → unpair."""
        import asyncio

        from property.integrations.bluetooth.routes import list_devices, pair_device, unpair_device
        from property.integrations.bluetooth.schemas import BluetoothDeviceIn

        property_id = uuid4()

        macs = ["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02", "AA:BB:CC:DD:EE:03"]
        device_ids = []

        for i, mac in enumerate(macs):
            device_in = BluetoothDeviceIn(
                mac_address=mac,
                name=f"Device {i + 1}",
                property_id=property_id,
            )
            result = asyncio.run(pair_device(device_in, self.settings))
            device_ids.append(result.device_id)

        devices = asyncio.run(list_devices(property_id, self.settings))
        self.assertEqual(len(devices), 3)

        asyncio.run(unpair_device(device_ids[0], self.settings))

        devices = asyncio.run(list_devices(property_id, self.settings))
        self.assertEqual(len(devices), 2)

        remaining_macs = {d.mac_address for d in devices}
        self.assertNotIn(macs[0], remaining_macs)
        self.assertIn(macs[1], remaining_macs)
        self.assertIn(macs[2], remaining_macs)


if __name__ == "__main__":
    unittest.main()
