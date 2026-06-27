"""State history service — records and queries device state change events via SQLModel."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.tables import StateHistory as DBStateHistory

logger = logging.getLogger(__name__)


async def record_state_change(
    device_id: str,
    event_type: str,
    session: AsyncSession,
    property_id: str | None = None,
    value: str | None = None,
) -> None:
    try:
        row = DBStateHistory(
            device_id=uuid.UUID(device_id),
            event_type=event_type,
            property_id=uuid.UUID(property_id) if property_id else None,
            value=value,
        )
        session.add(row)
        await session.commit()
    except Exception as exc:
        logger.warning("record_state_change failed for %s: %s", device_id, exc)
        await session.rollback()


async def get_power_history(
    device_id: str,
    session: AsyncSession,
) -> list[dict[str, Any]]:
    since = datetime.now(UTC) - timedelta(hours=24)
    stmt = (
        select(DBStateHistory)
        .where(DBStateHistory.device_id == uuid.UUID(device_id))  # type: ignore[arg-type]
        .where(DBStateHistory.event_type == "power_reading")  # type: ignore[arg-type]
        .where(DBStateHistory.recorded_at >= since)  # type: ignore[operator, arg-type]
        .order_by(DBStateHistory.recorded_at.asc())  # type: ignore[union-attr]
        .limit(1440)
    )
    result = await session.execute(stmt)
    return [
        {
            "recorded_at": row.recorded_at.isoformat() if row.recorded_at else None,
            "value": row.value,
        }
        for row in result.scalars().all()
    ]


async def delete_device_history(device_id: str, session: AsyncSession) -> None:
    await session.execute(
        sql_delete(DBStateHistory).where(
            DBStateHistory.device_id == uuid.UUID(device_id)  # type: ignore[arg-type]
        )
    )
    await session.commit()


async def get_device_history(
    device_id: str,
    session: AsyncSession,
    limit: int = 50,
) -> list[dict[str, Any]]:
    stmt = (
        select(DBStateHistory)
        .where(DBStateHistory.device_id == uuid.UUID(device_id))  # type: ignore[arg-type]
        .where(DBStateHistory.event_type != "power_reading")  # type: ignore[arg-type]
        .order_by(DBStateHistory.recorded_at.desc())  # type: ignore[union-attr]
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "device_id": str(r.device_id),
            "property_id": str(r.property_id) if r.property_id else None,
            "event_type": r.event_type,
            "value": r.value,
            "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
        }
        for r in rows
    ]
