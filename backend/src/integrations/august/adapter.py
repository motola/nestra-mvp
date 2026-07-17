"""August Smart Locks adapter — normalizes August locks to unified Device model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device


class AugustAdapter:
    """Adapter for August Smart Lock devices."""

    vendor = "august"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Fetch August locks from API and normalize to Device objects.

        Mock implementation — returns empty list. Real implementation
        would call August API and parse response.
        """
        # TODO: Call August API, parse locks, build Device objects with create_device_data()
        return []

    async def fetch_state(self, device: Device) -> Device:
        """Refresh device state from August API.

        Mock implementation — returns device unchanged.
        """
        # TODO: Call August API to get lock state
        return Device(
            id=device.id,
            organization_id=device.organization_id,
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
        """Execute lock/unlock command on August lock.

        Mock implementation — returns True for lock/unlock commands.
        """
        return command in ("lock", "unlock")
