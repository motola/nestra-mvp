"""Magic link token domain models for share-based access."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MagicLinkToken(BaseModel):
    """Temporary access token for sharing device access."""

    id: UUID | None = None
    organization_id: UUID
    device_id: UUID
    access_type: str  # "read", "control"
    token: str
    created_by_user_id: UUID
    claimed_by_user_id: UUID | None = None
    claimed_at: datetime | None = None
    expires_at: datetime
    created_at: datetime

    model_config = {"frozen": False}
