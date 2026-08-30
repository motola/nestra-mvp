"""API request/response schemas for property management entities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PortfolioCreate(BaseModel):
    """Request to create a portfolio."""

    name: str = Field(..., description="Portfolio name")
    description: str | None = Field(None, description="Optional portfolio description")


class PortfolioRead(BaseModel):
    """Portfolio response."""

    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PortfolioUpdate(BaseModel):
    """Request to update a portfolio."""

    name: str | None = Field(None, description="Updated portfolio name")
    description: str | None = Field(None, description="Updated portfolio description")


class PortfolioList(BaseModel):
    """List response with portfolios."""

    items: list[PortfolioRead]
    total: int
    skip: int
    limit: int


class PropertyCreate(BaseModel):
    """Request to create a property."""

    portfolio_id: UUID = Field(..., description="Portfolio ID")
    name: str = Field(..., description="Property name")
    address: str = Field(..., description="Physical address")
    property_type: str = Field(..., description="Type of property (apartment, house, etc)")
    units: int = Field(1, description="Number of units")
    timezone: str = Field("UTC", description="Property timezone")
    description: str | None = Field(None, description="Optional description")


class PropertyRead(BaseModel):
    """Property response."""

    id: UUID
    portfolio_id: UUID
    organization_id: UUID
    name: str
    address: str
    property_type: str
    units: int
    timezone: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyUpdate(BaseModel):
    """Request to update a property."""

    name: str | None = Field(None, description="Updated property name")
    address: str | None = Field(None, description="Updated address")
    property_type: str | None = Field(None, description="Updated property type")
    units: int | None = Field(None, description="Updated unit count")
    timezone: str | None = Field(None, description="Updated timezone")
    description: str | None = Field(None, description="Updated description")


class PropertyList(BaseModel):
    """List response with properties."""

    items: list[PropertyRead]
    total: int
    skip: int
    limit: int


class CapabilityRead(BaseModel):
    """Capability response."""

    id: UUID | None = None
    code: str = Field(..., description="Unique capability code (on_off, brightness, etc)")
    name: str = Field(..., description="Human-readable capability name")
    description: str | None = Field(None, description="Capability description")
    category: str = Field(..., description="Capability category (control, sensor, info, etc)")
    created_at: datetime

    model_config = {"from_attributes": True}


class CapabilityList(BaseModel):
    """List response with capabilities."""

    items: list[CapabilityRead]
    total: int
    skip: int
    limit: int


class DeviceCapabilityRead(BaseModel):
    """Device capability response."""

    id: UUID | None = None
    device_id: UUID
    capability_id: UUID
    capability: CapabilityRead | None = Field(None, description="Nested capability details")
    created_at: datetime

    model_config = {"from_attributes": True}


class IntegrationRead(BaseModel):
    """Integration response."""

    id: UUID
    organization_id: UUID
    vendor: str = Field(..., description="Integration vendor (shelly, august, lifx, etc)")
    account_identifier: str = Field(..., description="Vendor account identifier")
    enabled: bool = Field(True, description="Whether integration is active")
    provider_id: str | None = None
    connection_identifier: str | None = None
    display_name: str | None = None
    credential_provider: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeviceRead(BaseModel):
    """Device response."""

    id: UUID
    organization_id: UUID
    portfolio_id: UUID
    property_id: UUID
    integration_id: UUID
    device_type: str = Field(
        ..., description="Device type (lock, thermostat, camera, plug, sensor, speaker, light)"
    )
    vendor: str = Field(..., description="Device vendor")
    vendor_specific_id: str = Field(..., description="Vendor-specific device ID")
    vendor_name: str | None = None
    online: bool = Field(True, description="Device online status")
    last_sync: datetime | None = None
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeviceDetail(BaseModel):
    """Detailed device response with placement, integrations, and capabilities."""

    id: UUID | None = None
    organization_id: UUID
    portfolio_id: UUID
    property_id: UUID
    integration_id: UUID
    device_type: str
    vendor: str
    vendor_specific_id: str
    vendor_name: str | None = None
    online: bool
    last_sync: datetime | None = None
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    placement: dict[str, object] | None = Field(None, description="Device placement info")
    capabilities: list[DeviceCapabilityRead] = Field(
        default_factory=list, description="Device capabilities"
    )
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeviceCreate(BaseModel):
    """Request to create a device."""

    portfolio_id: UUID = Field(..., description="Portfolio ID")
    property_id: UUID = Field(..., description="Property ID")
    integration_id: UUID = Field(..., description="Integration ID")
    device_type: str = Field(..., description="Device type")
    vendor: str = Field(..., description="Device vendor")
    vendor_specific_id: str = Field(..., description="Vendor-specific device ID")
    vendor_name: str | None = Field(None, description="Vendor-provided device name")
    room_id: UUID | None = Field(None, description="Optional room ID for placement")
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None


class DeviceUpdate(BaseModel):
    """Request to update a device."""

    vendor_name: str | None = Field(None, description="Updated device name")
    online: bool | None = Field(None, description="Updated online status")
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None


class DeviceList(BaseModel):
    """List response with devices."""

    items: list[DeviceRead]
    total: int
    skip: int
    limit: int


class RoomRead(BaseModel):
    """Room response."""

    id: UUID
    property_id: UUID
    name: str
    room_type: str
    floor_number: int | None = None
    square_feet: int | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class StayRead(BaseModel):
    """Stay response."""

    id: UUID
    property_id: UUID
    check_in_date: datetime
    check_out_date: datetime | None = None
    status: str = Field(..., description="Stay status (active, completed, cancelled)")
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TenantRead(BaseModel):
    """Tenant response."""

    id: UUID
    organization_id: UUID
    user_id: UUID | None = None
    full_name: str
    email: str
    phone: str | None = None
    tenant_type: str = Field(..., description="Tenant type (resident, guest, staff)")
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
