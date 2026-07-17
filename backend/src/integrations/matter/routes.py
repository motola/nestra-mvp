"""Matter API routes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter

from integrations.matter.adapter import MatterAdapter
from integrations.matter.schemas import MatterDeviceIn, MatterDeviceOut

router = APIRouter(prefix="/integrations/matter", tags=["matter"])

# Mock storage for devices - replace with DB later
_devices: dict[UUID, MatterDeviceOut] = {}
_adapter = MatterAdapter()


@router.post("/devices")
async def add_matter_device(request: MatterDeviceIn) -> MatterDeviceOut:
    """Add a Matter device to a property."""
    device_id = uuid4()
    device = MatterDeviceOut(
        id=device_id,
        property_id=request.property_id,
        matter_id=request.matter_id,
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
async def list_matter_devices(property_id: UUID | None = None) -> list[MatterDeviceOut]:
    """List Matter devices."""
    if property_id:
        return [d for d in _devices.values() if d.property_id == property_id]
    return list(_devices.values())


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on Matter device."""
    if device_id not in _devices:
        return {"error": "Device not found"}
    return {"status": "turned_on"}


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off Matter device."""
    if device_id not in _devices:
        return {"error": "Device not found"}
    return {"status": "turned_off"}
