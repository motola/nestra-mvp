"""Bluetooth adapter — normalizes BLE sensors to unified Device model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device


class BluetoothAdapter:
    """Adapter for Bluetooth Low Energy sensor devices."""

    vendor = "bluetooth"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Scan for Bluetooth devices and normalize to Device objects.

        Mock implementation — returns empty list. Real implementation
        would scan BLE, parse advertisements, build Device objects.
        """
        # TODO: Scan for BLE devices, parse, build Device objects with create_device_data()
        return []

    async def fetch_state(self, device: Device) -> Device:
        """Refresh sensor state from Bluetooth device.

        Mock implementation — returns device unchanged.
        """
        # TODO: Read from BLE device
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
        """Execute command on Bluetooth device.

        Mock implementation — not supported for sensors.
        """
        return False
