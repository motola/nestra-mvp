"""Govee API routes."""

from __future__ import annotations

from datetime import datetime
from typing import cast
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import SessionLocal
from integrations.govee.adapter import GoveeAdapter
from integrations.govee.schemas import GoveeDeviceIn, GoveeDeviceOut
from property.persistence.device_repository import DeviceRepository

router = APIRouter(prefix="/integrations/govee", tags=["govee"])


class GoveeSyncRequest(BaseModel):
    """Request to sync Govee devices."""

    organization_id: UUID
    property_id: UUID
    api_key: str


class DeviceResponse(BaseModel):
    """Device response."""

    id: UUID
    vendor_name: str
    device_type: str
    online: bool


# Mock storage for devices - replace with DB later
_devices: dict[UUID, GoveeDeviceOut] = {
    UUID("22222222-2222-2222-2222-222222222221"): GoveeDeviceOut(
        id=UUID("22222222-2222-2222-2222-222222222221"),
        property_id=UUID("b4e3df93-f5e0-4e8f-beaa-33e2aead82ba"),  # p_maple
        govee_id="govee-1",
        name="Living room light",
        device_type="light",
        online=True,
        raw_state={"brightness": 100, "color": "#ffffff"},
        last_sync=datetime.now(),
        created_at=datetime.now(),
    ),
    UUID("22222222-2222-2222-2222-222222222222"): GoveeDeviceOut(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        property_id=UUID("b4e3df93-f5e0-4e8f-beaa-33e2aead82ba"),  # p_maple
        govee_id="govee-2",
        name="Bedroom light",
        device_type="light",
        online=False,
        raw_state={"brightness": 0, "color": "#ffffff"},
        last_sync=datetime.now(),
        created_at=datetime.now(),
    ),
}
_adapter = GoveeAdapter()


@router.post("/devices")
async def add_govee_device(request: GoveeDeviceIn) -> GoveeDeviceOut:
    """Add a Govee device to a property."""
    device_id = uuid4()
    device = GoveeDeviceOut(
        id=device_id,
        property_id=request.property_id,
        govee_id=request.govee_id,
        name=request.name,
        device_type=request.device_type,
        online=True,
        raw_state={},
        last_sync=datetime.now(),
        created_at=datetime.now(),
    )
    _devices[device_id] = device
    return device


@router.get("/devices")
async def list_govee_devices(property_id: UUID | None = None) -> list[GoveeDeviceOut]:
    """List Govee devices."""
    if property_id:
        return [d for d in _devices.values() if d.property_id == property_id]
    return list(_devices.values())


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on Govee device."""
    if device_id not in _devices:
        return {"error": "Device not found"}
    return {"status": "turned_on"}


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off Govee device."""
    if device_id not in _devices:
        return {"error": "Device not found"}
    return {"status": "turned_off"}


@router.post("/sync", response_model=list[DeviceResponse])
async def sync_govee_devices(request: GoveeSyncRequest) -> list[DeviceResponse]:
    """Sync Govee devices from cloud API and create device entries."""
    try:
        adapter = GoveeAdapter()

        # Fetch devices from Govee cloud API
        devices = await adapter.fetch_devices(
            organization_id=UUID("00000000-0000-0000-0000-000000000001"),
        portfolio_id=request.organization_id,
            property_id=request.property_id,
            integration_id=uuid4(),
            api_key=request.api_key,
        )

        # Store devices in database
        async with SessionLocal() as db:
            repository = DeviceRepository(db)
            created_devices = []
            for device in devices:
                stored_device = await repository.upsert(device)
                created_devices.append(
                    DeviceResponse(
                        id=cast(UUID, stored_device.id),
                        vendor_name=cast(str, stored_device.vendor_name),
                        device_type=stored_device.device_type.value,
                        online=stored_device.online,
                    )
                )

        return created_devices
    except Exception as e:
        msg = f"Failed to sync Govee devices: {str(e)}"
        raise HTTPException(status_code=500, detail=msg) from e
