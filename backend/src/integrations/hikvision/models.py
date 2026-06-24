"""Hikvision Camera ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from integrations.models import IntegrationModel
from shared.db import Base


class HikvisionCameraModel(Base):
    """A Hikvision Camera paired to a property."""

    __tablename__ = "hikvision_cameras"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    camera_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=True)
    stream_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    integration: Mapped[IntegrationModel] = relationship(back_populates="devices")

    __table_args__ = (
        UniqueConstraint("property_id", "camera_id", name="uq_camera_property_hikvision"),
    )
