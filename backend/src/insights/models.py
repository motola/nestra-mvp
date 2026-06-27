"""Insight model — AI-generated plain English analysis of a device's behaviour."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

InsightSeverity = Literal["info", "warning", "critical"]


class Insight(BaseModel):
    """Claude-generated insight for a single device, cached in Upstash Redis."""

    device_id: str
    message: str
    severity: InsightSeverity = "info"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    cached: bool = False
    model_used: str = ""
