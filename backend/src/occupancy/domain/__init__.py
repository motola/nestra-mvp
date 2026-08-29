"""Occupancy domain models — rooms, tenants, stays, and preferences."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class TenantType(StrEnum):
    """Types of tenants."""

    RESIDENT = "resident"
    GUEST = "guest"
    STAFF = "staff"


class Tenant(BaseModel):
    """A tenant (resident, guest, or staff member)."""

    id: UUID | None = None
    organization_id: UUID
    user_id: UUID | None = None
    full_name: str
    email: str
    phone: str | None = None
    tenant_type: TenantType = TenantType.RESIDENT
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"frozen": False}


class Room(BaseModel):
    """A room within a property."""

    id: UUID | None = None
    property_id: UUID
    name: str
    room_type: str  # "bedroom", "bathroom", "kitchen", "living_room", etc.
    floor_number: int | None = None
    square_feet: int | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class Stay(BaseModel):
    """A stay (occupancy period) at a property."""

    id: UUID | None = None
    property_id: UUID
    check_in_date: datetime
    check_out_date: datetime | None = None
    status: str  # "active", "completed", "cancelled"
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class StayRoom(BaseModel):
    """Assignment of rooms to a stay."""

    id: UUID | None = None
    stay_id: UUID
    room_id: UUID
    created_at: datetime

    model_config = {"frozen": False}


class StayTenant(BaseModel):
    """Assignment of tenants to a stay."""

    id: UUID | None = None
    stay_id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = {"frozen": False}


class StayPreference(BaseModel):
    """Preferences for a tenant during a stay."""

    id: UUID | None = None
    stay_tenant_id: UUID
    temperature: int | None = None
    humidity: int | None = None
    lighting: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}
