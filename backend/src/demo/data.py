"""
Demo data for Alphacon AI.

On startup (when DEMO_MODE=true), call ensure_demo_seeded(settings) from the
lifespan. It seeds properties and rooms into Supabase if they don't exist, then
builds the in-memory device list with real UUIDs. All lookup helpers below use
those real UUIDs once seeding is complete.

If Supabase is not configured, deterministic UUID5 stubs are used so IDs stay
stable across restarts in local-only mode.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

import httpx

from config import Settings

logger = logging.getLogger(__name__)

# ── Raw seed definitions (no hardcoded IDs) ────────────────────────────────────

_PROP_SEEDS: list[dict] = [
    {"name": "Maple Court",    "address": "14 Maple Street, Leeds, LS1 1AA"},
    {"name": "Brunswick House","address": "Flat 3, Brunswick House, Manchester, M2 4QQ"},
    {"name": "Cedar Lodge",    "address": "8 Cedar Road, Birmingham, B15 2TT"},
    {"name": "The Annexe",     "address": "22 Riverside Walk, Bristol, BS1 5SB"},
    {"name": "Oak House",      "address": "5 Oak Lane, Leeds, LS6 2AA"},
    {"name": "Riverside Flat", "address": "41 Riverside Drive, London, SE1 7PB"},
]

_ROOM_SEEDS: dict[str, list[str]] = {
    "Maple Court":    ["Living Room", "Kitchen", "Master Bedroom", "Second Bedroom", "Bathroom"],
    "Brunswick House":["Hallway", "Living Room", "Kitchen", "Bedroom", "Bathroom"],
    "Cedar Lodge":    ["Boiler Room", "Kitchen", "Entry", "Living Room"],
    "The Annexe":     ["Bedroom", "Kitchen", "Bathroom", "Entry"],
    "Oak House":      ["Living Room", "Kitchen", "Bedroom 1", "Bedroom 2"],
    "Riverside Flat": ["Living Room", "Kitchen", "Bedroom", "Bathroom"],
}

# _vid is the stable vendor identifier used as a lookup key for alerts / history
_DEVICE_SEEDS: list[dict] = [
    # ── Maple Court ──
    {"_prop": "Maple Court", "_room": "Living Room",    "_vid": "demo-dev-mc-001",
     "name": "Smart Plug (TV)",        "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True},  "power": 87.0},
    {"_prop": "Maple Court", "_room": "Living Room",    "_vid": "demo-dev-mc-002",
     "name": "Motion Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": True}},
    {"_prop": "Maple Court", "_room": "Kitchen",        "_vid": "demo-dev-mc-003",
     "name": "Fridge Monitor",         "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 4.2},
    {"_prop": "Maple Court", "_room": "Kitchen",        "_vid": "demo-dev-mc-004",
     "name": "Smart Plug (Kettle)",    "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": False}, "power": 0.0},
    {"_prop": "Maple Court", "_room": "Kitchen",        "_vid": "demo-dev-mc-005",
     "name": "Leak Sensor",            "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "leak_detected": False},
    {"_prop": "Maple Court", "_room": "Master Bedroom", "_vid": "demo-dev-mc-006",
     "name": "Temperature Sensor",     "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 19.8, "humidity": 52.0},
    {"_prop": "Maple Court", "_room": "Master Bedroom", "_vid": "demo-dev-mc-007",
     "name": "Smart Plug (Heater)",    "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": False}, "power": 0.0},

    # ── Brunswick House ──
    {"_prop": "Brunswick House", "_room": "Hallway",     "_vid": "demo-dev-bh-001",
     "name": "Smart Lock",             "vendor": "demo", "model": "Demo Lock",   "type": "lock",
     "online": True, "state": {"locked": True}},
    {"_prop": "Brunswick House", "_room": "Hallway",     "_vid": "demo-dev-bh-002",
     "name": "Motion Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": False}},
    {"_prop": "Brunswick House", "_room": "Living Room", "_vid": "demo-dev-bh-003",
     "name": "Energy Meter",           "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 340.0},
    {"_prop": "Brunswick House", "_room": "Living Room", "_vid": "demo-dev-bh-004",
     "name": "Temperature Sensor",     "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 22.1, "humidity": 48.0},
    {"_prop": "Brunswick House", "_room": "Kitchen",     "_vid": "demo-dev-bh-005",
     "name": "Fridge Monitor",         "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 3.8},
    {"_prop": "Brunswick House", "_room": "Kitchen",     "_vid": "demo-dev-bh-006",
     "name": "Leak Sensor",            "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "leak_detected": False},
    {"_prop": "Brunswick House", "_room": "Bathroom",    "_vid": "demo-dev-bh-007",
     "name": "Humidity Sensor",        "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "humidity": 78.0, "temperature": 21.0},

    # ── Cedar Lodge ──
    {"_prop": "Cedar Lodge", "_room": "Boiler Room", "_vid": "demo-dev-cl-001",
     "name": "Temperature Sensor",     "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 68.0},
    {"_prop": "Cedar Lodge", "_room": "Boiler Room", "_vid": "demo-dev-cl-002",
     "name": "Energy Meter",           "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 2400.0},
    {"_prop": "Cedar Lodge", "_room": "Kitchen",     "_vid": "demo-dev-cl-003",
     "name": "Fridge Monitor",         "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 5.1},
    {"_prop": "Cedar Lodge", "_room": "Kitchen",     "_vid": "demo-dev-cl-004",
     "name": "Leak Sensor",            "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "leak_detected": False},
    {"_prop": "Cedar Lodge", "_room": "Kitchen",     "_vid": "demo-dev-cl-005",
     "name": "Smart Plug (Dishwasher)","vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 1200.0},
    {"_prop": "Cedar Lodge", "_room": "Entry",       "_vid": "demo-dev-cl-006",
     "name": "Smart Lock",             "vendor": "demo", "model": "Demo Lock",   "type": "lock",
     "online": True, "state": {"locked": False}},
    {"_prop": "Cedar Lodge", "_room": "Entry",       "_vid": "demo-dev-cl-007",
     "name": "Motion Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": True}},

    # ── The Annexe ──
    {"_prop": "The Annexe", "_room": "Bedroom", "_vid": "demo-dev-ta-001",
     "name": "Temperature Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 17.2},
    {"_prop": "The Annexe", "_room": "Bedroom", "_vid": "demo-dev-ta-002",
     "name": "Smart Plug (Electric Blanket)","vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 60.0},
    {"_prop": "The Annexe", "_room": "Kitchen", "_vid": "demo-dev-ta-003",
     "name": "Smart Plug (Fridge)",          "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 45.0},
    {"_prop": "The Annexe", "_room": "Kitchen", "_vid": "demo-dev-ta-004",
     "name": "Leak Sensor",                  "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "leak_detected": True},
    {"_prop": "The Annexe", "_room": "Entry",   "_vid": "demo-dev-ta-005",
     "name": "Smart Lock",                   "vendor": "demo", "model": "Demo Lock",   "type": "lock",
     "online": True, "state": {"locked": True}},
    {"_prop": "The Annexe", "_room": "Entry",   "_vid": "demo-dev-ta-006",
     "name": "Motion Sensor",                "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": False}},

    # ── Oak House ──
    {"_prop": "Oak House", "_room": "Living Room", "_vid": "demo-dev-oh-001",
     "name": "Smart TV Plug",          "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 120.0},
    {"_prop": "Oak House", "_room": "Living Room", "_vid": "demo-dev-oh-002",
     "name": "Motion Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": True}},
    {"_prop": "Oak House", "_room": "Kitchen",     "_vid": "demo-dev-oh-003",
     "name": "Fridge Monitor",         "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 4.5},
    {"_prop": "Oak House", "_room": "Kitchen",     "_vid": "demo-dev-oh-004",
     "name": "Energy Meter",           "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 890.0},
    {"_prop": "Oak House", "_room": "Bedroom 1",   "_vid": "demo-dev-oh-005",
     "name": "Temperature Sensor",     "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 20.3, "humidity": 55.0},
    {"_prop": "Oak House", "_room": "Bedroom 2",   "_vid": "demo-dev-oh-006",
     "name": "Smart Plug (Laptop)",    "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 65.0},
    {"_prop": "Oak House", "_room": "Bedroom 2",   "_vid": "demo-dev-oh-007",
     "name": "Motion Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": False}},

    # ── Riverside Flat ──
    {"_prop": "Riverside Flat", "_room": "Living Room", "_vid": "demo-dev-rf-001",
     "name": "Energy Meter",           "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 1840.0},
    {"_prop": "Riverside Flat", "_room": "Living Room", "_vid": "demo-dev-rf-002",
     "name": "Smart Lock",             "vendor": "demo", "model": "Demo Lock",   "type": "lock",
     "online": True, "state": {"locked": True}},
    {"_prop": "Riverside Flat", "_room": "Living Room", "_vid": "demo-dev-rf-003",
     "name": "Motion Sensor",          "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {"motion": True}},
    {"_prop": "Riverside Flat", "_room": "Kitchen",     "_vid": "demo-dev-rf-004",
     "name": "Fridge Monitor",         "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 3.2},
    {"_prop": "Riverside Flat", "_room": "Kitchen",     "_vid": "demo-dev-rf-005",
     "name": "Leak Sensor",            "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "leak_detected": False},
    {"_prop": "Riverside Flat", "_room": "Bedroom",     "_vid": "demo-dev-rf-006",
     "name": "Temperature Sensor",     "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "temperature": 21.5, "humidity": 50.0},
    {"_prop": "Riverside Flat", "_room": "Bedroom",     "_vid": "demo-dev-rf-007",
     "name": "Smart Plug (AC)",        "vendor": "demo", "model": "Demo Plug",   "type": "plug",
     "online": True, "state": {"on": True}, "power": 950.0},
    {"_prop": "Riverside Flat", "_room": "Bathroom",    "_vid": "demo-dev-rf-008",
     "name": "Humidity Sensor",        "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "humidity": 65.0},
    {"_prop": "Riverside Flat", "_room": "Bathroom",    "_vid": "demo-dev-rf-009",
     "name": "Leak Sensor",            "vendor": "demo", "model": "Demo Sensor", "type": "sensor",
     "online": True, "state": {}, "leak_detected": False},
]

# ── Runtime state (populated by ensure_demo_seeded) ───────────────────────────

# Maps: "prop:NAME" → uuid, "room:PROP/ROOM" → uuid, "dev:VID" → uuid
_demo_id_map: dict[str, str] = {}
_demo_prop_uuids: set[str] = set()
_demo_dev_uuids: set[str] = set()

DEMO_PROPERTIES: list[dict] = []
DEMO_DEVICES: list[dict] = []

_devices_by_id: dict[str, dict] = {}
_devices_by_property: dict[str, list[dict]] = {}
_rooms_by_property: dict[str, list[dict]] = {}

_seeded = False

# Fixed namespace for deterministic stub UUIDs (used when Supabase is not available)
_DEMO_NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


# ── Seeding ───────────────────────────────────────────────────────────────────

async def ensure_demo_seeded(settings: Settings) -> None:
    global _seeded
    if _seeded:
        return
    try:
        if settings.supabase_url and settings.supabase_service_role_key:
            await _seed_supabase(settings)
        else:
            _seed_stubs()
    except Exception as exc:
        logger.error("Demo seed failed: %s — falling back to stubs", exc)
        if not _seeded:
            _seed_stubs()
    _seeded = True
    logger.info("Demo: ready — %d properties, %d devices", len(DEMO_PROPERTIES), len(DEMO_DEVICES))


def _build_dev(seed: dict, dev_id: str, vid: str, prop_id: str, room_id: str | None) -> dict:
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
    """Generate deterministic stub UUIDs for local-only mode (no Supabase)."""
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
        prop_id = _demo_id_map.get(f"prop:{prop_name}")
        room_id = _demo_id_map.get(f"room:{prop_name}/{room_name}")
        if not prop_id:
            continue
        dev_id = str(uuid.uuid5(_DEMO_NS, f"dev:{vid}"))
        _demo_id_map[f"dev:{vid}"] = dev_id
        _demo_dev_uuids.add(dev_id)
        DEMO_DEVICES.append(_build_dev(dev_seed, dev_id, vid, prop_id, room_id))

    _finalise_devices()


async def _seed_supabase(settings: Settings) -> None:
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }
    base = f"{settings.supabase_url}/rest/v1"

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Resolve org_id
        r = await client.get(f"{base}/organisations", headers=headers,
                             params={"select": "id", "limit": "1"})
        if r.status_code != 200 or not r.json():
            raise RuntimeError("No organisation found in Supabase")
        org_id = r.json()[0]["id"]

        # Fetch all existing properties once
        r = await client.get(f"{base}/properties", headers=headers,
                             params={"select": "id,name"})
        existing_props = {row["name"]: row["id"] for row in r.json()} if r.status_code == 200 else {}

        for prop_seed in _PROP_SEEDS:
            name = prop_seed["name"]

            if name in existing_props:
                prop_id = existing_props[name]
            else:
                r = await client.post(
                    f"{base}/properties",
                    headers={**headers, "Prefer": "return=representation"},
                    json={"organisation_id": org_id, "name": name, "address": prop_seed["address"]},
                )
                if r.status_code not in (200, 201):
                    logger.error("Demo seed: failed to create property '%s': %s", name, r.text[:200])
                    continue
                rows = r.json()
                prop_id = (rows[0] if isinstance(rows, list) else rows)["id"]
                logger.info("Demo: created property '%s' (%s)", name, prop_id)

            _demo_id_map[f"prop:{name}"] = prop_id
            _demo_prop_uuids.add(prop_id)
            DEMO_PROPERTIES.append({"id": prop_id, "name": name, "address": prop_seed["address"]})

            # Fetch existing rooms for this property
            r = await client.get(f"{base}/rooms", headers=headers,
                                 params={"property_id": f"eq.{prop_id}", "select": "id,name"})
            existing_rooms = {row["name"]: row["id"] for row in r.json()} if r.status_code == 200 else {}

            for room_name in _ROOM_SEEDS.get(name, []):
                if room_name in existing_rooms:
                    room_id = existing_rooms[room_name]
                else:
                    r2 = await client.post(
                        f"{base}/rooms",
                        headers={**headers, "Prefer": "return=representation"},
                        json={"property_id": prop_id, "name": room_name},
                    )
                    if r2.status_code not in (200, 201):
                        logger.error("Demo seed: failed to create room '%s'/'%s': %s",
                                     name, room_name, r2.text[:200])
                        continue
                    rows = r2.json()
                    room_id = (rows[0] if isinstance(rows, list) else rows)["id"]

                _demo_id_map[f"room:{name}/{room_name}"] = room_id
                _rooms_by_property.setdefault(prop_id, []).append(
                    {"id": room_id, "property_id": prop_id, "name": room_name}
                )

    # Build in-memory device list with real property/room UUIDs
    for dev_seed in _DEVICE_SEEDS:
        prop_name = dev_seed["_prop"]
        room_name = dev_seed["_room"]
        vid = dev_seed["_vid"]
        prop_id = _demo_id_map.get(f"prop:{prop_name}")
        room_id = _demo_id_map.get(f"room:{prop_name}/{room_name}")
        if not prop_id:
            continue
        dev_id = str(uuid.uuid4())
        _demo_id_map[f"dev:{vid}"] = dev_id
        _demo_dev_uuids.add(dev_id)
        DEMO_DEVICES.append(_build_dev(dev_seed, dev_id, vid, prop_id, room_id))

    _finalise_devices()


# ── Lookup helpers ─────────────────────────────────────────────────────────────

def is_demo_property(property_id: str) -> bool:
    return property_id in _demo_prop_uuids


def is_demo_device(device_id: str) -> bool:
    return device_id in _demo_dev_uuids


def get_demo_device(device_id: str) -> dict | None:
    return _devices_by_id.get(device_id)


def get_demo_devices_for_property(property_id: str) -> list[dict]:
    return _devices_by_property.get(property_id, [])


def get_demo_rooms(property_id: str) -> list[dict]:
    return _rooms_by_property.get(property_id, [])


def demo_device_as_saved(d: dict) -> dict:
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


def demo_device_as_alphacon(d: dict) -> dict:
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


def demo_device_state(d: dict) -> dict:
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
