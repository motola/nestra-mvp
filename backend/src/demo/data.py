"""
Demo data for Alphacon AI.

On startup (when DEMO_MODE=true), call ensure_demo_seeded(session) from the
lifespan. It seeds properties and rooms into the database if they don't exist,
then builds the in-memory device list with real UUIDs. All lookup helpers below
use those real UUIDs once seeding is complete.

If the database is unavailable, deterministic UUID5 stubs are used so IDs stay
stable across restarts in local-only mode.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

# ── Raw seed definitions (no hardcoded IDs) ────────────────────────────────────

_PROP_SEEDS: list[dict[str, Any]] = [
    {"name": "14 Aldgate Court", "address": "14 Aldgate Court, London, E1 7QX"},
    {"name": "Flat 3, Brunswick House", "address": "Brunswick House, Manchester, M2 4QQ"},
    {"name": "Room 7, The Cedars HMO", "address": "42 Cedar Road, Birmingham, B15 2TT"},
    {"name": "The Annexe", "address": "22 Riverside Walk, Bristol, BS1 5SB"},
    {"name": "Oak House", "address": "5 Oak Lane, Leeds, LS6 2AA"},
    {"name": "Riverside Flat", "address": "41 Riverside Drive, London, SE1 7PB"},
]

_ROOM_SEEDS: dict[str, list[str]] = {
    "14 Aldgate Court": ["Living Room", "Kitchen", "Master Bedroom", "Second Bedroom", "Bathroom"],
    "Flat 3, Brunswick House": ["Hallway", "Living Room", "Kitchen", "Bedroom", "Bathroom"],
    "Room 7, The Cedars HMO": ["Boiler Room", "Kitchen", "Entry", "Living Room"],
    "The Annexe": ["Bedroom", "Kitchen", "Bathroom", "Entry"],
    "Oak House": ["Living Room", "Kitchen", "Bedroom 1", "Bedroom 2"],
    "Riverside Flat": ["Living Room", "Kitchen", "Bedroom", "Bathroom"],
}

# _vid is the stable vendor identifier used as a lookup key for alerts / history
_DEVICE_SEEDS: list[dict[str, Any]] = [
    # ── 14 Aldgate Court ──
    {
        "_prop": "14 Aldgate Court",
        "_room": "Living Room",
        "_vid": "demo-dev-mc-001",
        "name": "Smart Plug (TV)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 87.0,
    },
    {
        "_prop": "14 Aldgate Court",
        "_room": "Living Room",
        "_vid": "demo-dev-mc-002",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": True},
    },
    {
        "_prop": "14 Aldgate Court",
        "_room": "Kitchen",
        "_vid": "demo-dev-mc-003",
        "name": "Fridge Monitor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 4.2,
    },
    {
        "_prop": "14 Aldgate Court",
        "_room": "Kitchen",
        "_vid": "demo-dev-mc-004",
        "name": "Smart Plug (Kettle)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": False},
        "power": 0.0,
    },
    {
        "_prop": "14 Aldgate Court",
        "_room": "Kitchen",
        "_vid": "demo-dev-mc-005",
        "name": "Leak Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "leak_detected": False,
    },
    {
        "_prop": "14 Aldgate Court",
        "_room": "Master Bedroom",
        "_vid": "demo-dev-mc-006",
        "name": "Temperature Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 19.8,
        "humidity": 52.0,
    },
    {
        "_prop": "14 Aldgate Court",
        "_room": "Master Bedroom",
        "_vid": "demo-dev-mc-007",
        "name": "Smart Plug (Heater)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": False},
        "power": 0.0,
    },
    # ── Flat 3, Brunswick House ──
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Hallway",
        "_vid": "demo-dev-bh-001",
        "name": "Smart Lock",
        "vendor": "demo",
        "model": "Demo Lock",
        "type": "lock",
        "online": True,
        "state": {"locked": True},
    },
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Hallway",
        "_vid": "demo-dev-bh-002",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": False},
    },
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Living Room",
        "_vid": "demo-dev-bh-003",
        "name": "Smart Plug",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 340.0,
    },
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Living Room",
        "_vid": "demo-dev-bh-004",
        "name": "Temperature Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 22.1,
        "humidity": 48.0,
    },
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Kitchen",
        "_vid": "demo-dev-bh-005",
        "name": "Fridge Monitor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 3.8,
    },
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Kitchen",
        "_vid": "demo-dev-bh-006",
        "name": "Leak Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "leak_detected": False,
    },
    {
        "_prop": "Flat 3, Brunswick House",
        "_room": "Bathroom",
        "_vid": "demo-dev-bh-007",
        "name": "Humidity Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "humidity": 78.0,
        "temperature": 21.0,
    },
    # ── Room 7, The Cedars HMO ──
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Boiler Room",
        "_vid": "demo-dev-cl-001",
        "name": "Temperature Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 68.0,
    },
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Boiler Room",
        "_vid": "demo-dev-cl-002",
        "name": "Smart Plug",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 2400.0,
    },
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Kitchen",
        "_vid": "demo-dev-cl-003",
        "name": "Fridge Monitor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 5.1,
    },
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Kitchen",
        "_vid": "demo-dev-cl-004",
        "name": "Leak Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "leak_detected": False,
    },
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Kitchen",
        "_vid": "demo-dev-cl-005",
        "name": "Smart Plug (Dishwasher)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 1200.0,
    },
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Entry",
        "_vid": "demo-dev-cl-006",
        "name": "Smart Lock",
        "vendor": "demo",
        "model": "Demo Lock",
        "type": "lock",
        "online": True,
        "state": {"locked": False},
    },
    {
        "_prop": "Room 7, The Cedars HMO",
        "_room": "Entry",
        "_vid": "demo-dev-cl-007",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": True},
    },
    # ── The Annexe ──
    {
        "_prop": "The Annexe",
        "_room": "Bedroom",
        "_vid": "demo-dev-ta-001",
        "name": "Temperature Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 17.2,
    },
    {
        "_prop": "The Annexe",
        "_room": "Bedroom",
        "_vid": "demo-dev-ta-002",
        "name": "Smart Plug (Electric Blanket)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 60.0,
    },
    {
        "_prop": "The Annexe",
        "_room": "Kitchen",
        "_vid": "demo-dev-ta-003",
        "name": "Smart Plug (Fridge)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 45.0,
    },
    {
        "_prop": "The Annexe",
        "_room": "Kitchen",
        "_vid": "demo-dev-ta-004",
        "name": "Leak Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "leak_detected": True,
    },
    {
        "_prop": "The Annexe",
        "_room": "Entry",
        "_vid": "demo-dev-ta-005",
        "name": "Smart Lock",
        "vendor": "demo",
        "model": "Demo Lock",
        "type": "lock",
        "online": True,
        "state": {"locked": True},
    },
    {
        "_prop": "The Annexe",
        "_room": "Entry",
        "_vid": "demo-dev-ta-006",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": False},
    },
    # ── Oak House ──
    {
        "_prop": "Oak House",
        "_room": "Living Room",
        "_vid": "demo-dev-oh-001",
        "name": "Smart TV Plug",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 120.0,
    },
    {
        "_prop": "Oak House",
        "_room": "Living Room",
        "_vid": "demo-dev-oh-002",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": True},
    },
    {
        "_prop": "Oak House",
        "_room": "Kitchen",
        "_vid": "demo-dev-oh-003",
        "name": "Fridge Monitor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 4.5,
    },
    {
        "_prop": "Oak House",
        "_room": "Kitchen",
        "_vid": "demo-dev-oh-004",
        "name": "Smart Plug",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 890.0,
    },
    {
        "_prop": "Oak House",
        "_room": "Bedroom 1",
        "_vid": "demo-dev-oh-005",
        "name": "Temperature Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 20.3,
        "humidity": 55.0,
    },
    {
        "_prop": "Oak House",
        "_room": "Bedroom 2",
        "_vid": "demo-dev-oh-006",
        "name": "Smart Plug (Laptop)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 65.0,
    },
    {
        "_prop": "Oak House",
        "_room": "Bedroom 2",
        "_vid": "demo-dev-oh-007",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": False},
    },
    # ── Riverside Flat ──
    {
        "_prop": "Riverside Flat",
        "_room": "Living Room",
        "_vid": "demo-dev-rf-001",
        "name": "Smart Plug",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 1840.0,
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Living Room",
        "_vid": "demo-dev-rf-002",
        "name": "Smart Lock",
        "vendor": "demo",
        "model": "Demo Lock",
        "type": "lock",
        "online": True,
        "state": {"locked": True},
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Living Room",
        "_vid": "demo-dev-rf-003",
        "name": "Motion Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {"motion": True},
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Kitchen",
        "_vid": "demo-dev-rf-004",
        "name": "Fridge Monitor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 3.2,
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Kitchen",
        "_vid": "demo-dev-rf-005",
        "name": "Leak Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "leak_detected": False,
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Bedroom",
        "_vid": "demo-dev-rf-006",
        "name": "Temperature Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "temperature": 21.5,
        "humidity": 50.0,
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Bedroom",
        "_vid": "demo-dev-rf-007",
        "name": "Smart Plug (AC)",
        "vendor": "demo",
        "model": "Demo Plug",
        "type": "plug",
        "online": True,
        "state": {"on": True},
        "power": 950.0,
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Bathroom",
        "_vid": "demo-dev-rf-008",
        "name": "Humidity Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "humidity": 65.0,
    },
    {
        "_prop": "Riverside Flat",
        "_room": "Bathroom",
        "_vid": "demo-dev-rf-009",
        "name": "Leak Sensor",
        "vendor": "demo",
        "model": "Demo Sensor",
        "type": "sensor",
        "online": True,
        "state": {},
        "leak_detected": False,
    },
]

# ── Runtime state (populated by ensure_demo_seeded) ───────────────────────────

# Maps: "prop:NAME" → uuid, "room:PROP/ROOM" → uuid, "dev:VID" → uuid
_demo_id_map: dict[str, str] = {}
_demo_prop_uuids: set[str] = set()
_demo_dev_uuids: set[str] = set()
# Properties that have real Supabase devices — demo devices are NOT generated for these.
# device_count comes from DB instead of in-memory DEMO_DEVICES.
_real_device_prop_counts: dict[str, int] = {}  # prop_id → real device count

DEMO_PROPERTIES: list[dict[str, Any]] = []
DEMO_DEVICES: list[dict[str, Any]] = []

_devices_by_id: dict[str, dict[str, Any]] = {}
_devices_by_property: dict[str, list[dict[str, Any]]] = {}
_rooms_by_property: dict[str, list[dict[str, Any]]] = {}

_seeded = False

# Fixed namespace for deterministic stub UUIDs (used when DB is not available)
_DEMO_NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


# ── Seeding ───────────────────────────────────────────────────────────────────


async def ensure_demo_seeded(session: AsyncSession) -> None:
    global _seeded
    if _seeded:
        return
    logger.info("Demo: seeding via SQLModel session (no Supabase REST client)...")
    try:
        await _seed_db(session)
        logger.info("Demo: DB seed complete")
    except Exception as exc:
        logger.warning(
            "Demo: DB seed failed (%s) — check DATABASE_URL / Supabase IP allowlist. "
            "Falling back to deterministic stubs.",
            exc,
        )
        if not _seeded:
            _seed_stubs()
    _seeded = True
    logger.info("Demo: ready — %d properties, %d devices", len(DEMO_PROPERTIES), len(DEMO_DEVICES))


def _build_dev(
    seed: dict[str, Any], dev_id: str, vid: str, prop_id: str, room_id: str | None
) -> dict[str, Any]:
    return {
        "id": dev_id,
        "property_id": prop_id,
        "room_id": room_id,
        "vendor": seed["vendor"],
        "vendor_id": vid,
        "name": seed["name"],
        "model": seed.get("model"),
        "type": seed["type"],
        "online": seed.get("online", True),
        "state": dict(seed.get("state", {})),
        "power": seed.get("power"),
        "temperature": seed.get("temperature"),
        "humidity": seed.get("humidity"),
        "leak_detected": seed.get("leak_detected"),
        "ip_address": None,
        "mac": None,
    }


def _finalise_devices() -> None:
    for dev in DEMO_DEVICES:
        _devices_by_id[dev["id"]] = dev
        _devices_by_property.setdefault(dev["property_id"], []).append(dev)


def _seed_stubs() -> None:
    """Generate deterministic stub UUIDs for local-only mode (no database)."""
    for prop_seed in _PROP_SEEDS:
        name = prop_seed["name"]
        prop_id = str(uuid.uuid5(_DEMO_NS, f"prop:{name}"))
        _demo_id_map[f"prop:{name}"] = prop_id
        _demo_prop_uuids.add(prop_id)
        DEMO_PROPERTIES.append({"id": prop_id, "name": name, "address": prop_seed["address"]})

        for room_name in _ROOM_SEEDS.get(name, []):
            room_id = str(uuid.uuid5(_DEMO_NS, f"room:{name}/{room_name}"))
            _demo_id_map[f"room:{name}/{room_name}"] = room_id
            _rooms_by_property.setdefault(prop_id, []).append(
                {"id": room_id, "property_id": prop_id, "name": room_name}
            )

    for dev_seed in _DEVICE_SEEDS:
        prop_name = dev_seed["_prop"]
        room_name = dev_seed["_room"]
        vid = dev_seed["_vid"]
        dev_prop_id: str | None = _demo_id_map.get(f"prop:{prop_name}")
        dev_room_id: str | None = _demo_id_map.get(f"room:{prop_name}/{room_name}")
        if not dev_prop_id:
            continue
        dev_id = str(uuid.uuid5(_DEMO_NS, f"dev:{vid}"))
        _demo_id_map[f"dev:{vid}"] = dev_id
        _demo_dev_uuids.add(dev_id)
        DEMO_DEVICES.append(_build_dev(dev_seed, dev_id, vid, dev_prop_id, dev_room_id))

    _finalise_devices()


async def _seed_db(session: AsyncSession) -> None:
    from models.database import Organisation as DBOrg
    from models.database import Property as DBProperty
    from models.database import Room as DBRoom

    logger.info("Demo: connecting to PostgreSQL via asyncpg...")
    result = await session.execute(select(DBOrg).limit(1))
    org = result.scalars().first()
    if not org:
        raise RuntimeError("No organisation found in database")
    org_id = org.id

    # Fetch all existing properties once
    result = await session.execute(select(DBProperty))
    existing_props = {row.name: str(row.id) for row in result.scalars().all()}

    for prop_seed in _PROP_SEEDS:
        name = prop_seed["name"]

        if name in existing_props:
            prop_id = existing_props[name]
        else:
            new_prop = DBProperty(
                organisation_id=org_id,
                name=name,
                address=prop_seed["address"],
            )
            session.add(new_prop)
            await session.flush()
            await session.refresh(new_prop)
            prop_id = str(new_prop.id)
            logger.info("Demo: created property '%s' (%s)", name, prop_id)

        _demo_id_map[f"prop:{name}"] = prop_id
        _demo_prop_uuids.add(prop_id)
        DEMO_PROPERTIES.append({"id": prop_id, "name": name, "address": prop_seed["address"]})

        # Fetch existing rooms for this property
        result = await session.execute(
            select(DBRoom).where(DBRoom.property_id == uuid.UUID(prop_id))  # type: ignore[arg-type]
        )
        existing_rooms = {row.name: str(row.id) for row in result.scalars().all()}

        for room_name in _ROOM_SEEDS.get(name, []):
            if room_name in existing_rooms:
                room_id = existing_rooms[room_name]
            else:
                new_room = DBRoom(
                    property_id=uuid.UUID(prop_id),
                    name=room_name,
                )
                session.add(new_room)
                await session.flush()
                await session.refresh(new_room)
                room_id = str(new_room.id)

            _demo_id_map[f"room:{name}/{room_name}"] = room_id
            _rooms_by_property.setdefault(prop_id, []).append(
                {"id": room_id, "property_id": prop_id, "name": room_name}
            )

    await session.commit()

    # Find which properties already have real Supabase devices — skip demo devices for those.
    from models.database import Device as DBDevice

    result = await session.execute(select(DBDevice.property_id))  # type: ignore[call-overload]
    for (pid,) in result.all():
        if pid:
            s = str(pid)
            _real_device_prop_counts[s] = _real_device_prop_counts.get(s, 0) + 1

    # Build in-memory device list — only for demo-only properties (no real devices)
    for dev_seed in _DEVICE_SEEDS:
        prop_name = dev_seed["_prop"]
        room_name = dev_seed["_room"]
        vid = dev_seed["_vid"]
        dev_prop_id: str | None = _demo_id_map.get(f"prop:{prop_name}")
        dev_room_id: str | None = _demo_id_map.get(f"room:{prop_name}/{room_name}")
        if not dev_prop_id:
            continue
        if dev_prop_id in _real_device_prop_counts:
            continue  # property has real Supabase devices — don't overlay demo devices
        dev_id = str(uuid.uuid4())
        _demo_id_map[f"dev:{vid}"] = dev_id
        _demo_dev_uuids.add(dev_id)
        DEMO_DEVICES.append(_build_dev(dev_seed, dev_id, vid, dev_prop_id, dev_room_id))

    _finalise_devices()


# ── Lookup helpers ─────────────────────────────────────────────────────────────


def is_demo_property(property_id: str) -> bool:
    return property_id in _demo_prop_uuids


def is_demo_device(device_id: str) -> bool:
    return device_id in _demo_dev_uuids


def get_demo_device(device_id: str) -> dict[str, Any] | None:
    return _devices_by_id.get(device_id)


def get_demo_devices_for_property(property_id: str) -> list[dict[str, Any]]:
    return _devices_by_property.get(property_id, [])


def get_demo_rooms(property_id: str) -> list[dict[str, Any]]:
    return _rooms_by_property.get(property_id, [])


def demo_device_as_saved(d: dict[str, Any]) -> dict[str, Any]:
    """Convert a demo device dict to the SavedDevice wire format."""
    return {
        "id": d["id"],
        "property_id": d["property_id"],
        "room_id": d.get("room_id"),
        "vendor": d["vendor"],
        "vendor_id": d.get("vendor_id", d["id"]),
        "name": d["name"],
        "model": d.get("model"),
        "ip_address": None,
        "mac": None,
        "created_at": "2024-01-01T00:00:00Z",
    }


def demo_device_as_alphacon(d: dict[str, Any]) -> dict[str, Any]:
    """Convert a demo device dict to the AlphaconDevice wire format."""
    return {
        "id": d["id"],
        "vendor_id": d.get("vendor_id", d["id"]),
        "vendor": d["vendor"],
        "name": d["name"],
        "type": d.get("type", "plug"),
        "online": d.get("online", True),
        "controllable": d.get("type") == "plug",
        "state": d.get("state", {}),
        "power_draw": d.get("power"),
        "temperature": d.get("temperature"),
        "humidity": d.get("humidity"),
        "leak_detected": d.get("leak_detected"),
        "property_id": d["property_id"],
        "room_id": d.get("room_id"),
        "last_seen": datetime.utcnow().isoformat(),
        "supported_commands": ["turn_on", "turn_off"] if d.get("type") == "plug" else [],
    }


def demo_device_state(d: dict[str, Any]) -> dict[str, Any]:
    """Return state response for a demo device."""
    return {
        "device_id": d["id"],
        "on": d.get("state", {}).get("on", False),
        "power": d.get("power", 0.0),
        "voltage": 238.0,
        "current": round(d.get("power", 0.0) / 238.0, 3),
        "energy": round(d.get("power", 0.0) * 8 / 1000, 2),
        "online": d.get("online", True),
    }
