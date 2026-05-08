"""Demo portfolio intelligence items."""
from __future__ import annotations

from datetime import datetime, timedelta

_PROP_VID_MAP = {
    "demo-prop-001": "Maple Court",
    "demo-prop-002": "Brunswick House",
    "demo-prop-003": "Cedar Lodge",
    "demo-prop-004": "The Annexe",
    "demo-prop-005": "Oak House",
    "demo-prop-006": "Riverside Flat",
}


def _ts(hours_ago: float = 0) -> str:
    return (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat() + "Z"


DEMO_INTELLIGENCE: list[dict] = [
    {
        "id": "intel-001",
        "property_id": "demo-prop-003",
        "property_name": "Cedar Lodge",
        "type": "energy_anomaly",
        "severity": "critical",
        "title": "Boiler Room energy spike detected",
        "detail": (
            "The energy meter in the Boiler Room has been recording 2.4 kW continuously for 18+ hours — "
            "well above the 0.8 kW baseline. This is consistent with a heating system fault or a "
            "malfunctioning appliance left running. Recommend immediate inspection."
        ),
        "generated_at": _ts(2),
        "metric": 2400.0,
        "unit": "W",
    },
    {
        "id": "intel-002",
        "property_id": "demo-prop-004",
        "property_name": "The Annexe",
        "type": "environmental",
        "severity": "critical",
        "title": "Active leak detected in Kitchen",
        "detail": (
            "The leak sensor in the Kitchen at The Annexe has detected moisture. "
            "Treat as an active leak until confirmed otherwise. "
            "Risk of water damage to flooring and cabinetry if not addressed promptly."
        ),
        "generated_at": _ts(1),
        "metric": None,
        "unit": None,
    },
    {
        "id": "intel-003",
        "property_id": "demo-prop-002",
        "property_name": "Brunswick House",
        "type": "environmental",
        "severity": "warning",
        "title": "High bathroom humidity — mould risk",
        "detail": (
            "Bathroom humidity has remained above 75% for 3 consecutive days, "
            "suggesting poor ventilation. Prolonged high humidity can lead to mould growth "
            "and structural damp. Consider inspecting the extractor fan or adding ventilation."
        ),
        "generated_at": _ts(12),
        "metric": 78.0,
        "unit": "%",
    },
    {
        "id": "intel-004",
        "property_id": "demo-prop-006",
        "property_name": "Riverside Flat",
        "type": "energy_anomaly",
        "severity": "warning",
        "title": "Living room energy 2.3× above portfolio average",
        "detail": (
            "Riverside Flat living room has averaged 1.84 kW over the last 48 hours — 2.3× the "
            "portfolio average for this device type. Could indicate a high-draw appliance left on "
            "or a device fault. Review what is plugged into the energy meter."
        ),
        "generated_at": _ts(20),
        "metric": 1840.0,
        "unit": "W",
    },
    {
        "id": "intel-005",
        "property_id": "demo-prop-004",
        "property_name": "The Annexe",
        "type": "occupancy_pattern",
        "severity": "warning",
        "title": "Entry motion detected at 02:47",
        "detail": (
            "Motion was detected at the entry of The Annexe at 02:47 — outside the typical "
            "occupancy window (08:00–23:00). This could indicate a late return or an "
            "unauthorised access event. Cross-reference with smart lock activity."
        ),
        "generated_at": _ts(7),
        "metric": None,
        "unit": None,
    },
    {
        "id": "intel-006",
        "property_id": "demo-prop-003",
        "property_name": "Cedar Lodge",
        "type": "maintenance_prediction",
        "severity": "warning",
        "title": "Smart lock battery low — Cedar Lodge entry",
        "detail": (
            "Based on lock event frequency, the entry smart lock at Cedar Lodge is estimated to "
            "have 15–20% battery remaining. At current usage (~8 events/day), "
            "replacement should be scheduled within the next 2 weeks to avoid a lockout."
        ),
        "generated_at": _ts(30),
        "metric": 17.0,
        "unit": "% battery",
    },
    {
        "id": "intel-007",
        "property_id": "demo-prop-001",
        "property_name": "Maple Court",
        "type": "occupancy_pattern",
        "severity": "info",
        "title": "Normal occupancy pattern — Maple Court",
        "detail": (
            "Motion sensors show regular daytime occupancy (07:00–22:00) and overnight inactivity. "
            "No anomalous activity detected. Heating and power usage aligns with expected "
            "occupancy patterns for a single-tenancy property."
        ),
        "generated_at": _ts(24),
        "metric": None,
        "unit": None,
    },
    {
        "id": "intel-008",
        "property_id": "demo-prop-005",
        "property_name": "Oak House",
        "type": "energy_anomaly",
        "severity": "info",
        "title": "Oak House energy within normal range",
        "detail": (
            "Total energy draw for Oak House is 1.19 kW — consistent with a 2-bedroom property "
            "in active use. No anomalies detected. The main draw is the kitchen energy meter at 890 W, "
            "consistent with a cooker or washing machine cycle."
        ),
        "generated_at": _ts(48),
        "metric": 1190.0,
        "unit": "W",
    },
]


def get_demo_intelligence() -> list[dict]:
    """Return DEMO_INTELLIGENCE with property_id resolved to real UUIDs."""
    from demo.data import _demo_id_map
    result = []
    for item in DEMO_INTELLIGENCE:
        prop_name = _PROP_VID_MAP.get(item["property_id"])
        prop_id = _demo_id_map.get(f"prop:{prop_name}", item["property_id"]) if prop_name else item["property_id"]
        result.append({**item, "property_id": prop_id})
    return result
