"""August Smart Lock ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from integrations.models import IntegrationModel
from utility.db import Base


class AugustLockModel(Base):
    """An August Smart Lock paired to a property."""

    __tablename__ = "august_locks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    lock_id: Mapped[str] = mapped_column(String(255), nullable=False)  # August device ID
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    battery_level: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    integration: Mapped[IntegrationModel] = relationship(back_populates="devices")

    __table_args__ = (UniqueConstraint("property_id", "lock_id", name="uq_lock_property_august"),)
