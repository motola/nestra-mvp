"""Shared integration ORM models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from utility.db import Base


class IntegrationModel(Base):
    """Integration connection (vendor API access)."""

    __tablename__ = "integrations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    vendor: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "bluetooth", "govee", "lifx", etc.
    account_identifier: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships will be defined in respective integration modules
    # to avoid circular imports
    # devices: Mapped[list] = relationship(back_populates="integration")

    __table_args__ = (
        UniqueConstraint("organization_id", "vendor", name="uq_integration_org_vendor"),
    )
