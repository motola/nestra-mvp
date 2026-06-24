"""Property API routes - includes all integration routers."""

from fastapi import APIRouter

from integrations.bluetooth import router as bluetooth_router

router = APIRouter()

# Include all integration routers
router.include_router(bluetooth_router)
