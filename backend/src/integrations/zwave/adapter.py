"""Z-Wave adapter — normalizes Z-Wave devices to unified Device model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device


class ZwaveAdapter:
    """Adapter for Z-Wave devices."""

    vendor = "zwave"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Fetch Z-Wave devices and normalize to Device objects.

        Mock implementation — returns empty list. Real implementation
        would call Z-Wave API and parse devices.
        """
        # TODO: Call Z-Wave API, parse devices, build Device objects with create_device_data()
        return []

    async def fetch_state(self, device: Device) -> Device:
        """Refresh device state from Z-Wave API.

        Mock implementation — returns device unchanged.
        """
        # TODO: Call Z-Wave API to get device state
        return Device(
            id=device.id,
            organization_id=device.organization_id,
            portfolio_id=device.portfolio_id,
            property_id=device.property_id,
            integration_id=device.integration_id,
            vendor=device.vendor,
            vendor_specific_id=device.vendor_specific_id,
            vendor_name=device.vendor_name,
            device_type=device.device_type,
            online=device.online,
            raw_state=device.raw_state,
            last_sync=datetime.now(UTC),
            created_at=device.created_at,
            updated_at=datetime.now(UTC),
        )

    async def execute(self, device: Device, command: str, params: dict[str, object]) -> bool:
        """Execute control command on Z-Wave device.

        Mock implementation — returns True for basic commands.
        """
        return True
