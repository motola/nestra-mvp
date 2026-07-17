"""Property API routes - includes all integration routers."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from integrations.august import router as august_router
from integrations.bluetooth import router as bluetooth_router
from integrations.govee import router as govee_router
from integrations.lifx import router as lifx_router
from integrations.matter import router as matter_router
from integrations.shelly import router as shelly_router

router = APIRouter()


class DeviceResponse(BaseModel):
    """Unified device response."""

    id: str
    name: str
    vendor: str
    online: bool


@router.get("/properties/{property_id}/devices")
async def get_property_devices(property_id: UUID) -> list[DeviceResponse]:
    """Get all devices for a property across all integrations."""
    # TODO: Aggregate devices from all integration routers
    # For now, return empty list - will be populated by device sync service
    return []


# Include all integration routers
router.include_router(bluetooth_router)
router.include_router(august_router)
router.include_router(shelly_router)
router.include_router(govee_router)
router.include_router(lifx_router)
router.include_router(matter_router)
