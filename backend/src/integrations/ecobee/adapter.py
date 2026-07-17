"""Ecobee adapter — normalizes Ecobee thermostats to unified Device model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device


class EcobeeAdapter:
    """Adapter for Ecobee smart thermostat devices."""

    vendor = "ecobee"

    async def fetch_devices(
        self,
        *,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
    ) -> list[Device]:
        """Fetch Ecobee thermostats and normalize to Device objects.

        Mock implementation — returns empty list. Real implementation
        would call Ecobee API and parse thermostats.
        """
        # TODO: Call Ecobee API, parse thermostats, build Device objects with create_device_data()
        return []

    async def fetch_state(self, device: Device) -> Device:
        """Refresh thermostat state from Ecobee API.

        Mock implementation — returns device unchanged.
        """
        # TODO: Call Ecobee API to get thermostat state
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
        """Execute control command on Ecobee thermostat.

        Mock implementation — returns True for temperature commands.
        """
        return command in ("set_temperature", "set_mode")
