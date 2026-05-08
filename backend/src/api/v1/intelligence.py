"""Portfolio intelligence endpoint — cross-property anomaly and insight summaries."""
from __future__ import annotations

from pydantic import BaseModel

from fastapi import APIRouter

from api.dependencies import SettingsDep

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


class IntelligenceItem(BaseModel):
    id: str
    property_id: str
    property_name: str
    type: str
    severity: str
    title: str
    detail: str
    generated_at: str
    metric: float | None = None
    unit: str | None = None


@router.get("/", response_model=list[IntelligenceItem])
async def list_intelligence(settings: SettingsDep) -> list[IntelligenceItem]:
    """Return portfolio-level intelligence items (anomalies, predictions, patterns)."""
    if settings.demo_mode:
        from demo.intelligence import get_demo_intelligence
        return [IntelligenceItem(**item) for item in get_demo_intelligence()]
    return []
