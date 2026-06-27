"""The SPIRE vendor-adapter contract.

Any integration that wants to speak SPIRE implements this interface: it returns
``SpireDevice`` resources and accepts canonical commands, so nothing downstream
ever sees a vendor-specific type. This is the seam third parties extend to add a
new vendor to a SPIRE-based platform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from spire.device import SpireDevice


class VendorAdapter(ABC):
    """Abstract base every vendor integration implements."""

    @abstractmethod
    async def list_devices(self) -> list[SpireDevice]:
        """Return all devices for this vendor account as SPIRE resources."""
        ...

    @abstractmethod
    async def get_device_state(self, device_id: str) -> SpireDevice:
        """Return the current state of a single device by its SPIRE id."""
        ...

    @abstractmethod
    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """Send a canonical command (e.g. ``{"action": "turn_on"}``); return True on success."""
        ...
