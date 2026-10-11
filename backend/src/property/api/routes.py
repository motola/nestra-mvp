"""Property API routes - includes all integration routers."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from db import SessionLocal, org_scope
from dependencies import OrgDep
from integrations.august import router as august_router
from integrations.lifx import router as lifx_router
from integrations.matter import router as matter_router
from integrations.shelly import router as shelly_router
from occupancy.api.routes import router as occupancy_router
from property.api.access_routes import router as access_router
from property.api.capability_routes import router as capability_router
from property.api.command_routes import router as command_router
from property.api.schemas import DeviceRead
from property.persistence.device_repository import DeviceRepository
from property.persistence.property_repository import PropertyRepository

router = APIRouter()


@router.get("/properties/{property_id}/devices", response_model=list[DeviceRead])
async def get_property_devices(property_id: UUID, organization_id: OrgDep) -> list[DeviceRead]:
    """Return persisted devices for a property in the authenticated tenant."""
    async with SessionLocal() as db, org_scope(db, organization_id):
        property_obj = await PropertyRepository(db).get_by_id(property_id)
        if not property_obj or property_obj.organization_id != organization_id:
            raise HTTPException(status_code=404, detail="Property not found")
        devices = await DeviceRepository(db).find_by_property(property_id)
        return [DeviceRead.model_validate(device) for device in devices]


# Include all integration routers
router.include_router(access_router)
router.include_router(capability_router)
router.include_router(command_router)
router.include_router(occupancy_router)
router.include_router(august_router)
router.include_router(shelly_router)
router.include_router(lifx_router)
router.include_router(matter_router)
