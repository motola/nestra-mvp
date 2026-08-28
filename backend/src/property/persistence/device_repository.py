"""Device repository — the only place that persists devices."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import Device
from property.repository.models import DeviceModel

logger = logging.getLogger(__name__)


class DeviceRepository:
    """Persist and retrieve devices. Upsert is the only write method."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, incoming: Device) -> Device:
        """Insert or merge a device.

        Lookup by (vendor, vendor_specific_id). On insert, assign id.
        On update, preserve display_name, id, created_at, organization_id.
        Merge: vendor_name, device_type, online, raw_state, last_sync → update.
        """
        existing = await self._get_by_vendor_key(incoming.vendor, incoming.vendor_specific_id)

        if existing is None:
            incoming.id = uuid4()
            model = DeviceModel(
                id=incoming.id,
                organization_id=incoming.organization_id,
                property_id=incoming.property_id,
                integration_id=incoming.integration_id,
                vendor=incoming.vendor,
                vendor_specific_id=incoming.vendor_specific_id,
                vendor_name=incoming.vendor_name,
                device_type=incoming.device_type,
                online=incoming.online,
                raw_state=incoming.raw_state,
                last_sync=incoming.last_sync,
                created_at=incoming.created_at,
                updated_at=incoming.updated_at,
            )
            self._session.add(model)
            try:
                await self._session.flush()
            except ProgrammingError as e:
                logger.error(f"Failed to persist device - table may not exist: {e}")
                raise
            return incoming

        existing.vendor_name = incoming.vendor_name
        existing.device_type = incoming.device_type
        existing.online = incoming.online
        existing.raw_state = incoming.raw_state
        existing.last_sync = incoming.last_sync
        existing.updated_at = datetime.now(UTC)
        await self._session.flush()

        return Device(
            id=existing.id,
            organization_id=existing.organization_id,
            property_id=existing.property_id,
            integration_id=existing.integration_id,
            vendor=existing.vendor,
            vendor_specific_id=existing.vendor_specific_id,
            vendor_name=existing.vendor_name,
            device_type=existing.device_type,
            online=existing.online,
            raw_state=existing.raw_state,
            last_sync=existing.last_sync,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )

    async def get_by_id(self, device_id: UUID) -> Device | None:
        """Get a device by ID."""
        result = await self._session.execute(select(DeviceModel).where(DeviceModel.id == device_id))
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def find_by_id(self, device_id: UUID) -> Device | None:
        """Alias for get_by_id for compatibility."""
        return await self.get_by_id(device_id)

    async def find_by_property(self, property_id: UUID) -> list[Device]:
        """Get all devices for a property."""
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.property_id == property_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def _get_by_vendor_key(self, vendor: str, vendor_specific_id: str) -> DeviceModel | None:
        """O(1) lookup by (vendor, vendor_specific_id) index."""
        try:
            result = await self._session.execute(
                select(DeviceModel).where(
                    DeviceModel.vendor == vendor,
                    DeviceModel.vendor_specific_id == vendor_specific_id,
                )
            )
            return result.scalar_one_or_none()
        except ProgrammingError as e:
            logger.warning(f"Devices table not ready: {e} - treating as new device")
            return None

    @staticmethod
    def _model_to_domain(model: DeviceModel) -> Device:
        """Convert ORM model to domain model."""
        return Device(
            id=model.id,
            organization_id=model.organization_id,
            property_id=model.property_id,
            integration_id=model.integration_id,
            vendor=model.vendor,
            vendor_specific_id=model.vendor_specific_id,
            vendor_name=model.vendor_name,
            device_type=model.device_type,
            online=model.online,
            raw_state=model.raw_state,
            last_sync=model.last_sync,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
