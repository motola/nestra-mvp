"""Shelly API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from integrations.shelly.schemas import ShellyDeviceIn, ShellyDeviceOut

router = APIRouter(prefix="/integrations/shelly", tags=["shelly"])


@router.post("/devices")
async def add_shelly_device(request: ShellyDeviceIn) -> ShellyDeviceOut:
    """Add a Shelly device to a property."""
    # TODO: Implement device creation
    raise NotImplementedError()


@router.get("/devices")
async def list_shelly_devices(property_id: UUID | None = None) -> list[ShellyDeviceOut]:
    """List Shelly devices."""
    # TODO: Implement device listing
    raise NotImplementedError()


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on Shelly device."""
    # TODO: Implement turn on
    raise NotImplementedError()


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off Shelly device."""
    # TODO: Implement turn off
    raise NotImplementedError()
