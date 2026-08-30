"""Tenant repository — persistence and retrieval of tenants."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from occupancy.domain import Tenant
from occupancy.repository.models import TenantModel

logger = logging.getLogger(__name__)


class TenantRepository:
    """Persist and retrieve tenants."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        """Get a tenant by ID."""
        result = await self._session.execute(select(TenantModel).where(TenantModel.id == tenant_id))
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        now = datetime.now(UTC)
        model = TenantModel(
            id=tenant.id,
            organization_id=tenant.organization_id,
            user_id=tenant.user_id,
            full_name=tenant.full_name,
            email=tenant.email,
            phone=tenant.phone,
            tenant_type=tenant.tenant_type,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_organization(self, organization_id: UUID) -> list[Tenant]:
        """Get all tenants for an organization."""
        result = await self._session.execute(
            select(TenantModel).where(
                TenantModel.organization_id == organization_id,
                TenantModel.deleted_at.is_(None),
            )
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def update(self, tenant: Tenant) -> Tenant:
        """Update an existing tenant."""
        result = await self._session.execute(select(TenantModel).where(TenantModel.id == tenant.id))
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Tenant {tenant.id} not found")

        model.full_name = tenant.full_name
        model.email = tenant.email
        model.phone = tenant.phone
        model.tenant_type = tenant.tenant_type
        model.updated_at = datetime.now(UTC)

        await self._session.flush()
        return self._model_to_domain(model)

    async def soft_delete(self, tenant_id: UUID) -> None:
        """Soft delete a tenant."""
        result = await self._session.execute(select(TenantModel).where(TenantModel.id == tenant_id))
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Tenant {tenant_id} not found")

        model.deleted_at = datetime.now(UTC)
        model.updated_at = datetime.now(UTC)
        await self._session.flush()

    @staticmethod
    def _model_to_domain(model: TenantModel) -> Tenant:
        """Convert ORM model to domain model."""
        return Tenant(
            id=model.id,
            organization_id=model.organization_id,
            user_id=model.user_id,
            full_name=model.full_name,
            email=model.email,
            phone=model.phone,
            tenant_type=model.tenant_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
