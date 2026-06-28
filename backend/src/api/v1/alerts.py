"""Alert endpoints — list active alerts, dismiss an alert."""

from __future__ import annotations

from fastapi import APIRouter

from alerts import service as alert_service
from alerts.models import Alert
from api.dependencies import SessionDep, SettingsDep
from shared.pagination import PageDep, paginate

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[Alert])
async def list_alerts(settings: SettingsDep, session: SessionDep, page: PageDep) -> list[Alert]:
    """Return active (non-dismissed) alerts, newest first. Supports ?limit/?offset."""
    alerts = await alert_service.list_active_alerts(session)
    if settings.demo_mode:
        from demo.alerts import get_demo_alerts

        demo_alerts = [Alert(**a) for a in get_demo_alerts() if not a.get("dismissed")]
        alerts = alerts + demo_alerts
    return paginate(alerts, page)


@router.patch("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str, session: SessionDep) -> dict[str, str]:
    """Mark an alert as dismissed."""
    await alert_service.dismiss_alert(alert_id, session)
    return {"status": "dismissed", "alert_id": alert_id}
