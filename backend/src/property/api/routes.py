"""Property API routes - includes all integration routers."""

from fastapi import APIRouter

from integrations.bluetooth import router as bluetooth_router
from integrations.ecobee import router as ecobee_router
from integrations.hikvision import router as hikvision_router
from integrations.tplink import router as tplink_router

router = APIRouter()

router.include_router(bluetooth_router)
router.include_router(ecobee_router)
router.include_router(hikvision_router)
router.include_router(tplink_router)
