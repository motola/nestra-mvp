"""API request/response schemas for occupancy management entities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    """Request to create a tenant."""

    full_name: str = Field(..., description="Tenant full name")
    email: str = Field(..., description="Tenant email address")
    phone: str | None = Field(None, description="Optional phone number")
    tenant_type: str = Field("resident", description="Tenant type (resident, guest, staff)")
    user_id: UUID | None = Field(None, description="Optional linked user ID")


class TenantRead(BaseModel):
    """Tenant response."""

    id: UUID | None = None
    organization_id: UUID
    user_id: UUID | None = None
    full_name: str
    email: str
    phone: str | None = None
    tenant_type: str = Field(..., description="Tenant type (resident, guest, staff)")
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class TenantUpdate(BaseModel):
    """Request to update a tenant."""

    full_name: str | None = Field(None, description="Updated full name")
    email: str | None = Field(None, description="Updated email")
    phone: str | None = Field(None, description="Updated phone number")
    tenant_type: str | None = Field(None, description="Updated tenant type")


class TenantList(BaseModel):
    """List response with tenants."""

    items: list[TenantRead]
    total: int
    skip: int
    limit: int


class RoomCreate(BaseModel):
    """Request to create a room."""

    property_id: UUID = Field(..., description="Property ID")
    name: str = Field(..., description="Room name")
    room_type: str = Field(..., description="Room type (bedroom, bathroom, kitchen, etc)")
    floor_number: int | None = Field(None, description="Floor number")
    square_feet: int | None = Field(None, description="Room area in square feet")
    description: str | None = Field(None, description="Optional room description")


class RoomRead(BaseModel):
    """Room response."""

    id: UUID | None = None
    property_id: UUID
    name: str
    room_type: str
    floor_number: int | None = None
    square_feet: int | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class RoomUpdate(BaseModel):
    """Request to update a room."""

    name: str | None = Field(None, description="Updated room name")
    room_type: str | None = Field(None, description="Updated room type")
    floor_number: int | None = Field(None, description="Updated floor number")
    square_feet: int | None = Field(None, description="Updated square footage")
    description: str | None = Field(None, description="Updated description")


class RoomList(BaseModel):
    """List response with rooms."""

    items: list[RoomRead]
    total: int
    skip: int
    limit: int


class StayCreate(BaseModel):
    """Request to create a stay."""

    property_id: UUID = Field(..., description="Property ID")
    check_in_date: datetime = Field(..., description="Check-in datetime")
    check_out_date: datetime | None = Field(None, description="Optional check-out datetime")
    status: str = Field("active", description="Stay status (active, completed, cancelled)")
    notes: str | None = Field(None, description="Optional stay notes")
    room_ids: list[UUID] = Field(default_factory=list, description="Room IDs to assign")
    tenant_ids: list[UUID] = Field(default_factory=list, description="Tenant IDs to assign")


class StayRead(BaseModel):
    """Stay response."""

    id: UUID | None = None
    property_id: UUID
    check_in_date: datetime
    check_out_date: datetime | None = None
    status: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class StayUpdate(BaseModel):
    """Request to update a stay."""

    check_in_date: datetime | None = Field(None, description="Updated check-in date")
    check_out_date: datetime | None = Field(None, description="Updated check-out date")
    status: str | None = Field(None, description="Updated status")
    notes: str | None = Field(None, description="Updated notes")


class StayList(BaseModel):
    """List response with stays."""

    items: list[StayRead]
    total: int
    skip: int
    limit: int


class StayPreferenceRead(BaseModel):
    """Stay preference response."""

    id: UUID
    stay_tenant_id: UUID
    temperature: int | None = None
    humidity: int | None = None
    lighting: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class StayTenantRead(BaseModel):
    """Stay tenant response with associated tenant and preference details."""

    id: UUID
    stay_id: UUID
    tenant_id: UUID
    tenant: TenantRead | None = Field(None, description="Tenant details")
    preference: StayPreferenceRead | None = Field(None, description="Tenant preferences")
    created_at: datetime

    model_config = {"from_attributes": True}
