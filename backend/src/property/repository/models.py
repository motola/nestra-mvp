from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base


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

    devices: Mapped[list[BluetoothDeviceModel]] = relationship(back_populates="integration")

    __table_args__ = (
        UniqueConstraint("organization_id", "vendor", name="uq_integration_org_vendor"),
    )


class BluetoothDeviceModel(Base):
    """A Bluetooth device paired via Web Bluetooth API."""

    __tablename__ = "bluetooth_devices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    mac_address: Mapped[str] = mapped_column(String(17), nullable=False)  # AA:BB:CC:DD:EE:FF format
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    rssi: Mapped[int] = mapped_column(Integer, nullable=False, default=-100)  # signal strength
    battery_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    is_paired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    integration: Mapped[IntegrationModel] = relationship(back_populates="devices")

    __table_args__ = (
        UniqueConstraint("property_id", "mac_address", name="uq_device_property_mac"),
    )
