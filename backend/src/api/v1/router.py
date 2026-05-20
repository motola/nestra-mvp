"""Registers all v1 route modules onto a single APIRouter."""

from __future__ import annotations

from fastapi import APIRouter

from api.v1 import alerts, chat, devices, insights, integrations, intelligence, properties, rooms

router = APIRouter(prefix="/api/v1")

router.include_router(properties.router)
router.include_router(devices.router)
router.include_router(rooms.router)
router.include_router(alerts.router)
router.include_router(insights.router)
router.include_router(integrations.router)
router.include_router(chat.router)
router.include_router(intelligence.router)
