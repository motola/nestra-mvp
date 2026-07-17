"""Property API routes - includes all integration routers."""

from fastapi import APIRouter

from integrations.august import router as august_router
from integrations.bluetooth import router as bluetooth_router
from integrations.govee import router as govee_router
from integrations.lifx import router as lifx_router
from integrations.matter import router as matter_router
from integrations.shelly import router as shelly_router

router = APIRouter()

# Include all integration routers
router.include_router(bluetooth_router)
router.include_router(august_router)
router.include_router(shelly_router)
router.include_router(govee_router)
router.include_router(lifx_router)
router.include_router(matter_router)
