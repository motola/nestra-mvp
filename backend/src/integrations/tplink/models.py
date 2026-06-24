"""TP-Link Smart Plug ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from integrations.models import IntegrationModel
from shared.db import Base


class TPlinkPlugModel(Base):
    """A TP-Link Smart Plug paired to a property."""

    __tablename__ = "tplink_plugs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    power_state: Mapped[bool] = mapped_column(Boolean, default=False)
    power_usage_w: Mapped[float] = mapped_column(Float, default=0.0)
    is_online: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    integration: Mapped[IntegrationModel] = relationship(back_populates="devices")

    __table_args__ = (UniqueConstraint("property_id", "device_id", name="uq_plug_property_tplink"),)
