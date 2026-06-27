"""Matter → SpireDevice normaliser stub."""

from __future__ import annotations

from typing import Any

from devices.models import SpireDevice


def normalise_matter_device(raw: dict[str, Any]) -> SpireDevice:
    """Convert a zeroconf-discovered Matter service record to SpireDevice."""
    return SpireDevice(
        vendor_id=raw.get("name", "unknown"),
        vendor="matter",
        name=raw.get("name", "Matter Device"),
        type="light",
        online=True,
        controllable=False,
    )
