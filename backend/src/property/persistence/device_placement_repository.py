"""Device placement repository — persistence and retrieval of device placements."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import DevicePlacement
from property.repository.models import DevicePlacementModel

logger = logging.getLogger(__name__)


class DevicePlacementRepository:
    """Persist and retrieve device placements."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_device_id(self, device_id: UUID) -> DevicePlacement | None:
        """Get device placement by device ID."""
        result = await self._session.execute(
            select(DevicePlacementModel).where(DevicePlacementModel.device_id == device_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def get_by_id(self, placement_id: UUID) -> DevicePlacement | None:
        """Get a device placement by ID."""
        result = await self._session.execute(
            select(DevicePlacementModel).where(DevicePlacementModel.id == placement_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, placement: DevicePlacement) -> DevicePlacement:
        """Create a new device placement."""
        now = datetime.now(UTC)
        model = DevicePlacementModel(
            id=placement.id,
            device_id=placement.device_id,
            property_id=placement.property_id,
            room_id=placement.room_id,
            placement_type=placement.placement_type,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def update_placement(self, placement: DevicePlacement) -> DevicePlacement:
        """Update an existing device placement."""
        result = await self._session.execute(
            select(DevicePlacementModel).where(
                DevicePlacementModel.device_id == placement.device_id
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Placement for device {placement.device_id} not found")

        model.property_id = placement.property_id
        model.room_id = placement.room_id
        model.placement_type = placement.placement_type
        model.updated_at = datetime.now(UTC)

        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_property(self, property_id: UUID) -> list[DevicePlacement]:
        """Get all device placements for a property."""
        result = await self._session.execute(
            select(DevicePlacementModel).where(DevicePlacementModel.property_id == property_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_room(self, room_id: UUID) -> list[DevicePlacement]:
        """Get all device placements for a room."""
        result = await self._session.execute(
            select(DevicePlacementModel).where(DevicePlacementModel.room_id == room_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    @staticmethod
    def _model_to_domain(model: DevicePlacementModel) -> DevicePlacement:
        """Convert ORM model to domain model."""
        return DevicePlacement(
            id=model.id,
            device_id=model.device_id,
            property_id=model.property_id,
            room_id=model.room_id,
            placement_type=model.placement_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
