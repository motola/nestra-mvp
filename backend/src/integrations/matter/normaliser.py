"""Matter → AlphaconDevice normaliser stub."""
from __future__ import annotations

from models.device import AlphaconDevice


def normalise_matter_device(raw: dict) -> AlphaconDevice:
    """Convert a zeroconf-discovered Matter service record to AlphaconDevice."""
    return AlphaconDevice(
        vendor_id=raw.get("name", "unknown"),
        vendor="matter",
        name=raw.get("name", "Matter Device"),
        type="light",
        online=True,
        controllable=False,
    )
