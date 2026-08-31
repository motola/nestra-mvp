"""Device state synchronization — query device state and update local records."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import Device
from property.persistence.device_repository import DeviceRepository

logger = logging.getLogger(__name__)


class DeviceStateSynchronizer:
    """Synchronize device state with local database."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._device_repo = DeviceRepository(session)

    async def sync_device_state(
        self,
        device_id: UUID,
        integration_id: UUID,
    ) -> Device | None:
        """Sync a single device's state.

        Queries the device via its integration and updates local state.

        Args:
            device_id: ID of device to sync
            integration_id: Integration to use for sync

        Returns:
            Updated Device or None if not found
        """
        # TODO: Query device state via integration API
        # For now, just update last_sync timestamp
        device = await self._device_repo.get_by_id(device_id)
        if not device:
            return None

        device.last_sync = datetime.now(UTC)
        device.updated_at = datetime.now(UTC)

        # Upsert to update
        return await self._device_repo.upsert(device)

    async def update_device_state(
        self,
        device_id: UUID,
        state_data: dict[str, object],
    ) -> Device | None:
        """Update local device state.

        Args:
            device_id: ID of device to update
            state_data: New state data

        Returns:
            Updated Device or None if not found
        """
        device = await self._device_repo.get_by_id(device_id)
        if not device:
            return None

        device.raw_state = state_data
        device.last_sync = datetime.now(UTC)
        device.updated_at = datetime.now(UTC)

        return await self._device_repo.upsert(device)

    async def sync_all_devices(
        self,
        property_id: UUID,
    ) -> list[Device]:
        """Sync all devices in a property.

        Args:
            property_id: Property to sync devices for

        Returns:
            List of updated Devices
        """
        # TODO: Query all devices for property and sync via integrations
        # For now, return empty list
        return []
