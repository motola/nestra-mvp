"""Unit tests for Govee integration."""

from __future__ import annotations

from uuid import uuid4

import pytest

from integrations.govee.adapter import GoveeAdapter
from property.domain import DeviceType


class TestGoveeAdapter:
    """Test GoveeAdapter functionality."""

    def test_get_device_type_mapping(self) -> None:
        """Test that device types are correctly mapped."""
        adapter = GoveeAdapter()

        assert adapter._get_device_type("SmartPlug") == DeviceType.PLUG
        assert adapter._get_device_type("Light") == DeviceType.LIGHT
        assert adapter._get_device_type("Sensor") == DeviceType.SENSOR
        assert adapter._get_device_type("Switch") == DeviceType.PLUG
        assert adapter._get_device_type("Unknown") == DeviceType.PLUG

    @pytest.mark.asyncio
    async def test_fetch_devices_without_api_key(self) -> None:
        """Test fetch_devices returns mock devices when no API key provided."""
        adapter = GoveeAdapter()
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        devices = await adapter.fetch_devices(
            organization_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
            api_key=None,
        )

        assert len(devices) > 0
        assert all(d.vendor == "govee" for d in devices)
        assert all(d.organization_id == org_id for d in devices)
        assert all(d.property_id == prop_id for d in devices)

    @pytest.mark.asyncio
    async def test_fetch_devices_preserves_organization_id(self) -> None:
        """Test that fetch_devices preserves organization_id in devices."""
        adapter = GoveeAdapter()
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        devices = await adapter.fetch_devices(
            organization_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
        )

        for device in devices:
            assert device.organization_id == org_id
            assert device.property_id == prop_id
            assert device.integration_id == int_id

    @pytest.mark.asyncio
    async def test_fetch_devices_mock_returns_valid_devices(self) -> None:
        """Test that mock devices have all required fields."""
        adapter = GoveeAdapter()
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        devices = await adapter.fetch_devices(
            organization_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
        )

        for device in devices:
            assert device.vendor_name is not None
            assert device.vendor_specific_id is not None
            assert device.device_type is not None
            assert device.last_sync is not None
            assert device.created_at is not None
