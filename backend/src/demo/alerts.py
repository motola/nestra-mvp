"""Pre-defined demo alerts."""

from __future__ import annotations

from typing import Any

# Legacy vendor IDs used as keys in _demo_id_map
_PROP_VID_MAP = {
    "demo-prop-001": "Maple Court",
    "demo-prop-002": "Brunswick House",
    "demo-prop-003": "Cedar Lodge",
    "demo-prop-004": "The Annexe",
    "demo-prop-005": "Oak House",
    "demo-prop-006": "Riverside Flat",
}

DEMO_ALERTS: list[dict[str, Any]] = [
    {
        "id": "demo-alert-001",
        "device_id": "demo-dev-bh-003",
        "device_name": "Energy Meter",
        "property_id": "demo-prop-002",
        "property_name": "Brunswick House",
        "type": "power_spike",
        "severity": "warning",
        "message": "Energy meter drawing 23% above 7-day average for 4 hours.",
        "dismissed": False,
        "created_at": "2024-01-15T10:00:00Z",
    },
    {
        "id": "demo-alert-002",
        "device_id": "demo-dev-cl-006",
        "device_name": "Smart Lock",
        "property_id": "demo-prop-003",
        "property_name": "Cedar Lodge",
        "type": "lock_open",
        "severity": "warning",
        "message": "Front door lock left unlocked for 3 hours.",
        "dismissed": False,
        "created_at": "2024-01-15T09:30:00Z",
    },
    {
        "id": "demo-alert-003",
        "device_id": "demo-dev-ta-004",
        "device_name": "Leak Sensor",
        "property_id": "demo-prop-004",
        "property_name": "The Annexe",
        "type": "leak",
        "severity": "critical",
        "message": "Water leak sensor triggered in kitchen. Immediate inspection required.",
        "dismissed": False,
        "created_at": "2024-01-15T11:15:00Z",
    },
    {
        "id": "demo-alert-004",
        "device_id": "demo-dev-ta-001",
        "device_name": "Temperature Sensor",
        "property_id": "demo-prop-004",
        "property_name": "The Annexe",
        "type": "temperature",
        "severity": "warning",
        "message": "Bedroom temperature dropped below 18°C threshold.",
        "dismissed": False,
        "created_at": "2024-01-15T08:00:00Z",
    },
    {
        "id": "demo-alert-005",
        "device_id": "demo-dev-bh-007",
        "device_name": "Humidity Sensor",
        "property_id": "demo-prop-002",
        "property_name": "Brunswick House",
        "type": "humidity",
        "severity": "info",
        "message": "Bathroom humidity at 78%. Consider improving ventilation.",
        "dismissed": False,
        "created_at": "2024-01-15T07:45:00Z",
    },
    {
        "id": "demo-alert-006",
        "device_id": "demo-dev-oh-007",
        "device_name": "Motion Sensor",
        "property_id": "demo-prop-005",
        "property_name": "Oak House",
        "type": "no_motion",
        "severity": "info",
        "message": "No motion detected in Bedroom 2 for 6 hours.",
        "dismissed": False,
        "created_at": "2024-01-15T06:00:00Z",
    },
]


def get_demo_alerts() -> list[dict[str, Any]]:
    """Return DEMO_ALERTS with property_id and device_id resolved to real UUIDs."""
    from demo.data import _demo_id_map

    result = []
    for a in DEMO_ALERTS:
        prop_name = _PROP_VID_MAP.get(a["property_id"])
        prop_id = (
            _demo_id_map.get(f"prop:{prop_name}", a["property_id"])
            if prop_name
            else a["property_id"]
        )
        dev_id = _demo_id_map.get(f"dev:{a['device_id']}", a["device_id"])
        result.append({**a, "property_id": prop_id, "device_id": dev_id})
    return result
