"""Property repository — persistence and retrieval of properties."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import Property
from property.repository.models import PropertyModel

logger = logging.getLogger(__name__)


class PropertyRepository:
    """Persist and retrieve properties."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, property_id: UUID) -> Property | None:
        """Get a property by ID."""
        result = await self._session.execute(
            select(PropertyModel).where(PropertyModel.id == property_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def list_by_portfolio(self, portfolio_id: UUID) -> list[Property]:
        """Get all properties for a portfolio."""
        result = await self._session.execute(
            select(PropertyModel).where(PropertyModel.portfolio_id == portfolio_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    @staticmethod
    def _model_to_domain(model: PropertyModel) -> Property:
        """Convert ORM model to domain model."""
        return Property(
            id=model.id,
            portfolio_id=model.portfolio_id,
            organization_id=model.organization_id,
            name=model.name,
            address=model.address,
            description=model.description,
            timezone=model.timezone,
            property_type=model.property_type,
            units=model.units,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
