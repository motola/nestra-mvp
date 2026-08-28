"""Integration API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IntegrationCreateRequest(BaseModel):
    """Request to create an integration."""

    organization_id: UUID
    vendor: str
    account_identifier: str = ""


class IntegrationResponse(BaseModel):
    """Integration response."""

    id: UUID
    organization_id: UUID
    vendor: str
    account_identifier: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


class IntegrationUpdateRequest(BaseModel):
    """Request to update an integration."""

    account_identifier: str | None = None
    enabled: bool | None = None
