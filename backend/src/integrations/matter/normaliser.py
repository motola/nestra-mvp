"""Matter → SpireDevice normaliser stub."""

from __future__ import annotations

from typing import Any

from spire import SpireDevice


def normalise_matter_device(raw: dict[str, Any]) -> SpireDevice:
    """Convert a zeroconf-discovered Matter service record to SpireDevice."""
    return SpireDevice.from_vendor(
        vendor="matter",
        vendor_id=raw.get("name", "unknown"),
        name=raw.get("name", "Matter Device"),
        device_type="light",
        online=True,
    )
