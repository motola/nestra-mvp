"""Meross adapter — normalizes Meross devices to unified Device model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device


class MerossAdapter:
    """Adapter for Meross devices."""

    vendor = "meross"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Fetch Meross devices and normalize to Device objects."""
        return [
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="meross",
                vendor_specific_id="meross_smart_plug_1",
                vendor_name="Meross Smart Plug",
                device_type="PLUG",
                online=True,
                raw_state={"on": True, "power": 12.5, "voltage": 230},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="meross",
                vendor_specific_id="meross_switch_1",
                vendor_name="Meross Smart Switch",
                device_type="SWITCH",
                online=True,
                raw_state={"on": False, "power": 0.0},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

    async def fetch_state(self, device: Device) -> Device:
        """Refresh device state from Meross API.

        Mock implementation — returns device unchanged.
        """
        # TODO: Call Meross API to get device state
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
        """Execute control command on Meross device.

        Mock implementation — returns True for basic commands.
        """
        return True
