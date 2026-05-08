"""
Demo data for Alphacon AI.

All demo content is isolated here. Delete this folder and set
DEMO_MODE=false to remove all demo content with zero other changes.
"""
from __future__ import annotations

from datetime import datetime

# ── Properties ────────────────────────────────────────────────────────────────

DEMO_PROPERTIES: list[dict] = [
    {"id": "demo-prop-001", "name": "Maple Court", "address": "14 Maple Street, Leeds, LS1 1AA"},
    {"id": "demo-prop-002", "name": "Brunswick House", "address": "Flat 3, Brunswick House, Manchester, M2 4QQ"},
    {"id": "demo-prop-003", "name": "Cedar Lodge", "address": "8 Cedar Road, Birmingham, B15 2TT"},
    {"id": "demo-prop-004", "name": "The Annexe", "address": "22 Riverside Walk, Bristol, BS1 5SB"},
    {"id": "demo-prop-005", "name": "Oak House", "address": "5 Oak Lane, Leeds, LS6 2AA"},
    {"id": "demo-prop-006", "name": "Riverside Flat", "address": "41 Riverside Drive, London, SE1 7PB"},
]

# ── Rooms ─────────────────────────────────────────────────────────────────────

DEMO_ROOMS: dict[str, list[dict]] = {
    "demo-prop-001": [
        {"id": "demo-room-001-01", "property_id": "demo-prop-001", "name": "Living Room"},
        {"id": "demo-room-001-02", "property_id": "demo-prop-001", "name": "Kitchen"},
        {"id": "demo-room-001-03", "property_id": "demo-prop-001", "name": "Master Bedroom"},
        {"id": "demo-room-001-04", "property_id": "demo-prop-001", "name": "Second Bedroom"},
        {"id": "demo-room-001-05", "property_id": "demo-prop-001", "name": "Bathroom"},
    ],
    "demo-prop-002": [
        {"id": "demo-room-002-01", "property_id": "demo-prop-002", "name": "Hallway"},
        {"id": "demo-room-002-02", "property_id": "demo-prop-002", "name": "Living Room"},
        {"id": "demo-room-002-03", "property_id": "demo-prop-002", "name": "Kitchen"},
        {"id": "demo-room-002-04", "property_id": "demo-prop-002", "name": "Bedroom"},
        {"id": "demo-room-002-05", "property_id": "demo-prop-002", "name": "Bathroom"},
    ],
    "demo-prop-003": [
        {"id": "demo-room-003-01", "property_id": "demo-prop-003", "name": "Boiler Room"},
        {"id": "demo-room-003-02", "property_id": "demo-prop-003", "name": "Kitchen"},
        {"id": "demo-room-003-03", "property_id": "demo-prop-003", "name": "Entry"},
        {"id": "demo-room-003-04", "property_id": "demo-prop-003", "name": "Living Room"},
    ],
    "demo-prop-004": [
        {"id": "demo-room-004-01", "property_id": "demo-prop-004", "name": "Bedroom"},
        {"id": "demo-room-004-02", "property_id": "demo-prop-004", "name": "Kitchen"},
        {"id": "demo-room-004-03", "property_id": "demo-prop-004", "name": "Bathroom"},
        {"id": "demo-room-004-04", "property_id": "demo-prop-004", "name": "Entry"},
    ],
    "demo-prop-005": [
        {"id": "demo-room-005-01", "property_id": "demo-prop-005", "name": "Living Room"},
        {"id": "demo-room-005-02", "property_id": "demo-prop-005", "name": "Kitchen"},
        {"id": "demo-room-005-03", "property_id": "demo-prop-005", "name": "Bedroom 1"},
        {"id": "demo-room-005-04", "property_id": "demo-prop-005", "name": "Bedroom 2"},
    ],
    "demo-prop-006": [
        {"id": "demo-room-006-01", "property_id": "demo-prop-006", "name": "Living Room"},
        {"id": "demo-room-006-02", "property_id": "demo-prop-006", "name": "Kitchen"},
        {"id": "demo-room-006-03", "property_id": "demo-prop-006", "name": "Bedroom"},
        {"id": "demo-room-006-04", "property_id": "demo-prop-006", "name": "Bathroom"},
    ],
}

# ── Devices ───────────────────────────────────────────────────────────────────
# ip_address is always None — never expose IPs to frontend

