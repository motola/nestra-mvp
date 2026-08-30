"""API schemas for access control and audit logging."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeviceAccessGrantCreate(BaseModel):
    """Create a device access grant."""

    device_id: UUID
    grantee_user_id: UUID | None = None
    grantee_email: str | None = None
    access_type: str  # "read", "control", "manage"
    capabilities: list[str] = []
    expires_at: datetime | None = None


class DeviceAccessGrantUpdate(BaseModel):
    """Update a device access grant."""

    access_type: str | None = None
    capabilities: list[str] | None = None
    expires_at: datetime | None = None


class DeviceAccessGrantRead(BaseModel):
    """Read a device access grant."""

    id: UUID
    device_id: UUID
    grantee_user_id: UUID | None = None
    grantee_email: str | None = None
    access_type: str
    capabilities: list[str]
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None = None


class DeviceAccessGrantList(BaseModel):
    """List of device access grants."""

    items: list[DeviceAccessGrantRead]
    total: int
    skip: int
    limit: int


class MagicLinkTokenCreate(BaseModel):
    """Create a magic link token."""

    device_id: UUID
    access_type: str  # "read", "control"
    expires_in_hours: int = 24


class MagicLinkTokenRead(BaseModel):
    """Read a magic link token (without exposing the token itself)."""

    id: UUID
    device_id: UUID
    access_type: str
    created_at: datetime
    claimed_at: datetime | None = None
    expires_at: datetime
    revoked_at: datetime | None = None


class MagicLinkTokenClaimResponse(BaseModel):
    """Response when claiming a magic link token."""

    success: bool
    message: str
    device_id: UUID | None = None


class AuditEventRead(BaseModel):
    """Read an audit event."""

    id: UUID
    organization_id: UUID
    actor_user_id: UUID | None = None
    actor_type: str
    action: str
    resource_type: str
    resource_id: UUID
    resource_name: str | None = None
    changes: dict[str, object]
    status: str
    reason: str | None = None
    ip_address: str | None = None
    created_at: datetime


class AuditEventList(BaseModel):
    """List of audit events."""

    items: list[AuditEventRead]
    total: int
    skip: int
    limit: int


class AuditEventSummary(BaseModel):
    """Summary of audit events."""

    events_today: int
    total_events: int
    action_counts: dict[str, int]


class MagicLinkTokenWithToken(BaseModel):
    """Magic link token with the actual token value (only for creation)."""

    id: UUID
    token: str
    device_id: UUID
    access_type: str
    created_at: datetime
    expires_at: datetime
    share_link: str  # Full URL to share
