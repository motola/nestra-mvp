"""Property-specific ORM models.

Note: IntegrationModel is now in integrations.models (shared across contexts).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from integrations.models import IntegrationModel  # noqa: F401
from property.domain import DeviceType


class PropertyModel(Base):
    """A property (building/asset) within a portfolio."""

    __tablename__ = "properties"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    property_type: Mapped[str] = mapped_column(String(100), nullable=False)
    units: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeviceModel(Base):
    """A unified smart home device across all integrations."""

    __tablename__ = "devices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    integration_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=True
    )
    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType), nullable=False)
    vendor: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_specific_id: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    online: Mapped[bool] = mapped_column(default=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_state: Mapped[dict[str, object]] = mapped_column(JSON, default={}, nullable=False)