DEMO_DEVICES: list[dict] = [
    # ── Maple Court ──
    {"id": "demo-dev-mc-001", "property_id": "demo-prop-001", "room_id": "demo-room-001-01",
     "name": "Smart Plug (TV)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 87.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-mc-002", "property_id": "demo-prop-001", "room_id": "demo-room-001-01",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": True}, "ip_address": None, "mac": None},
    {"id": "demo-dev-mc-003", "property_id": "demo-prop-001", "room_id": "demo-room-001-02",
     "name": "Fridge Monitor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 4.2, "ip_address": None, "mac": None},
    {"id": "demo-dev-mc-004", "property_id": "demo-prop-001", "room_id": "demo-room-001-02",
     "name": "Smart Plug (Kettle)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": False}, "power": 0.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-mc-005", "property_id": "demo-prop-001", "room_id": "demo-room-001-02",
     "name": "Leak Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "leak_detected": False, "ip_address": None, "mac": None},
    {"id": "demo-dev-mc-006", "property_id": "demo-prop-001", "room_id": "demo-room-001-03",
     "name": "Temperature Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 19.8, "humidity": 52.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-mc-007", "property_id": "demo-prop-001", "room_id": "demo-room-001-03",
     "name": "Smart Plug (Heater)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": False}, "power": 0.0, "ip_address": None, "mac": None},

    # ── Brunswick House ──
    {"id": "demo-dev-bh-001", "property_id": "demo-prop-002", "room_id": "demo-room-002-01",
     "name": "Smart Lock", "vendor": "demo", "type": "lock", "model": "Demo Lock",
     "online": True, "state": {"locked": True}, "ip_address": None, "mac": None},
    {"id": "demo-dev-bh-002", "property_id": "demo-prop-002", "room_id": "demo-room-002-01",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": False}, "ip_address": None, "mac": None},
    {"id": "demo-dev-bh-003", "property_id": "demo-prop-002", "room_id": "demo-room-002-02",
     "name": "Energy Meter", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 340.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-bh-004", "property_id": "demo-prop-002", "room_id": "demo-room-002-02",
     "name": "Temperature Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 22.1, "humidity": 48.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-bh-005", "property_id": "demo-prop-002", "room_id": "demo-room-002-03",
     "name": "Fridge Monitor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 3.8, "ip_address": None, "mac": None},
    {"id": "demo-dev-bh-006", "property_id": "demo-prop-002", "room_id": "demo-room-002-03",
     "name": "Leak Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "leak_detected": False, "ip_address": None, "mac": None},
    {"id": "demo-dev-bh-007", "property_id": "demo-prop-002", "room_id": "demo-room-002-05",
     "name": "Humidity Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "humidity": 78.0, "temperature": 21.0, "ip_address": None, "mac": None},

    # ── Cedar Lodge ──
    {"id": "demo-dev-cl-001", "property_id": "demo-prop-003", "room_id": "demo-room-003-01",
     "name": "Temperature Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 68.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-cl-002", "property_id": "demo-prop-003", "room_id": "demo-room-003-01",
     "name": "Energy Meter", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 2400.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-cl-003", "property_id": "demo-prop-003", "room_id": "demo-room-003-02",
     "name": "Fridge Monitor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 5.1, "ip_address": None, "mac": None},
    {"id": "demo-dev-cl-004", "property_id": "demo-prop-003", "room_id": "demo-room-003-02",
     "name": "Leak Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "leak_detected": False, "ip_address": None, "mac": None},
    {"id": "demo-dev-cl-005", "property_id": "demo-prop-003", "room_id": "demo-room-003-02",
     "name": "Smart Plug (Dishwasher)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 1200.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-cl-006", "property_id": "demo-prop-003", "room_id": "demo-room-003-03",
     "name": "Smart Lock", "vendor": "demo", "type": "lock", "model": "Demo Lock",
     "online": True, "state": {"locked": False}, "ip_address": None, "mac": None},
    {"id": "demo-dev-cl-007", "property_id": "demo-prop-003", "room_id": "demo-room-003-03",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": True}, "ip_address": None, "mac": None},

    # ── The Annexe ──
    {"id": "demo-dev-ta-001", "property_id": "demo-prop-004", "room_id": "demo-room-004-01",
     "name": "Temperature Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 17.2, "ip_address": None, "mac": None},
    {"id": "demo-dev-ta-002", "property_id": "demo-prop-004", "room_id": "demo-room-004-01",
     "name": "Smart Plug (Electric Blanket)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 60.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-ta-003", "property_id": "demo-prop-004", "room_id": "demo-room-004-02",
     "name": "Smart Plug (Fridge)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 45.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-ta-004", "property_id": "demo-prop-004", "room_id": "demo-room-004-02",
     "name": "Leak Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "leak_detected": True, "ip_address": None, "mac": None},
    {"id": "demo-dev-ta-005", "property_id": "demo-prop-004", "room_id": "demo-room-004-04",
     "name": "Smart Lock", "vendor": "demo", "type": "lock", "model": "Demo Lock",
     "online": True, "state": {"locked": True}, "ip_address": None, "mac": None},
    {"id": "demo-dev-ta-006", "property_id": "demo-prop-004", "room_id": "demo-room-004-04",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": False}, "ip_address": None, "mac": None},

    # ── Oak House ──
    {"id": "demo-dev-oh-001", "property_id": "demo-prop-005", "room_id": "demo-room-005-01",
     "name": "Smart TV Plug", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 120.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-oh-002", "property_id": "demo-prop-005", "room_id": "demo-room-005-01",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": True}, "ip_address": None, "mac": None},
    {"id": "demo-dev-oh-003", "property_id": "demo-prop-005", "room_id": "demo-room-005-02",
     "name": "Fridge Monitor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 4.5, "ip_address": None, "mac": None},
    {"id": "demo-dev-oh-004", "property_id": "demo-prop-005", "room_id": "demo-room-005-02",
     "name": "Energy Meter", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 890.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-oh-005", "property_id": "demo-prop-005", "room_id": "demo-room-005-03",
     "name": "Temperature Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 20.3, "humidity": 55.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-oh-006", "property_id": "demo-prop-005", "room_id": "demo-room-005-04",
     "name": "Smart Plug (Laptop)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 65.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-oh-007", "property_id": "demo-prop-005", "room_id": "demo-room-005-04",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": False}, "ip_address": None, "mac": None},

    # ── Riverside Flat ──
    {"id": "demo-dev-rf-001", "property_id": "demo-prop-006", "room_id": "demo-room-006-01",
     "name": "Energy Meter", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 1840.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-002", "property_id": "demo-prop-006", "room_id": "demo-room-006-01",
     "name": "Smart Lock", "vendor": "demo", "type": "lock", "model": "Demo Lock",
     "online": True, "state": {"locked": True}, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-003", "property_id": "demo-prop-006", "room_id": "demo-room-006-01",
     "name": "Motion Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {"motion": True}, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-004", "property_id": "demo-prop-006", "room_id": "demo-room-006-02",
     "name": "Fridge Monitor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 3.2, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-005", "property_id": "demo-prop-006", "room_id": "demo-room-006-02",
     "name": "Leak Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "leak_detected": False, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-006", "property_id": "demo-prop-006", "room_id": "demo-room-006-03",
     "name": "Temperature Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "temperature": 21.5, "humidity": 50.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-007", "property_id": "demo-prop-006", "room_id": "demo-room-006-03",
     "name": "Smart Plug (AC)", "vendor": "demo", "type": "plug", "model": "Demo Plug",
     "online": True, "state": {"on": True}, "power": 950.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-008", "property_id": "demo-prop-006", "room_id": "demo-room-006-04",
     "name": "Humidity Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "humidity": 65.0, "ip_address": None, "mac": None},
    {"id": "demo-dev-rf-009", "property_id": "demo-prop-006", "room_id": "demo-room-006-04",
     "name": "Leak Sensor", "vendor": "demo", "type": "sensor", "model": "Demo Sensor",
     "online": True, "state": {}, "leak_detected": False, "ip_address": None, "mac": None},
]

# ── Lookup helpers ────────────────────────────────────────────────────────────

_devices_by_id: dict[str, dict] = {d["id"]: d for d in DEMO_DEVICES}
_devices_by_property: dict[str, list[dict]] = {}
for _d in DEMO_DEVICES:
    _devices_by_property.setdefault(_d["property_id"], []).append(_d)


def get_demo_device(device_id: str) -> dict | None:
    return _devices_by_id.get(device_id)


def get_demo_devices_for_property(property_id: str) -> list[dict]:
    return _devices_by_property.get(property_id, [])


def get_demo_rooms(property_id: str) -> list[dict]:
    return DEMO_ROOMS.get(property_id, [])


def demo_device_as_saved(d: dict) -> dict:
    """Convert a demo device dict to the SavedDevice wire format."""
    return {
        "id": d["id"],
        "property_id": d["property_id"],
        "room_id": d.get("room_id"),
        "vendor": d["vendor"],
        "vendor_id": d["id"],
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
        "vendor_id": d["id"],
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
