"""Shelly API routes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter

from integrations.shelly.adapter import ShellyAdapter
from integrations.shelly.schemas import ShellyDeviceIn, ShellyDeviceOut

router = APIRouter(prefix="/integrations/shelly", tags=["shelly"])

# Mock storage for devices - replace with DB later
_devices: dict[UUID, ShellyDeviceOut] = {}
_adapter = ShellyAdapter()


@router.post("/devices")
async def add_shelly_device(request: ShellyDeviceIn) -> ShellyDeviceOut:
    """Add a Shelly device to a property."""
    device_id = uuid4()
    device = ShellyDeviceOut(
        id=device_id,
        property_id=request.property_id,
        shelly_id=request.shelly_id,
        name=request.name,
        ip_address="192.168.1.100",  # TODO: Get from request
        online=True,
        raw_state={},
        last_sync=datetime.now(),
        created_at=datetime.now(),
    )
    _devices[device_id] = device
    return device


@router.get("/devices")
async def list_shelly_devices(property_id: UUID | None = None) -> list[ShellyDeviceOut]:
    """List Shelly devices."""
    if property_id:
        return [d for d in _devices.values() if d.property_id == property_id]
    return list(_devices.values())


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on Shelly device."""
    if device_id not in _devices:
        return {"error": "Device not found"}
    # TODO: Call adapter to turn on device
    return {"status": "turned_on"}


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off Shelly device."""
    if device_id not in _devices:
        return {"error": "Device not found"}
    # TODO: Call adapter to turn off device
    return {"status": "turned_off"}
