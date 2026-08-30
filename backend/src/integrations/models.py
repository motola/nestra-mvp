"""Shared integration ORM models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class IntegrationModel(Base):
    """Integration connection (vendor API access)."""

    __tablename__ = "integrations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    provider_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
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
    config: Mapped[dict[str, object]] = mapped_column(JSON, default={}, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships will be defined in respective integration modules
    # to avoid circular imports
    # devices: Mapped[list] = relationship(back_populates="integration")

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "provider_id",
            "connection_identifier",
            name="uq_integration_org_provider_connection",
            postgresql_where="deleted_at IS NULL",
        ),
        Index("idx_integration_provider", "provider_id"),
        Index("idx_integration_org", "organization_id"),
    )
