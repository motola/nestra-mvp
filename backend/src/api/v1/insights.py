"""Insight endpoints — AI-generated device analysis."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.dependencies import SettingsDep
from models.insight import Insight
from services import device_service, insight_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{device_id}", response_model=Insight)
async def get_device_insight(device_id: str, settings: SettingsDep) -> Insight:
    """
    Return a plain English AI insight for a device.
    Demo devices return pre-written insights. Real devices are cached in Redis for 15 minutes.
    """
    if settings.demo_mode and device_id.startswith("demo-"):
        from demo.insights import get_demo_insight
        insight = get_demo_insight(device_id)
        if not insight:
            raise HTTPException(status_code=404, detail="Device not found")
        return Insight(**insight)

    device = await device_service.get_device(device_id, settings)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return await insight_service.get_insight(device, history=[], settings=settings)
