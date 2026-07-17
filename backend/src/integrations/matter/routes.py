"""Matter API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from integrations.matter.schemas import MatterDeviceIn, MatterDeviceOut

router = APIRouter(prefix="/integrations/matter", tags=["matter"])


@router.post("/devices")
async def add_matter_device(request: MatterDeviceIn) -> MatterDeviceOut:
    """Add a Matter device to a property."""
    raise NotImplementedError()


@router.get("/devices")
async def list_matter_devices(property_id: UUID | None = None) -> list[MatterDeviceOut]:
    """List Matter devices."""
    raise NotImplementedError()


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on Matter device."""
    raise NotImplementedError()


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off Matter device."""
    raise NotImplementedError()
