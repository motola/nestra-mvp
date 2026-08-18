"""OAuth models and schemas for device integrations."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class OAuthConfig(BaseModel):
    """OAuth configuration for a device vendor."""

    vendor: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    scopes: list[str]
    redirect_uri_path: str

    class Config:
        frozen = True


class OAuthTokenIn(BaseModel):
    """Input schema for storing OAuth token."""

    access_token: str
    token_type: str = "Bearer"
    refresh_token: str | None = None
    expires_at: datetime | None = None


class OAuthTokenOut(BaseModel):
    """Output schema for OAuth token."""

    id: UUID
    organization_id: UUID
    vendor: str
    access_token: str
    token_type: str
    refresh_token: str | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OAuthTokenModel(Base):
    """OAuth token storage (encrypted at rest in production)."""

    __tablename__ = "oauth_tokens"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    vendor: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), default="Bearer")
    refresh_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_response: Mapped[dict[str, Any]] = mapped_column(JSON, default={})
