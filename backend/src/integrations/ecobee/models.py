"""Ecobee Thermostat ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from integrations.models import IntegrationModel
from shared.db import Base


class EcobeeDeviceModel(Base):
    """An Ecobee Thermostat paired to a property."""

    __tablename__ = "ecobee_devices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    target_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    mode: Mapped[str] = mapped_column(String(50), nullable=False)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    is_online: Mapped[bool] = mapped_column(default=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    integration: Mapped[IntegrationModel] = relationship(back_populates="devices")

    __table_args__ = (
        UniqueConstraint("property_id", "device_id", name="uq_device_property_ecobee"),
    )
