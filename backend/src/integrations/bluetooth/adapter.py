"""Bluetooth adapter — normalizes BLE sensors to unified Device model."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from property.domain import Device

logger = logging.getLogger(__name__)


class BluetoothAdapter:
    """Adapter for Bluetooth Low Energy sensor devices."""

    vendor = "bluetooth"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        _credentials: str | None = None,
    ) -> list[Device]:
        """Scan for Bluetooth devices and normalize to Device objects.

        Mock implementation — returns mock BLE sensors for testing.
        """
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

    async def fetch_state(self, device: Device, _credentials: str | None = None) -> Device:
        """Refresh sensor state from Bluetooth device.

        Mock implementation — returns device unchanged.
        """
        device.updated_at = datetime.now(UTC)
        return device

    async def execute(
        self, device: Device, command: str, params: dict[str, Any], _credentials: str | None = None
    ) -> bool:
        """Execute command on Bluetooth device.

        Not supported for sensors.
        """
        return False
