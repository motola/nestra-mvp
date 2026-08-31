"""Shared integration ORM models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class IntegrationModel(Base):
    """Integration connection (vendor API access)."""

    __tablename__ = "integrations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    provider_id: Mapped[str] = mapped_column(String(50), nullable=False)
    account_identifier: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    connection_identifier: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credential_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    credential_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    oauth_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    config: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships will be defined in respective integration modules
    # to avoid circular imports
    # devices: Mapped[list] = relationship(back_populates="integration")

    __table_args__ = (
        Index("idx_integration_provider", "provider_id"),
        Index("idx_integration_org", "organization_id"),
        Index(
            "uq_integrations_connection",
            "organization_id",
            "provider_id",
            "connection_identifier",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
    # Partial unique index handled in migration (g7h8i9j0k1l2m)
    # CREATE UNIQUE INDEX uq_integrations_connection ON integrations
    # (organization_id, provider_id, connection_identifier)
    # WHERE provider_id IS NOT NULL AND deleted_at IS NULL
