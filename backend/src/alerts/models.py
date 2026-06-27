"""Alert model — an anomaly or issue detected by the alert service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

AlertSeverity = Literal["info", "warning", "critical"]


class Alert(BaseModel):
    """An unresolved issue flagged by the alert service for a property manager."""

    id: str
    device_id: str
    device_name: str
    property_id: str
    property_name: str
    type: str
    severity: AlertSeverity
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dismissed: bool = False
