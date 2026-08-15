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
    devices: list[DeviceResponse] = []

    # Aggregate from Shelly
    from integrations.shelly import routes as shelly_routes

    for shelly_device in shelly_routes._devices.values():
        if shelly_device.property_id == property_id:
            devices.append(
                DeviceResponse(
                    id=str(shelly_device.id),
                    name=shelly_device.name,
                    vendor="Shelly",
                    online=shelly_device.online,
                )
            )

    # Aggregate from Govee
    from integrations.govee import routes as govee_routes

    for govee_device in govee_routes._devices.values():
        if govee_device.property_id == property_id:
            devices.append(
                DeviceResponse(
                    id=str(govee_device.id),
                    name=govee_device.name,
                    vendor="Govee",
                    online=govee_device.online,
                )
            )

    # Aggregate from LIFX
    from integrations.lifx import routes as lifx_routes

    for lifx_device in lifx_routes._devices.values():
        if lifx_device.property_id == property_id:
            devices.append(
                DeviceResponse(
                    id=str(lifx_device.id),
                    name=lifx_device.name,
                    vendor="LIFX",
                    online=lifx_device.online,
                )
            )

    # Aggregate from Matter
    from integrations.matter import routes as matter_routes

    for matter_device in matter_routes._devices.values():
        if matter_device.property_id == property_id:
            devices.append(
                DeviceResponse(
                    id=str(matter_device.id),
                    name=matter_device.name,
                    vendor="Matter",
                    online=matter_device.online,
                )
            )

    return devices


# Include all integration routers
router.include_router(bluetooth_router)
router.include_router(august_router)
router.include_router(shelly_router)
router.include_router(govee_router)
router.include_router(lifx_router)
router.include_router(matter_router)
