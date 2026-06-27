"""Integration adapter pattern — normalizes vendor devices to AlphaconDevice."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID

from property.domain import Device, DeviceType


class IntegrationAdapter(ABC):
    """Base adapter for vendor-specific device integrations."""

    @property
    @abstractmethod
    def device_type(self) -> DeviceType:
        """The type of device this adapter handles."""

    @property
    @abstractmethod
    def vendor_name(self) -> str:
        """The vendor/integration name (e.g., 'August', 'Ecobee')."""

    @abstractmethod
    async def to_device(
        self,
        vendor_device: object,
        property_id: UUID,
        integration_id: UUID,
    ) -> Device:
        """Convert vendor-specific device to AlphaconDevice."""

    @abstractmethod
    async def execute_command(
        self, device: Device, command: str, params: dict[str, object]
    ) -> bool:
        """Execute a command on the device (lock, set_temp, toggle, etc)."""

    def _build_device(
        self,
        device_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        name: str,
        vendor_specific_id: str,
        online: bool,
        raw_state: dict[str, object],
    ) -> Device:
        """Helper to build Device from common fields."""
        now = datetime.now(UTC)
        return Device(
            id=device_id,
            property_id=property_id,
            integration_id=integration_id,
            device_type=self.device_type,
            name=name,
            vendor_specific_id=vendor_specific_id,
            online=online,
            last_sync=now,
            created_at=now,
            updated_at=now,
            raw_state=raw_state,
        )
