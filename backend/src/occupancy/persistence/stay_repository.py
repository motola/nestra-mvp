"""Stay repository — persistence and retrieval of stays."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from occupancy.domain import Stay
from occupancy.repository.models import StayModel

logger = logging.getLogger(__name__)


class StayRepository:
    """Persist and retrieve stays."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, stay_id: UUID) -> Stay | None:
        """Get a stay by ID."""
        result = await self._session.execute(select(StayModel).where(StayModel.id == stay_id))
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, stay: Stay) -> Stay:
        """Create a new stay."""
        now = datetime.now(UTC)
        model = StayModel(
            id=stay.id,
            property_id=stay.property_id,
            check_in_date=stay.check_in_date,
            check_out_date=stay.check_out_date,
            status=stay.status,
            notes=stay.notes,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_property(self, property_id: UUID) -> list[Stay]:
        """Get all stays for a property."""
        result = await self._session.execute(
            select(StayModel).where(StayModel.property_id == property_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def get_active_for_property(self, property_id: UUID) -> list[Stay]:
        """Get all active stays for a property."""
        result = await self._session.execute(
            select(StayModel).where(
                StayModel.property_id == property_id,
                StayModel.status == "active",
            )
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def update(self, stay: Stay) -> Stay:
        """Update an existing stay."""
        result = await self._session.execute(select(StayModel).where(StayModel.id == stay.id))
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Stay {stay.id} not found")

        model.check_in_date = stay.check_in_date
        model.check_out_date = stay.check_out_date
        model.status = stay.status
        model.notes = stay.notes
        model.updated_at = datetime.now(UTC)

        await self._session.flush()
        return self._model_to_domain(model)

    @staticmethod
    def _model_to_domain(model: StayModel) -> Stay:
        """Convert ORM model to domain model."""
        return Stay(
            id=model.id,
            property_id=model.property_id,
            check_in_date=model.check_in_date,
            check_out_date=model.check_out_date,
            status=model.status,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
