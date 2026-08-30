"""Audit event domain models for compliance and logging."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
