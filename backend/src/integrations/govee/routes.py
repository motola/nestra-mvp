"""Govee API routes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter

from integrations.govee.adapter import GoveeAdapter
from integrations.govee.schemas import GoveeDeviceIn, GoveeDeviceOut

router = APIRouter(prefix="/integrations/govee", tags=["govee"])

# Mock storage for devices - replace with DB later
_devices: dict[UUID, GoveeDeviceOut] = {}
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
