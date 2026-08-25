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
        """Scan for Bluetooth devices and normalize to Device objects."""
        return [
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="bluetooth",
                vendor_specific_id="ble_sensor_temp_1",
                vendor_name="BLE Temperature Sensor",
                device_type="SENSOR",
                online=True,
                raw_state={"temperature": 21.3, "battery": 85},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Device(
                id=None,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
                vendor="bluetooth",
                vendor_specific_id="ble_sensor_contact_1",
                vendor_name="BLE Door Contact Sensor",
                device_type="SENSOR",
                online=True,
                raw_state={"state": "closed", "battery": 95},
                last_sync=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

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
