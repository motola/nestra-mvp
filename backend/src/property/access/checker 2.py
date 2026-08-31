"""Access control checker for device operations."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.access import AccessType
from property.persistence.device_access_grant_repository import DeviceAccessGrantRepository

logger = logging.getLogger(__name__)


class AccessChecker:
    """Check and enforce access control for device operations."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._grant_repo = DeviceAccessGrantRepository(session)

    async def require_device_access(
        self, user_id: UUID, device_id: UUID, access_type: AccessType
    ) -> bool:
        """Check if user has required access to device."""
        return await self._grant_repo.check_access(user_id, device_id, access_type)

    async def get_user_accessible_devices(self, user_id: UUID) -> list[UUID]:
        """Get all devices a user can access."""
        grants = await self._grant_repo.list_by_grantee(user_id, skip=0, limit=1000)

        # Filter out expired grants
        now = datetime.now(UTC)
        accessible_devices = []
        for grant in grants:
            if grant.revoked_at is not None:
                continue
            if grant.expires_at is not None and grant.expires_at < now:
                continue
            accessible_devices.append(grant.device_id)

        return accessible_devices

    async def can_execute_command(
        self, user_id: UUID, device_id: UUID, capability: str | None = None
    ) -> bool:
        """Check if user can execute a command on a device."""
        # Must have control access
        if not await self.require_device_access(user_id, device_id, AccessType.CONTROL):
            return False

        # If specific capability requested, check it's in allowed list
        if capability:
            grant = await self._grant_repo.list_by_grantee(user_id)
            for g in grant:
                if g.device_id == device_id:
                    if g.capabilities and capability not in g.capabilities:
                        return False
                    break

        return True

    async def require_access_or_raise(
        self, user_id: UUID, device_id: UUID, access_type: AccessType
    ) -> None:
        """Check access or raise an exception."""
        from fastapi import HTTPException

        has_access = await self.require_device_access(user_id, device_id, access_type)
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied to device")
