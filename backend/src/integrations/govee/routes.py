"""Govee API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from integrations.govee.schemas import GoveeDeviceIn, GoveeDeviceOut

router = APIRouter(prefix="/integrations/govee", tags=["govee"])


@router.post("/devices")
async def add_govee_device(request: GoveeDeviceIn) -> GoveeDeviceOut:
    """Add a Govee device to a property."""
    raise NotImplementedError()


@router.get("/devices")
async def list_govee_devices(property_id: UUID | None = None) -> list[GoveeDeviceOut]:
    """List Govee devices."""
    raise NotImplementedError()


@router.post("/devices/{device_id}/on")
async def turn_on_device(device_id: UUID) -> dict[str, str]:
    """Turn on Govee device."""
    raise NotImplementedError()


@router.post("/devices/{device_id}/off")
async def turn_off_device(device_id: UUID) -> dict[str, str]:
    """Turn off Govee device."""
    raise NotImplementedError()
