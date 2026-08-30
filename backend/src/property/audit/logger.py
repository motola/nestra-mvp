"""Audit event logging for compliance and monitoring."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.audit import (
    AuditAction,
    AuditActorType,
    AuditEvent,
    AuditResourceType,
    AuditStatus,
)
from property.persistence.audit_event_repository import AuditEventRepository

logger = logging.getLogger(__name__)


class AuditLogger:
    """Log audit events for all critical operations."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = AuditEventRepository(session)

    async def log_event(
        self,
        organization_id: UUID,
        action: AuditAction,
        resource_type: AuditResourceType,
        resource_id: UUID,
        status: AuditStatus = AuditStatus.SUCCESS,
        actor_user_id: UUID | None = None,
        actor_type: AuditActorType = AuditActorType.USER,
        resource_name: str | None = None,
        changes: dict[str, object] | None = None,
        reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditEvent:
        """Log an audit event."""
        event = AuditEvent(
            id=None,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            changes=changes or {},
            status=status,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(UTC),
        )
        return await self._repo.create(event)

    async def log_device_created(
        self,
        organization_id: UUID,
        device_id: UUID,
        device_name: str | None = None,
        actor_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log device creation."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.DEVICE_CREATED,
            resource_type=AuditResourceType.DEVICE,
            resource_id=device_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=actor_user_id,
            resource_name=device_name,
            ip_address=ip_address,
        )

    async def log_device_updated(
        self,
        organization_id: UUID,
        device_id: UUID,
        device_name: str | None = None,
        changes: dict[str, object] | None = None,
        actor_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log device update."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.DEVICE_UPDATED,
            resource_type=AuditResourceType.DEVICE,
            resource_id=device_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=actor_user_id,
            resource_name=device_name,
            changes=changes,
            ip_address=ip_address,
        )

    async def log_command_executed(
        self,
        organization_id: UUID,
        command_id: UUID,
        device_id: UUID,
        actor_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log command execution."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.COMMAND_EXECUTED,
            resource_type=AuditResourceType.COMMAND,
            resource_id=command_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=actor_user_id,
            ip_address=ip_address,
            resource_name=f"Device {device_id}",
        )

    async def log_command_failed(
        self,
        organization_id: UUID,
        command_id: UUID,
        error_reason: str,
        actor_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log command execution failure."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.COMMAND_FAILED,
            resource_type=AuditResourceType.COMMAND,
            resource_id=command_id,
            status=AuditStatus.FAILURE,
            actor_user_id=actor_user_id,
            reason=error_reason,
            ip_address=ip_address,
        )

    async def log_access_granted(
        self,
        organization_id: UUID,
        grant_id: UUID,
        grantee_user_id: UUID | None = None,
        grantee_email: str | None = None,
        granted_by_user_id: UUID | None = None,
        device_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log access grant creation."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.ACCESS_GRANTED,
            resource_type=AuditResourceType.ACCESS_GRANT,
            resource_id=grant_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=granted_by_user_id,
            resource_name=grantee_email or str(grantee_user_id),
            changes={
                "grantee_user_id": str(grantee_user_id) if grantee_user_id else None,
                "grantee_email": grantee_email,
                "device_id": str(device_id) if device_id else None,
            },
            ip_address=ip_address,
        )

    async def log_access_revoked(
        self,
        organization_id: UUID,
        grant_id: UUID,
        grantee_user_id: UUID | None = None,
        grantee_email: str | None = None,
        revoked_by_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log access grant revocation."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.ACCESS_REVOKED,
            resource_type=AuditResourceType.ACCESS_GRANT,
            resource_id=grant_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=revoked_by_user_id,
            resource_name=grantee_email or str(grantee_user_id),
            ip_address=ip_address,
        )

    async def log_access_denied(
        self,
        organization_id: UUID,
        device_id: UUID,
        user_id: UUID | None = None,
        reason: str = "Insufficient permissions",
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log access denial attempt."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.ACCESS_DENIED,
            resource_type=AuditResourceType.DEVICE,
            resource_id=device_id,
            status=AuditStatus.FAILURE,
            actor_user_id=user_id,
            reason=reason,
            ip_address=ip_address,
        )

    async def log_share_link_created(
        self,
        organization_id: UUID,
        token_id: UUID,
        device_id: UUID,
        created_by_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log share link creation."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.SHARE_LINK_CREATED,
            resource_type=AuditResourceType.SHARE_LINK,
            resource_id=token_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=created_by_user_id,
            resource_name=f"Device {device_id}",
            ip_address=ip_address,
        )

    async def log_share_link_claimed(
        self,
        organization_id: UUID,
        token_id: UUID,
        claimed_by_user_id: UUID,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log share link claim."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.SHARE_LINK_CLAIMED,
            resource_type=AuditResourceType.SHARE_LINK,
            resource_id=token_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=claimed_by_user_id,
            ip_address=ip_address,
        )

    async def log_share_link_revoked(
        self,
        organization_id: UUID,
        token_id: UUID,
        revoked_by_user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log share link revocation."""
        return await self.log_event(
            organization_id=organization_id,
            action=AuditAction.SHARE_LINK_REVOKED,
            resource_type=AuditResourceType.SHARE_LINK,
            resource_id=token_id,
            status=AuditStatus.SUCCESS,
            actor_user_id=revoked_by_user_id,
            ip_address=ip_address,
        )
