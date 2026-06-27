"""Device registry — CRUD on the devices table via SQLModel."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.tables import Device as DBDevice
from devices.spire import SpireDevice

logger = logging.getLogger(__name__)

# Same namespace + scheme as the cloud-poll path (devices.models), so a device
# saved here and the same device polled live resolve to ONE logical id.
_DEVICE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "spire:device")


def spire_device_id(vendor: str, vendor_id: str) -> uuid.UUID:
    """Deterministic logical id from the business identity (vendor + vendor_id)."""
    return uuid.uuid5(_DEVICE_NAMESPACE, f"{vendor}:{vendor_id}")


def _to_dict(d: DBDevice) -> dict[str, Any]:
    return {
        "id": str(d.id),
        "property_id": str(d.property_id) if d.property_id else None,
        "room_id": str(d.room_id) if d.room_id else None,
        "vendor": d.vendor,
        "vendor_id": d.vendor_id,
        "name": d.name,
        "model": d.model,
        "ip_address": d.ip_address,
        "mac": d.mac,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


async def list_devices(
    session: AsyncSession,
    property_id: str | None = None,
) -> list[dict[str, Any]]:
    stmt = select(DBDevice).order_by(DBDevice.created_at.desc())  # type: ignore[union-attr]
    if property_id:
        stmt = stmt.where(DBDevice.property_id == uuid.UUID(property_id))  # type: ignore[arg-type]
    result = await session.execute(stmt)
    return [_to_dict(row) for row in result.scalars().all()]


async def save_device(data: dict[str, Any], session: AsyncSession) -> dict[str, Any]:
    """Upsert a device, keyed on its business identity (vendor + vendor_id).

    Saving the same physical device twice updates the one row rather than creating
    a duplicate. Vendor-owned fields (model, ip, mac) refresh on every save; the
    user-owned ``name`` is preserved once set — the sync never clobbers a rename.
    """
    vendor = data["vendor"]
    vendor_id = data.get("vendor_id") or data.get("mac") or ""
    device_id = spire_device_id(vendor, vendor_id)

    device = await session.get(DBDevice, device_id)
    if device is not None:
        device.model = data.get("model") or device.model
        device.ip_address = data.get("ip") or device.ip_address
        device.mac = data.get("mac") or device.mac
        if data.get("property_id"):
            device.property_id = uuid.UUID(data["property_id"])
        if data.get("room_id"):
            device.room_id = uuid.UUID(data["room_id"])
    else:
        device = DBDevice(
            id=device_id,
            property_id=uuid.UUID(data["property_id"]) if data.get("property_id") else None,
            room_id=uuid.UUID(data["room_id"]) if data.get("room_id") else None,
            vendor=vendor,
            vendor_id=vendor_id,
            name=data["name"],
            model=data.get("model") or "",
            ip_address=data.get("ip") or "",
            mac=data.get("mac") or "",
        )
        session.add(device)

    await session.flush()
    await session.refresh(device)
    await session.commit()
    return _to_dict(device)


async def upsert_device(device: SpireDevice, session: AsyncSession) -> dict[str, Any]:
    """Insert or update a device from a SPIRE resource, keyed on its identity.

    The repository entry point for the sync pipeline. Vendor-owned fields refresh;
    the user's ``name`` is preserved on update — a re-sync never clobbers a rename.
    """
    device_id = uuid.UUID(device.identity.id)
    row = await session.get(DBDevice, device_id)
    if row is not None:
        row.model = device.vendor.model_number or row.model
        row.ip_address = device.connectivity.ip_address or row.ip_address
        row.mac = device.connectivity.mac or row.mac
        if device.placement.property_id:
            row.property_id = uuid.UUID(device.placement.property_id)
        if device.placement.room_id:
            row.room_id = uuid.UUID(device.placement.room_id)
    else:
        row = DBDevice(
            id=device_id,
            vendor=device.vendor.vendor,
            vendor_id=device.identity.identifier.value,
            name=device.label,
            model=device.vendor.model_number or "",
            ip_address=device.connectivity.ip_address or "",
            mac=device.connectivity.mac or "",
            property_id=(
                uuid.UUID(device.placement.property_id) if device.placement.property_id else None
            ),
            room_id=uuid.UUID(device.placement.room_id) if device.placement.room_id else None,
        )
        session.add(row)
    await session.flush()
    await session.refresh(row)
    await session.commit()
    return _to_dict(row)


async def get_device_by_id(device_id: str, session: AsyncSession) -> dict[str, Any] | None:
    device = await session.get(DBDevice, uuid.UUID(device_id))
    return _to_dict(device) if device else None


async def update_device(
    device_id: str, data: dict[str, Any], session: AsyncSession
) -> dict[str, Any]:
    device = await session.get(DBDevice, uuid.UUID(device_id))
    if not device:
        raise RuntimeError(f"Device {device_id} not found")
    for key, value in data.items():
        if hasattr(device, key):
            setattr(device, key, value)
    await session.commit()
    await session.refresh(device)
    return _to_dict(device)


async def delete_device(device_id: str, session: AsyncSession) -> None:
    await session.execute(sql_delete(DBDevice).where(DBDevice.id == uuid.UUID(device_id)))  # type: ignore[arg-type]
    await session.commit()


async def move_devices_to_null_room(room_id: str, session: AsyncSession) -> None:
    stmt = select(DBDevice).where(DBDevice.room_id == uuid.UUID(room_id))  # type: ignore[arg-type]
    result = await session.execute(stmt)
    for device in result.scalars().all():
        device.room_id = None
    await session.commit()


async def assign_device_room(
    device_id: str, room_id: str | None, session: AsyncSession
) -> dict[str, Any]:
    device = await session.get(DBDevice, uuid.UUID(device_id))
    if not device:
        raise RuntimeError(f"Device {device_id} not found")
    device.room_id = uuid.UUID(room_id) if room_id else None
    await session.commit()
    await session.refresh(device)
    return _to_dict(device)
