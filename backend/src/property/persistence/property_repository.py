"""Property repository — retrieve properties by id."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import Property
from property.repository.models import PropertyModel


class PropertyRepository:
    """Retrieve properties from database."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, property_id: UUID) -> Property | None:
        """Retrieve property by id."""
        stmt = select(PropertyModel).where(PropertyModel.id == property_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_domain(model)

    def _model_to_domain(self, model: PropertyModel) -> Property:
        """Convert ORM model to domain object."""
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
