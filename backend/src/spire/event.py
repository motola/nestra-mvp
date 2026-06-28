"""SPIRE event resource — the time-series observation a device reports.

Where ``SpireDevice`` holds a device's *current* state, a ``SpireEvent`` records
*what it reported and when*: a state change, a transition online or offline, or a
sensor reading such as a leak, motion, or smoke detection. Each event optionally
references the ``Trait`` that produced it, so consumers can interpret the value
against the trait catalog. This is the append-only, time-stamped half of the
model — the history a property's monitoring and automation build on.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from spire.device import AuditMeta
from spire.traits import Trait


class EventType(StrEnum):
    """The kind of observation an event records (a state change or a sensor signal)."""

    STATE_CHANGE = "state_change"
    CAME_ONLINE = "came_online"
    WENT_OFFLINE = "went_offline"
    LEAK_DETECTED = "leak_detected"
    MOTION_DETECTED = "motion_detected"
    CONTACT_OPENED = "contact_opened"
    SMOKE_DETECTED = "smoke_detected"
    CO_DETECTED = "co_detected"
    LOW_BATTERY = "low_battery"


class SpireEvent(BaseModel):
    """A single time-stamped observation a device reported — SPIRE's time-series resource."""

    resource_type: Literal["Event"] = "Event"
    id: str
    device_id: str
    property_id: str | None = None
    type: EventType
    trait: Trait | None = None
    value: Any = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    meta: AuditMeta = Field(default_factory=AuditMeta)
