"""Device access grant repository."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.access import DeviceAccessGrant
from property.repository.models import DeviceAccessGrantModel

logger = logging.getLogger(__name__)


class DeviceAccessGrantRepository:
    """Persist and retrieve device access grants."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, grant_id: UUID) -> DeviceAccessGrant | None:
        """Get an access grant by ID."""
        result = await self._session.execute(
            select(DeviceAccessGrantModel).where(DeviceAccessGrantModel.id == grant_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, grant: DeviceAccessGrant) -> DeviceAccessGrant:
        """Create a new access grant."""
        grant.id = uuid4()
        grant.created_at = datetime.now(UTC)
        grant.updated_at = datetime.now(UTC)

        model = DeviceAccessGrantModel(
            id=grant.id,
            organization_id=grant.organization_id,
            device_id=grant.device_id,
            grantee_user_id=grant.grantee_user_id,
            grantee_email=grant.grantee_email,
            granted_by_user_id=grant.granted_by_user_id,
            access_type=grant.access_type,
            capabilities=grant.capabilities,
            expires_at=grant.expires_at,
            created_at=grant.created_at,
            updated_at=grant.updated_at,
            revoked_at=grant.revoked_at,
        )
        self._session.add(model)
        await self._session.flush()
        return grant

    async def list_by_device(
        self, device_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[DeviceAccessGrant]:
        """List all access grants for a device."""
        result = await self._session.execute(
            select(DeviceAccessGrantModel)
            .where(
                and_(
                    DeviceAccessGrantModel.device_id == device_id,
                    DeviceAccessGrantModel.revoked_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_grantee(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[DeviceAccessGrant]:
        """List all devices a user has access to."""
        result = await self._session.execute(
            select(DeviceAccessGrantModel)
            .where(
                and_(
                    DeviceAccessGrantModel.grantee_user_id == user_id,
                    DeviceAccessGrantModel.revoked_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def revoke(self, grant_id: UUID) -> bool:
        """Revoke an access grant (soft delete)."""
        result = await self._session.execute(
            select(DeviceAccessGrantModel).where(DeviceAccessGrantModel.id == grant_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.revoked_at = datetime.now(UTC)
        await self._session.flush()
        return True

    async def check_access(self, user_id: UUID, device_id: UUID, access_type: str) -> bool:
        """Check if a user has the requested access to a device."""
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(DeviceAccessGrantModel).where(
                and_(
                    DeviceAccessGrantModel.grantee_user_id == user_id,
                    DeviceAccessGrantModel.device_id == device_id,
                    DeviceAccessGrantModel.revoked_at.is_(None),
                    # Check not expired
                    or_(
                        DeviceAccessGrantModel.expires_at.is_(None),
                        DeviceAccessGrantModel.expires_at > now,
                    ),
                )
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        # Check access type
        grant_access_types = ["read", "control", "manage"]
        requested_index = grant_access_types.index(access_type)
        grant_index = grant_access_types.index(model.access_type)

        return grant_index >= requested_index

    @staticmethod
    def _model_to_domain(model: DeviceAccessGrantModel) -> DeviceAccessGrant:
        """Convert ORM model to domain model."""
        return DeviceAccessGrant(
            id=model.id,
            organization_id=model.organization_id,
            device_id=model.device_id,
            grantee_user_id=model.grantee_user_id,
            grantee_email=model.grantee_email,
            granted_by_user_id=model.granted_by_user_id,
            access_type=model.access_type,
            capabilities=model.capabilities,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            revoked_at=model.revoked_at,
        )
