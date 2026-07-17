"""LIFX API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from integrations.lifx.schemas import LifxDeviceIn, LifxDeviceOut

router = APIRouter(prefix="/integrations/lifx", tags=["lifx"])


@router.post("/devices")
async def add_lifx_device(request: LifxDeviceIn) -> LifxDeviceOut:
    """Add a LIFX device to a property."""
    raise NotImplementedError()


@router.get("/devices")
async def list_lifx_devices(property_id: UUID | None = None) -> list[LifxDeviceOut]:
    """List LIFX devices."""
    raise NotImplementedError()


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on LIFX device."""
    raise NotImplementedError()


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off LIFX device."""
    raise NotImplementedError()
