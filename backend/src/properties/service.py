"""Property service — CRUD on the properties table via SQLModel."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import Settings
from models.database import (
    Alert as DBAlert,
)
from models.database import (
    Device as DBDevice,
)
from models.database import (
    Property as DBProperty,
)
from models.database import (
    Room as DBRoom,
)
from models.database import (
    StateHistory as DBStateHistory,
)
from properties.models import Property, PropertyCreate, PropertyStatus

logger = logging.getLogger(__name__)


def _row_to_property(
    row: DBProperty,
    device_count: int = 0,
    alert_count: int = 0,
    is_demo: bool = False,
) -> Property:
    status: PropertyStatus
    if alert_count == 0:
        status = "all_clear"
    elif alert_count <= 2:
        status = "needs_attention"
    else:
        status = "critical"
    return Property(
        id=str(row.id),
        name=row.name,
        address=row.address or "",
        organisation_id=str(row.organisation_id) if row.organisation_id else None,
        device_count=device_count,
        alert_count=alert_count,
        status=status,
        is_demo=is_demo,
    )


def _demo_properties() -> list[Property]:
    from demo.alerts import get_demo_alerts
    from demo.data import DEMO_PROPERTIES, _real_device_prop_counts, get_demo_devices_for_property

    demo_alert_counts: dict[str, int] = {}
    for a in get_demo_alerts():
        pid = a.get("property_id")
        if pid and not a.get("dismissed"):
            demo_alert_counts[pid] = demo_alert_counts.get(pid, 0) + 1

    result = []
    for p in DEMO_PROPERTIES:
        pid = p["id"]
        # Use real DB device count for properties with Supabase devices; demo count otherwise.
        real_count = _real_device_prop_counts.get(pid)
        device_count = (
            real_count if real_count is not None else len(get_demo_devices_for_property(pid))
        )
        ac = demo_alert_counts.get(pid, 0)
        status: PropertyStatus = (
            "all_clear" if ac == 0 else ("needs_attention" if ac <= 2 else "critical")
        )
        result.append(
            Property(
                id=pid,
                name=p["name"],
                address=p.get("address", ""),
                organisation_id=None,
                device_count=device_count,
                alert_count=ac,
                status=status,
                is_demo=True,
            )
        )
    return result


async def list_properties(session: AsyncSession, settings: Settings) -> list[Property]:
    from alerts.service import get_alert_counts
    from services.device_registry import list_devices

    real_props: list[Property] = []
    try:
        result = await session.execute(select(DBProperty).order_by(DBProperty.name))
        rows = list(result.scalars().all())

        # Always drop DB-seeded demo rows from the "real" set. Whether demo data
        # is shown at all is decided below by settings.demo_mode — so when demo
        # is gated off, these never leak through as if they were real.
        from demo.data import is_demo_property

        rows = [r for r in rows if not is_demo_property(str(r.id))]

        if rows:
            device_rows = await list_devices(session)
            alert_counts = await get_alert_counts(session)

            device_counts: dict[str, int] = {}
            for d in device_rows:
                pid = d.get("property_id")
                if pid:
                    device_counts[pid] = device_counts.get(pid, 0) + 1

            real_props = [
                _row_to_property(
                    row, device_counts.get(str(row.id), 0), alert_counts.get(str(row.id), 0)
                )
                for row in rows
            ]
    except Exception as exc:
        logger.warning("list_properties DB query failed: %s", exc)

    if settings.demo_mode:
        return real_props + _demo_properties()
    return real_props


async def get_property(
    property_id: str, session: AsyncSession, settings: Settings
) -> Property | None:
    if settings.demo_mode:
        from demo.data import DEMO_PROPERTIES, get_demo_devices_for_property, is_demo_property

        if is_demo_property(property_id):
            from demo.alerts import get_demo_alerts

            p = next((p for p in DEMO_PROPERTIES if p["id"] == property_id), None)
            if not p:
                return None
            devices = get_demo_devices_for_property(property_id)
            ac = sum(
                1
                for a in get_demo_alerts()
                if a["property_id"] == property_id and not a.get("dismissed")
            )
            status: PropertyStatus = (
                "all_clear" if ac == 0 else ("needs_attention" if ac <= 2 else "critical")
            )
            return Property(
                id=p["id"],
                name=p["name"],
                address=p.get("address", ""),
                organisation_id=None,
                device_count=len(devices),
                alert_count=ac,
                status=status,
                is_demo=True,
            )

    try:
        result = await session.execute(
            select(DBProperty).where(DBProperty.id == uuid.UUID(property_id))  # type: ignore[arg-type]
        )
        row = result.scalars().first()
    except Exception as exc:
        logger.warning("get_property DB query failed: %s", exc)
        return None
    if not row:
        return None

    from alerts.service import get_alert_counts
    from services.device_registry import list_devices

    device_rows = await list_devices(session, property_id=property_id)
    alert_counts = await get_alert_counts(session)
    return _row_to_property(row, len(device_rows), alert_counts.get(property_id, 0))


async def delete_property(property_id: str, session: AsyncSession) -> None:
    """Cascade-delete property: state_history + alerts → devices → rooms → property."""
    pid = uuid.UUID(property_id)

    result = await session.execute(select(DBDevice).where(DBDevice.property_id == pid))  # type: ignore[arg-type]
    device_ids = [d.id for d in result.scalars().all()]

    for did in device_ids:
        await session.execute(sql_delete(DBStateHistory).where(DBStateHistory.device_id == did))  # type: ignore[arg-type]
        await session.execute(sql_delete(DBAlert).where(DBAlert.device_id == did))  # type: ignore[arg-type]

    await session.execute(sql_delete(DBDevice).where(DBDevice.property_id == pid))  # type: ignore[arg-type]
    await session.execute(sql_delete(DBRoom).where(DBRoom.property_id == pid))  # type: ignore[arg-type]
    await session.execute(sql_delete(DBProperty).where(DBProperty.id == pid))  # type: ignore[arg-type]
    await session.commit()


async def create_property(data: PropertyCreate, session: AsyncSession) -> Property:
    raise NotImplementedError("Property creation not yet implemented")
