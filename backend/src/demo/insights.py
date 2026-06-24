"""Pre-written insights for demo devices. Never calls Claude API."""

from __future__ import annotations

from typing import Any

from demo.data import get_demo_device

_INSIGHTS: dict[str, dict[str, Any]] = {
    # Maple Court
    "demo-dev-mc-001": {
        "severity": "info",
        "message": "Drawing 87W. Operating within normal range for this time of day.",
    },
    "demo-dev-mc-002": {
        "severity": "info",
        "message": "Motion detected 4 hours ago. Property appears to have been recently occupied.",
    },
    "demo-dev-mc-003": {
        "severity": "info",
        "message": "Fridge holding steady at 4.2°C. No issues detected.",
    },
    "demo-dev-mc-004": {"severity": "info", "message": "Kettle is off and drawing 0W. No issues."},
    "demo-dev-mc-005": {
        "severity": "info",
        "message": "No moisture detected. Sensor last checked less than 1 minute ago.",
    },
    "demo-dev-mc-006": {
        "severity": "info",
        "message": "Temperature stable at 19.8°C with 52% humidity. Within expected range.",
    },
    "demo-dev-mc-007": {"severity": "info", "message": "Heater is off. Not drawing power."},
    # Brunswick House
    "demo-dev-bh-001": {
        "severity": "info",
        "message": "Lock is secured. Last accessed 2 hours ago.",
    },
    "demo-dev-bh-002": {
        "severity": "info",
        "message": "No motion in hallway for 2 hours. Property may be unoccupied.",
    },
    "demo-dev-bh-003": {
        "severity": "warning",
        "message": (
            "Smart plug drawing 340W — 23% above its 7-day average, elevated for 4 hours. "
            "Consider checking the connected appliance for a fault."
        ),
    },
    "demo-dev-bh-004": {
        "severity": "info",
        "message": "Temperature stable at 22.1°C with 48% humidity. Comfortable living conditions.",
    },
    "demo-dev-bh-005": {
        "severity": "info",
        "message": "Fridge holding steady at 3.8°C. Well within safe range.",
    },
    "demo-dev-bh-006": {
        "severity": "info",
        "message": "No moisture detected in kitchen. No action required.",
    },
    "demo-dev-bh-007": {
        "severity": "warning",
        "message": (
            "Bathroom humidity at 78%. This is above the recommended 60% threshold. "
            "Consider improving ventilation to prevent mould."
        ),
    },
    # Cedar Lodge
    "demo-dev-cl-001": {
        "severity": "info",
        "message": "Boiler flow temperature at 68°C. Normal operating range for central heating.",
    },
    "demo-dev-cl-002": {
        "severity": "info",
        "message": "Boiler drawing 2400W. Normal for active heating cycle.",
    },
    "demo-dev-cl-003": {
        "severity": "info",
        "message": "Fridge at 5.1°C. Slightly warm but within acceptable range.",
    },
    "demo-dev-cl-004": {
        "severity": "info",
        "message": "No moisture detected in kitchen. All clear.",
    },
    "demo-dev-cl-005": {
        "severity": "info",
        "message": "Dishwasher drawing 1200W — currently mid-cycle. Expected power level.",
    },
    "demo-dev-cl-006": {
        "severity": "warning",
        "message": (
            "Front door lock has been in the unlocked position for 3 hours. "
            "Verify this is intentional and consider alerting the tenant."
        ),
    },
    "demo-dev-cl-007": {
        "severity": "info",
        "message": "Motion detected in entry 12 minutes ago. Someone recently entered or left.",
    },
    # The Annexe
    "demo-dev-ta-001": {
        "severity": "warning",
        "message": (
            "Bedroom temperature has dropped to 17.2°C, below the 18°C threshold. "
            "Consider checking the heating system or alerting the tenant."
        ),
    },
    "demo-dev-ta-002": {
        "severity": "info",
        "message": "Electric blanket drawing 60W. In use — expected for this temperature.",
    },
    "demo-dev-ta-003": {
        "severity": "info",
        "message": "Fridge drawing 45W. Normal standby draw.",
    },
    "demo-dev-ta-004": {
        "severity": "critical",
        "message": (
            "WATER LEAK DETECTED in kitchen. Immediate action required. "
            "Contact the tenant and arrange an urgent inspection."
        ),
    },
    "demo-dev-ta-005": {"severity": "info", "message": "Front door locked. No issues."},
    "demo-dev-ta-006": {
        "severity": "info",
        "message": "No motion detected in entry. Property appears unoccupied.",
    },
    # Oak House
    "demo-dev-oh-001": {
        "severity": "info",
        "message": "TV drawing 120W. Normal operating draw.",
    },
    "demo-dev-oh-002": {
        "severity": "info",
        "message": "Motion detected 8 minutes ago in living room. Property is occupied.",
    },
    "demo-dev-oh-003": {
        "severity": "info",
        "message": "Fridge at 4.5°C. Normal operating temperature.",
    },
    "demo-dev-oh-004": {
        "severity": "info",
        "message": "Kitchen smart plug drawing 890W. Likely cooking activity underway.",
    },
    "demo-dev-oh-005": {
        "severity": "info",
        "message": "Bedroom 1 at 20.3°C with 55% humidity. Comfortable conditions.",
    },
    "demo-dev-oh-006": {
        "severity": "info",
        "message": "Laptop charger drawing 65W. Normal draw for device charging.",
    },
    "demo-dev-oh-007": {
        "severity": "info",
        "message": "No motion detected in Bedroom 2 for 6 hours. Tenant may be away.",
    },
    # Riverside Flat
    "demo-dev-rf-001": {
        "severity": "warning",
        "message": (
            "Smart plug drawing 1840W — higher than usual. "
            "Could indicate multiple appliances running simultaneously, or one left on."
        ),
    },
    "demo-dev-rf-002": {"severity": "info", "message": "Front door locked. No issues."},
    "demo-dev-rf-003": {
        "severity": "info",
        "message": "Motion detected 2 minutes ago. Property is currently occupied.",
    },
    "demo-dev-rf-004": {
        "severity": "info",
        "message": "Fridge at 3.2°C. Excellent temperature for food safety.",
    },
    "demo-dev-rf-005": {
        "severity": "info",
        "message": "No moisture detected in kitchen. All clear.",
    },
    "demo-dev-rf-006": {
        "severity": "info",
        "message": "Bedroom at 21.5°C with 50% humidity. Ideal sleeping conditions.",
    },
    "demo-dev-rf-007": {
        "severity": "info",
        "message": "AC drawing 950W. Running actively — normal for current conditions.",
    },
    "demo-dev-rf-008": {
        "severity": "info",
        "message": "Bathroom humidity at 65%. Within acceptable range.",
    },
    "demo-dev-rf-009": {
        "severity": "info",
        "message": "No moisture detected in bathroom. All clear.",
    },
}


def get_demo_insight(device_id: str) -> dict[str, Any] | None:
    d = get_demo_device(device_id)
    if not d:
        return None
    vid = d.get("vendor_id", device_id)
    base = _INSIGHTS.get(vid)
    if not base:
        return None
    return {
        "device_id": device_id,
        "message": base["message"],
        "severity": base["severity"],
        "generated_at": "2024-01-01T00:00:00Z",
        "cached": False,
        "model_used": "demo",
    }
