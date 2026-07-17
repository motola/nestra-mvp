"""Matter ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from utility.db import Base


class MatterDeviceModel(Base):
    """Matter protocol device."""

    __tablename__ = "matter_devices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    matter_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    online: Mapped[bool] = mapped_column(default=False)
    raw_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
