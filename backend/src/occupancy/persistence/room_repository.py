"""Room repository — persistence and retrieval of rooms."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from occupancy.domain import Room
from occupancy.repository.models import RoomModel

logger = logging.getLogger(__name__)


class RoomRepository:
    """Persist and retrieve rooms."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, room_id: UUID) -> Room | None:
        """Get a room by ID."""
        result = await self._session.execute(select(RoomModel).where(RoomModel.id == room_id))
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, room: Room) -> Room:
        """Create a new room."""
        now = datetime.now(UTC)
        model = RoomModel(
            id=room.id,
            property_id=room.property_id,
            name=room.name,
            room_type=room.room_type,
            floor_number=room.floor_number,
            square_feet=room.square_feet,
            description=room.description,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_property(self, property_id: UUID) -> list[Room]:
        """Get all rooms for a property."""
        result = await self._session.execute(
            select(RoomModel).where(RoomModel.property_id == property_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def update(self, room: Room) -> Room:
        """Update an existing room."""
        result = await self._session.execute(select(RoomModel).where(RoomModel.id == room.id))
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Room {room.id} not found")

        model.name = room.name
        model.room_type = room.room_type
        model.floor_number = room.floor_number
        model.square_feet = room.square_feet
        model.description = room.description
        model.updated_at = datetime.now(UTC)

        await self._session.flush()
        return self._model_to_domain(model)

    @staticmethod
    def _model_to_domain(model: RoomModel) -> Room:
        """Convert ORM model to domain model."""
        return Room(
            id=model.id,
            property_id=model.property_id,
            name=model.name,
            room_type=model.room_type,
            floor_number=model.floor_number,
            square_feet=model.square_feet,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
