import unittest
from uuid import uuid4

from config import get_settings


class TestTPlinkPlugs(unittest.TestCase):
    """Test TP-Link Smart Plug operations."""

    def setUp(self) -> None:
        """Clear mock storage."""
        import integrations.tplink.routes as routes

        routes._MOCK_PLUGS.clear()
        routes._MOCK_INTEGRATIONS.clear()
        self.settings = get_settings()

    def test_add_plug_success(self) -> None:
        """Test adding a plug."""
        import asyncio

        from integrations.tplink.routes import add_plug
        from integrations.tplink.schemas import TPlinkPlugIn

        plug_in = TPlinkPlugIn(
            device_id="tplink_123",
            name="Bedroom Outlet",
            property_id=uuid4(),
        )

        result = asyncio.run(add_plug(plug_in, self.settings))

        self.assertIsNotNone(result.id)
        self.assertEqual(result.name, "Bedroom Outlet")
        self.assertTrue(result.is_online)

    def test_set_power_state(self) -> None:
        """Test turning plug on/off."""
        import asyncio

        from integrations.tplink.routes import add_plug, set_power_state
        from integrations.tplink.schemas import TPlinkPlugIn, TPlinkPowerStateUpdate

        plug_in = TPlinkPlugIn(
            device_id="tplink_123",
            name="Bedroom Outlet",
            property_id=uuid4(),
        )

        added = asyncio.run(add_plug(plug_in, self.settings))
        result = asyncio.run(
            set_power_state(
                added.id,
                TPlinkPowerStateUpdate(device_id=added.id, power_state=True),
                self.settings,
            )
        )

        self.assertEqual(result.status, "success")
        self.assertIn("ON", result.message)

    def test_list_plugs(self) -> None:
        """Test listing plugs."""
        import asyncio

        from integrations.tplink.routes import add_plug, list_plugs
        from integrations.tplink.schemas import TPlinkPlugIn

        prop_id = uuid4()
        plug_in = TPlinkPlugIn(
            device_id="tplink_123",
            name="Bedroom Outlet",
            property_id=prop_id,
        )

        asyncio.run(add_plug(plug_in, self.settings))
        plugs = asyncio.run(list_plugs(prop_id, self.settings))

        self.assertEqual(len(plugs), 1)


if __name__ == "__main__":
    unittest.main()
