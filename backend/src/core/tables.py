"""SQLModel table definitions — single source of truth for all 6 database tables."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Organisation(SQLModel, table=True):
    __tablename__ = "organisations"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    plan: str | None = None
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))


class Property(SQLModel, table=True):
    __tablename__ = "properties"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organisation_id: UUID | None = Field(foreign_key="organisations.id", default=None)
    name: str
    address: str | None = None
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))


class Room(SQLModel, table=True):
    __tablename__ = "rooms"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    property_id: UUID = Field(foreign_key="properties.id")
    name: str
    floor: int | None = None
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))


class Device(SQLModel, table=True):
    __tablename__ = "devices"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    property_id: UUID = Field(foreign_key="properties.id")
    room_id: UUID | None = Field(foreign_key="rooms.id", default=None)
    vendor: str | None = None
    vendor_id: str | None = None
    name: str
    model: str | None = None
    ip_address: str | None = None
    mac: str | None = None
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    device_id: UUID = Field(foreign_key="devices.id")
    property_id: UUID | None = None
    device_name: str | None = None
    property_name: str | None = None
    type: str | None = None
    severity: str | None = None
    message: str | None = None
    dismissed: bool = False
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))


class StateHistory(SQLModel, table=True):
    __tablename__ = "state_history"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    device_id: UUID = Field(foreign_key="devices.id")
    event_type: str | None = None
    value: str | None = None
    property_id: UUID | None = None
    recorded_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
