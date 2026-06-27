"""Alert service — CRUD on the alerts table via SQLModel."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from alerts.models import Alert
from models.database import Alert as DBAlert

logger = logging.getLogger(__name__)


def _to_alert(row: DBAlert) -> Alert:
    return Alert(
        id=str(row.id),
        device_id=str(row.device_id),
        device_name=row.device_name or "Unknown Device",
        property_id=str(row.property_id) if row.property_id else "",
        property_name=row.property_name or "",
        type=row.type or "unknown",
        severity=row.severity or "info",  # type: ignore[arg-type]
        message=row.message or "",
        created_at=row.created_at,  # type: ignore[arg-type]
        dismissed=row.dismissed,
    )


async def list_active_alerts(session: AsyncSession) -> list[Alert]:
    stmt = (
        select(DBAlert)
        .where(DBAlert.dismissed == False)  # type: ignore[arg-type]  # noqa: E712
        .order_by(DBAlert.created_at.desc())  # type: ignore[union-attr]
    )
    result = await session.execute(stmt)
    return [_to_alert(row) for row in result.scalars().all()]


async def dismiss_alert(alert_id: str, session: AsyncSession) -> None:
    alert = await session.get(DBAlert, uuid.UUID(alert_id))
    if alert:
        alert.dismissed = True
        await session.commit()


async def get_alert_counts(session: AsyncSession) -> dict[str, int]:
    stmt = select(DBAlert).where(DBAlert.dismissed == False)  # type: ignore[arg-type]  # noqa: E712
    result = await session.execute(stmt)
    counts: dict[str, int] = {}
    for row in result.scalars().all():
        if row.property_id:
            pid = str(row.property_id)
            counts[pid] = counts.get(pid, 0) + 1
    return counts


async def create_alert(
    device_id: str,
    device_name: str,
    property_id: str,
    property_name: str,
    alert_type: str,
    severity: str,
    message: str,
    session: AsyncSession,
) -> None:
    alert = DBAlert(
        device_id=uuid.UUID(device_id),
        device_name=device_name,
        property_id=uuid.UUID(property_id) if property_id else None,
        property_name=property_name,
        type=alert_type,
        severity=severity,
        message=message,
        dismissed=False,
    )
    session.add(alert)
    await session.commit()
