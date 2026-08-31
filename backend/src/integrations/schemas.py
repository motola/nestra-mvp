"""Integration API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IntegrationCreateRequest(BaseModel):
    """Request to create an integration."""

    organization_id: UUID
    provider_id: str
    account_identifier: str = ""
    connection_identifier: str | None = None
    display_name: str | None = None
    config: dict[str, object] = Field(default_factory=dict)


class IntegrationResponse(BaseModel):
    """Integration response."""

    id: UUID
    organization_id: UUID
    provider_id: str
    account_identifier: str
    connection_identifier: str | None
    display_name: str | None
    enabled: bool
    created_at: datetime
    updated_at: datetime


class IntegrationUpdateRequest(BaseModel):
    """Request to update an integration."""

    account_identifier: str | None = None
    connection_identifier: str | None = None
    display_name: str | None = None
    enabled: bool | None = None
