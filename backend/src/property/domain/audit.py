"""Audit event domain models for compliance and logging."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AuditActorType(StrEnum):
    """Actor types for audit events."""

    USER = "user"
    SYSTEM = "system"
    AUTOMATION = "automation"


class AuditAction(StrEnum):
    """Action types for audit events."""

    DEVICE_CREATED = "device_created"
    DEVICE_UPDATED = "device_updated"
    DEVICE_DELETED = "device_deleted"
    COMMAND_EXECUTED = "command_executed"
    COMMAND_FAILED = "command_failed"
    ACCESS_GRANTED = "access_granted"
    ACCESS_REVOKED = "access_revoked"
    SHARE_LINK_CREATED = "share_link_created"
    SHARE_LINK_CLAIMED = "share_link_claimed"
    SHARE_LINK_REVOKED = "share_link_revoked"
    ACCESS_DENIED = "access_denied"


class AuditResourceType(StrEnum):
    """Resource types for audit events."""

    DEVICE = "device"
    PROPERTY = "property"
    COMMAND = "command"
    GRANT = "grant"
    ACCESS_GRANT = "access_grant"
    SHARE_LINK = "share_link"


class AuditStatus(StrEnum):
    """Status of audit events."""

    SUCCESS = "success"
    FAILURE = "failure"


class AuditEvent(BaseModel):
    """Audit trail event for compliance and security logging."""

    id: UUID | None = None
    organization_id: UUID
    actor_user_id: UUID | None = None
    actor_type: str  # "user", "system", "automation"
    action: str  # "device_created", "command_executed", etc.
    resource_type: str  # "device", "property", "command"
    resource_id: UUID
    resource_name: str | None = None
    changes: dict[str, object] = Field(default_factory=dict)
    status: str  # "success", "failure"
    reason: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    model_config = {"frozen": False}
