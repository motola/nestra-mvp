import unittest
from uuid import uuid4

from config import get_settings


class TestEcobeeThermostats(unittest.TestCase):
    """Test Ecobee Thermostat operations."""

    def setUp(self) -> None:
        """Clear mock storage before each test."""
        import integrations.ecobee.routes as routes

        routes._MOCK_DEVICES.clear()
        routes._MOCK_INTEGRATIONS.clear()
        self.settings = get_settings()

    def test_add_thermostat_success(self) -> None:
        """Test successfully adding an Ecobee Thermostat."""
        import asyncio

        from integrations.ecobee.routes import add_thermostat
        from integrations.ecobee.schemas import EcobeeDeviceIn

        device_in = EcobeeDeviceIn(
            device_id="ecobee_123",
            name="Main Floor",
            property_id=uuid4(),
            current_temperature=72.0,
            target_temperature=70.0,
            mode="auto",
            humidity=45,
        )

        result = asyncio.run(add_thermostat(device_in, self.settings))

        self.assertIsNotNone(result.id)
        self.assertEqual(result.name, "Main Floor")
        self.assertEqual(result.target_temperature, 70.0)
        self.assertEqual(result.mode, "auto")

    def test_set_temperature_success(self) -> None:
        """Test setting thermostat temperature."""
        import asyncio

        from integrations.ecobee.routes import add_thermostat, set_temperature
        from integrations.ecobee.schemas import EcobeeDeviceIn, EcobeeTemperatureUpdate

        device_in = EcobeeDeviceIn(
            device_id="ecobee_123",
            name="Main Floor",
            property_id=uuid4(),
            current_temperature=72.0,
            target_temperature=70.0,
        )

        added = asyncio.run(add_thermostat(device_in, self.settings))
        result = asyncio.run(
            set_temperature(
                added.id,
                EcobeeTemperatureUpdate(device_id=added.id, target_temperature=68.0),
                self.settings,
            )
        )

        self.assertEqual(result.status, "success")
        self.assertIn("68", result.message)

    def test_list_thermostats(self) -> None:
        """Test listing thermostats."""
        import asyncio

        from integrations.ecobee.routes import add_thermostat, list_thermostats
        from integrations.ecobee.schemas import EcobeeDeviceIn

        prop_id = uuid4()
        device_in = EcobeeDeviceIn(
            device_id="ecobee_123",
            name="Main Floor",
            property_id=prop_id,
            current_temperature=72.0,
            target_temperature=70.0,
        )

        asyncio.run(add_thermostat(device_in, self.settings))
        devices = asyncio.run(list_thermostats(prop_id, self.settings))

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].name, "Main Floor")


if __name__ == "__main__":
    unittest.main()
