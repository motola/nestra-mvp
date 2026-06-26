"""Property API routes - includes all integration routers."""

from fastapi import APIRouter

from integrations.august import router as august_router
from integrations.bluetooth import router as bluetooth_router

router = APIRouter()

# Include all integration routers
router.include_router(bluetooth_router)
router.include_router(august_router)
