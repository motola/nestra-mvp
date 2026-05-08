"""Alert endpoints — list active alerts, dismiss an alert."""
from __future__ import annotations

from fastapi import APIRouter

from api.dependencies import SettingsDep
from models.alert import Alert
from services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[Alert])
async def list_alerts(settings: SettingsDep) -> list[Alert]:
    """Return all active (non-dismissed) alerts, newest first."""
    alerts = await alert_service.list_active_alerts(settings)
    if settings.demo_mode:
        from demo.alerts import get_demo_alerts
        demo_alerts = [Alert(**a) for a in get_demo_alerts() if not a.get("dismissed")]
        return alerts + demo_alerts
    return alerts


@router.patch("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str, settings: SettingsDep) -> dict[str, str]:
    """Mark an alert as dismissed."""
    await alert_service.dismiss_alert(alert_id, settings)
    return {"status": "dismissed", "alert_id": alert_id}
