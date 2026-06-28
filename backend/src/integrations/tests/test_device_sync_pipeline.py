"""Tests for device sync pipeline: factory, adapter, registry, sync, repository."""

import unittest
from typing import Any
from uuid import uuid4

from integrations.factory import create_device_data
from integrations.registry import AdapterRegistry, UnknownVendorError, create_registry
from property.domain import DeviceType


class MockAdapter:
    """Mock adapter for testing registry."""

    vendor: str = "mock"

    async def fetch_devices(
        self,
        *,
        organization_id: object,
        property_id: object,
        integration_id: object,
    ) -> list[object]:
        """Mock implementation."""
        return []

    async def fetch_state(self, device: object) -> object:
        """Mock implementation."""
        return device

    async def execute(self, device: object, command: str, params: dict[str, object]) -> bool:
        """Mock implementation."""
        return True


class TestDeviceFactory(unittest.TestCase):
    """Test create_device_data factory function."""

    def test_create_device_data_all_fields(self) -> None:
        """Factory builds device with all required fields."""
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        device = create_device_data(
            organization_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
            vendor="august",
            vendor_specific_id="lock-123",
            vendor_name="Front Door Lock",
            device_type=DeviceType.LOCK,
            online=True,
            raw_state={"is_locked": True},
        )

        self.assertIsNone(device.id)
        self.assertEqual(device.organization_id, org_id)
        self.assertEqual(device.property_id, prop_id)
        self.assertEqual(device.integration_id, int_id)
        self.assertEqual(device.vendor, "august")
        self.assertEqual(device.vendor_specific_id, "lock-123")
        self.assertEqual(device.vendor_name, "Front Door Lock")
        self.assertEqual(device.device_type, DeviceType.LOCK)
        self.assertTrue(device.online)
        self.assertEqual(device.raw_state, {"is_locked": True})
        self.assertIsNotNone(device.created_at)
        self.assertIsNotNone(device.updated_at)
        self.assertIsNotNone(device.last_sync)

    def test_create_device_data_empty_raw_state(self) -> None:
        """Factory defaults raw_state to empty dict."""
        device = create_device_data(
            organization_id=uuid4(),
            property_id=uuid4(),
            integration_id=uuid4(),
            vendor="bluetooth",
            vendor_specific_id="sensor-456",
            vendor_name=None,
            device_type=DeviceType.SENSOR,
            online=False,
        )

        self.assertEqual(device.raw_state, {})

    def test_create_device_data_timestamps_are_utc(self) -> None:
        """Factory timestamps are UTC-aware."""
        device = create_device_data(
            organization_id=uuid4(),
            property_id=uuid4(),
            integration_id=uuid4(),
            vendor="ecobee",
            vendor_specific_id="thermo-789",
            vendor_name=None,
            device_type=DeviceType.THERMOSTAT,
            online=True,
        )

        self.assertIsNotNone(device.created_at.tzinfo)
        self.assertIsNotNone(device.updated_at.tzinfo)
        self.assertIsNotNone(device.last_sync.tzinfo)


class TestAdapterRegistry(unittest.TestCase):
    """Test AdapterRegistry resolution."""

    def test_registry_resolve_existing_vendor(self) -> None:
        """Registry resolves registered vendor to adapter."""
        adapter: Any = MockAdapter()
        registry = AdapterRegistry({"mock": adapter})

        resolved = registry.resolve("mock")
        self.assertIs(resolved, adapter)

    def test_registry_resolve_unknown_vendor_raises(self) -> None:
        """Registry raises UnknownVendorError for unregistered vendor."""
        registry = AdapterRegistry({})

        with self.assertRaises(UnknownVendorError) as ctx:
            registry.resolve("unknown")

        self.assertIn("unknown", str(ctx.exception))

    def test_registry_case_sensitive(self) -> None:
        """Registry vendor lookup is case-sensitive."""
        adapter: Any = MockAdapter()
        registry = AdapterRegistry({"mock": adapter})

        with self.assertRaises(UnknownVendorError):
            registry.resolve("Mock")

    def test_create_registry_all_vendors(self) -> None:
        """create_registry factory initializes all 5 vendors."""
        registry = create_registry()

        for vendor in ("august", "bluetooth", "ecobee", "hikvision", "tplink"):
            adapter = registry.resolve(vendor)
            self.assertIsNotNone(adapter)
            self.assertEqual(adapter.vendor, vendor)

    def test_create_registry_vendors_distinct(self) -> None:
        """create_registry instantiates distinct adapter objects."""
        registry = create_registry()

        august = registry.resolve("august")
        bluetooth = registry.resolve("bluetooth")
        self.assertIsNot(august, bluetooth)


class TestIntegrationAdapterProtocol(unittest.TestCase):
    """Test that adapters conform to IntegrationAdapter protocol."""

    def test_adapter_has_vendor_attribute(self) -> None:
        """Each adapter has vendor attribute."""
        registry = create_registry()

        for vendor in ("august", "bluetooth", "ecobee", "hikvision", "tplink"):
            adapter = registry.resolve(vendor)
            self.assertTrue(hasattr(adapter, "vendor"))
            self.assertEqual(adapter.vendor, vendor)

    def test_adapter_has_required_methods(self) -> None:
        """Each adapter has required async methods."""
        registry = create_registry()

        for vendor in ("august", "bluetooth", "ecobee", "hikvision", "tplink"):
            adapter = registry.resolve(vendor)
            self.assertTrue(hasattr(adapter, "fetch_devices"))
            self.assertTrue(hasattr(adapter, "fetch_state"))
            self.assertTrue(hasattr(adapter, "execute"))


if __name__ == "__main__":
    unittest.main()
