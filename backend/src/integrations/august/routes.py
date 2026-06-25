"""August Smart Lock API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from dependencies import SettingsDep
from integrations.august.schemas import (
    AugustLockIn,
    AugustLockOut,
    AugustStatusResponse,
)

router = APIRouter(prefix="/integrations/august", tags=["property"])

# ─── Mock storage (replace with real DB when wired) ────────────────────────────

_MOCK_LOCKS: dict[UUID, AugustLockOut] = {}
_MOCK_INTEGRATIONS: dict[str, UUID] = {}  # vendor → integration_id


@router.post("/locks", response_model=AugustLockOut, status_code=status.HTTP_201_CREATED)
async def add_lock(
    body: AugustLockIn,
    settings: SettingsDep,
) -> AugustLockOut:
    """Add an August Smart Lock to a property."""
    # Check if lock already added
    existing = next(
        (lock for lock in _MOCK_LOCKS.values() if lock.lock_id == body.lock_id),
        None,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lock already added to this property",
        )

    # Get or create August integration
    integration_id = _MOCK_INTEGRATIONS.get("august", uuid4())
    if "august" not in _MOCK_INTEGRATIONS:
        _MOCK_INTEGRATIONS["august"] = integration_id

    # Create lock
    lock_id = uuid4()
    lock = AugustLockOut(
        id=lock_id,
        property_id=body.property_id,
        lock_id=body.lock_id,
        name=body.name,
        location=body.location,
        battery_level=body.battery_level,
        is_locked=body.is_locked,
        is_online=True,
        model=body.model,
        last_sync=datetime.now(tz=UTC),
        created_at=datetime.now(tz=UTC),
    )
    _MOCK_LOCKS[lock_id] = lock

    return lock


@router.get("/locks", response_model=list[AugustLockOut])
async def list_locks(
    property_id: UUID | None = None,
    settings: SettingsDep | None = None,
) -> list[AugustLockOut]:
    """List August Smart Locks, optionally filtered by property."""
    locks = list(_MOCK_LOCKS.values())
    if property_id:
        locks = [lock for lock in locks if lock.property_id == property_id]

    return locks


@router.post("/locks/{lock_id}/lock", response_model=AugustStatusResponse)
async def lock_device(
    lock_id: UUID,
    settings: SettingsDep,
) -> AugustStatusResponse:
    """Lock an August Smart Lock."""
    if lock_id not in _MOCK_LOCKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lock not found",
        )

    lock = _MOCK_LOCKS[lock_id]
    lock.is_locked = True
    lock.last_sync = datetime.now(tz=UTC)
    _MOCK_LOCKS[lock_id] = lock

    return AugustStatusResponse(message=f"Lock '{lock.name}' is now locked")


@router.post("/locks/{lock_id}/unlock", response_model=AugustStatusResponse)
async def unlock_device(
    lock_id: UUID,
    settings: SettingsDep,
) -> AugustStatusResponse:
    """Unlock an August Smart Lock."""
    if lock_id not in _MOCK_LOCKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lock not found",
        )

    lock = _MOCK_LOCKS[lock_id]
    lock.is_locked = False
    lock.last_sync = datetime.now(tz=UTC)
    _MOCK_LOCKS[lock_id] = lock

    return AugustStatusResponse(message=f"Lock '{lock.name}' is now unlocked")


@router.delete("/locks/{lock_id}", response_model=AugustStatusResponse)
async def remove_lock(
    lock_id: UUID,
    settings: SettingsDep,
) -> AugustStatusResponse:
    """Remove an August Smart Lock."""
    if lock_id not in _MOCK_LOCKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lock not found",
        )

    lock = _MOCK_LOCKS.pop(lock_id)

    return AugustStatusResponse(message=f"Lock '{lock.name}' removed")
