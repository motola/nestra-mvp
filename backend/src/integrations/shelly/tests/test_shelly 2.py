"""Unit tests for Shelly integration."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from integrations.shelly.adapter import ShellyAdapter
from property.domain import DeviceType


class TestShellyAdapter:
    """Test ShellyAdapter functionality."""

    def test_get_device_type_mapping(self) -> None:
        """Test that device types are correctly mapped."""
        adapter = ShellyAdapter()

        assert adapter._get_device_type("SHSW-1") == DeviceType.PLUG
        assert adapter._get_device_type("SHBLB-1") == DeviceType.LIGHT
        assert adapter._get_device_type("SHHT-1") == DeviceType.SENSOR
        assert adapter._get_device_type("Unknown") == DeviceType.PLUG

    @pytest.mark.asyncio  # type: ignore[untyped-decorator]
    async def test_fetch_devices_without_auth_token(self) -> None:
        """Test fetch_devices returns mock devices when no auth token provided."""
        adapter = ShellyAdapter()
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        devices = await adapter.fetch_devices(
            organization_id=UUID("00000000-0000-0000-0000-000000000001"),
            portfolio_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
            auth_token=None,
        )

        assert len(devices) > 0
        assert all(d.vendor == "shelly" for d in devices)
        assert all(d.organization_id == org_id for d in devices)
        assert all(d.property_id == prop_id for d in devices)

    @pytest.mark.asyncio  # type: ignore[untyped-decorator]
    async def test_fetch_devices_preserves_organization_id(self) -> None:
        """Test that fetch_devices preserves organization_id in devices."""
        adapter = ShellyAdapter()
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        devices = await adapter.fetch_devices(
            organization_id=UUID("00000000-0000-0000-0000-000000000001"),
            portfolio_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
        )

        for device in devices:
            assert device.organization_id == org_id
            assert device.property_id == prop_id
            assert device.integration_id == int_id

    @pytest.mark.asyncio  # type: ignore[untyped-decorator]
    async def test_fetch_devices_mock_returns_valid_devices(self) -> None:
        """Test that mock devices have all required fields."""
        adapter = ShellyAdapter()
        org_id = uuid4()
        prop_id = uuid4()
        int_id = uuid4()

        devices = await adapter.fetch_devices(
            organization_id=UUID("00000000-0000-0000-0000-000000000001"),
            portfolio_id=org_id,
            property_id=prop_id,
            integration_id=int_id,
        )

        for device in devices:
            assert device.vendor_name is not None
            assert device.vendor_specific_id is not None
            assert device.device_type is not None
            assert device.last_sync is not None
            assert device.created_at is not None
