"""Property-specific ORM models.

Note: IntegrationModel is now in integrations.models (shared across contexts).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from integrations.models import IntegrationModel  # noqa: F401
from property.domain import DeviceType
from property.domain.command import CommandPriority, CommandStatus, CommandType


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
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    portfolio_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("properties.id"), nullable=False, index=True
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True
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
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ownership_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    owner_property_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("properties.id"), nullable=True, index=True
    )
    owner_tenant_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )

    __table_args__ = (Index("idx_device_vendor_key", "vendor", "vendor_specific_id"),)


class CapabilityModel(Base):
    """A capability that a device can have (global catalog)."""

    __tablename__ = "capabilities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeviceCapabilityModel(Base):
    """A capability that a specific device supports."""

    __tablename__ = "device_capabilities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    capability_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("capabilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_device_capability_key", "device_id", "capability_id"),)


class DevicePlacementModel(Base):
    """Physical placement of a device (location within property/room)."""

    __tablename__ = "device_placements"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("properties.id"), nullable=False, index=True
    )
    room_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("rooms.id"), nullable=True, index=True
    )
    placement_type: Mapped[str] = mapped_column(String(50), nullable=False, default="room")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeviceIntegrationModel(Base):
    """Connection between a device and an integration."""

    __tablename__ = "device_integrations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True
    )
    connection_identifier: Mapped[str] = mapped_column(String(500), nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_device_integration_key", "device_id", "integration_id"),)


class DeviceCurrentStateModel(Base):
    """Current state of a device (one-to-one with device)."""

    __tablename__ = "device_current_states"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    state: Mapped[dict[str, object]] = mapped_column(JSON, default={}, nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeviceStateEventModel(Base):
    """Append-only log of device state changes."""

    __tablename__ = "device_state_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    state_change: Mapped[dict[str, object]] = mapped_column(JSON, default={}, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CommandModel(Base):
    """A command to execute on a device."""

    __tablename__ = "commands"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True
    )
    capability_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    command_type: Mapped[CommandType] = mapped_column(Enum(CommandType), nullable=False)
    parameters: Mapped[dict[str, object]] = mapped_column(JSON, default={}, nullable=False)
    priority: Mapped[CommandPriority] = mapped_column(
        Enum(CommandPriority), default=CommandPriority.NORMAL, nullable=False
    )
    status: Mapped[CommandStatus] = mapped_column(
        Enum(CommandStatus), default=CommandStatus.PENDING, nullable=False, index=True
    )
    result: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_command_device_status", "device_id", "status"),
        Index("idx_command_created_at", "created_at"),
    )


class CommandExecutionLogModel(Base):
    """Append-only log of command executions."""

    __tablename__ = "command_execution_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    command_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("commands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[CommandStatus] = mapped_column(Enum(CommandStatus), nullable=False, index=True)
    result: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    __table_args__ = (Index("idx_execution_log_command_created", "command_id", "created_at"),)
