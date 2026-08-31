"""Property domain models — portfolios, properties, devices, integrations, access, and audit."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

# Access control models
from property.domain.access import AccessType, DeviceAccessGrant  # noqa: F401
from property.domain.audit import (  # noqa: F401
    AuditAction,
    AuditActorType,
    AuditEvent,
    AuditResourceType,
    AuditStatus,
)
from property.domain.tokens import MagicLinkToken  # noqa: F401


class DeviceType(StrEnum):
    """Types of smart home devices."""

    LOCK = "lock"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    PLUG = "plug"
    SENSOR = "sensor"
    SPEAKER = "speaker"
    LIGHT = "light"


class Integration(BaseModel):
    """Configured provider connection belonging to an organization."""

    id: UUID | None = None
    organization_id: UUID
    provider_id: str
    account_identifier: str = ""
    enabled: bool = True
    created_at: datetime
    updated_at: datetime
    connection_identifier: str | None = None
    display_name: str | None = None
    credential_provider: str | None = None
    credential_ref: str | None = None
    oauth_expires_at: datetime | None = None
    config: dict[str, object] = Field(default_factory=dict)
    deleted_at: datetime | None = None

    model_config = {"frozen": False}


class Property(BaseModel):
    """A property (building/asset) within a portfolio."""

    id: UUID | None = None
    portfolio_id: UUID
    organization_id: UUID
    name: str
    address: str
    description: str | None = None
    timezone: str = "UTC"
    property_type: str
    units: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class Device(BaseModel):
    """Unified smart home device across all integrations."""

    id: UUID | None = None
    organization_id: UUID
    portfolio_id: UUID
    property_id: UUID
    integration_id: UUID
    device_type: DeviceType
    vendor: str
    vendor_specific_id: str
    vendor_name: str | None = None
    online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
    raw_state: dict[str, object] = Field(default_factory=dict)
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    ownership_type: str | None = None  # "organization", "property", "tenant"
    owner_property_id: UUID | None = None
    owner_tenant_id: UUID | None = None

    model_config = {"frozen": False}


class Capability(BaseModel):
    """A capability that a device can have (global catalog)."""

    id: UUID | None = None
    code: str  # e.g., "on_off", "brightness", "temperature"
    name: str
    description: str | None = None
    category: str  # e.g., "control", "sensor", "info"
    created_at: datetime

    model_config = {"frozen": False}


class DeviceCapability(BaseModel):
    """A capability that a specific device supports."""

    id: UUID | None = None
    device_id: UUID
    capability_id: UUID
    created_at: datetime

    model_config = {"frozen": False}


class DevicePlacement(BaseModel):
    """Physical placement of a device (location within property/room)."""

    id: UUID | None = None
    device_id: UUID
    property_id: UUID
    room_id: UUID | None = None
    placement_type: str = "room"  # "room", "building", "external"
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class DeviceIntegration(BaseModel):
    """Connection between a device and an integration."""

    id: UUID | None = None
    device_id: UUID
    integration_id: UUID
    connection_identifier: str  # vendor-specific connection info
    discovered_at: datetime
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class DeviceCurrentState(BaseModel):
    """Current state of a device (one-to-one with device)."""

    id: UUID | None = None
    device_id: UUID
    state: dict[str, object] = Field(default_factory=dict)
    last_updated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"frozen": False}


class DeviceStateEvent(BaseModel):
    """Append-only log of device state changes."""

    id: UUID | None = None
    device_id: UUID
    state_change: dict[str, object] = Field(default_factory=dict)
    event_type: str  # "state_change", "discovery", "error"
    created_at: datetime

    model_config = {"frozen": False}
