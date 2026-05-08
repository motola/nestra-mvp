"""Generate realistic fake state history for demo devices."""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

from demo.data import get_demo_device


def get_demo_history(device_id: str, limit: int = 50) -> list[dict]:
    """Return fake on/off state change events for a demo device."""
    d = get_demo_device(device_id)
    if not d:
        return []

    events = []
    now = datetime.now(timezone.utc)

    # Generate 3–8 on/off events over the last 24 hours
    rng = random.Random(device_id)
    n_events = rng.randint(3, 8)
    event_times = sorted(
        [now - timedelta(hours=rng.uniform(0.5, 23.5)) for _ in range(n_events)],
        reverse=True,
    )

    current_on = d.get("state", {}).get("on", False)
    for i, t in enumerate(event_times):
        event_type = "turned_on" if (i % 2 == 0) == current_on else "turned_off"
        events.append({
            "id": f"{device_id}-hist-{i}",
            "device_id": device_id,
            "property_id": d["property_id"],
            "event_type": event_type,
            "value": None,
            "recorded_at": t.isoformat(),
        })

    return events[:limit]


def get_demo_power_history(device_id: str) -> list[dict]:
    """Return 24h of power readings at 10-minute intervals for charting."""
    d = get_demo_device(device_id)
    if not d or d.get("type") != "plug":
        return []

    base_power = d.get("power", 0.0)
    if base_power == 0:
        return []

    now = datetime.now(timezone.utc)
    points = []
    rng = random.Random(device_id + "power")

    for i in range(144):  # 24h at 10-min intervals
        t = now - timedelta(minutes=10 * (143 - i))
        # Slight sinusoidal variation ±5% with random noise ±2%
        variation = 1.0 + 0.05 * math.sin(i / 12) + rng.uniform(-0.02, 0.02)
        power = round(base_power * variation, 1)
        points.append({
            "recorded_at": t.isoformat(),
            "value": str(power),
        })

    return points
