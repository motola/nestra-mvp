"""
AI Insight service — generates plain English device insights using Claude.

Model routing:
    claude-haiku-4-5-20251001  — routine summaries (80% of calls)
    claude-sonnet-4-6          — complex anomaly explanation and multi-device
                                 correlation (20% of calls, when warranted)

Insights are cached in Upstash Redis with a 15-minute TTL using the REST API
(no Redis socket required). If Upstash is not configured, caching is skipped
and Claude is called on every request.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

import anthropic
import httpx

from config import Settings
from insights.models import Insight, InsightSeverity
from spire import SpireDevice

logger = logging.getLogger(__name__)

_CACHE_TTL = 900  # 15 minutes in seconds
_HAIKU = "claude-haiku-4-5-20251001"
_SONNET = "claude-sonnet-4-6"


async def get_insight(
    device: SpireDevice,
    history: list[dict[str, Any]],
    settings: Settings,
) -> Insight:
    """
    Return a plain English insight for a property manager about a device.

    Checks Upstash Redis cache first. On cache miss, calls Claude and caches
    the result for 15 minutes.
    """
    if not settings.anthropic_api_key:
        return Insight(
            device_id=device.identity.id,
            message="AI insights require an Anthropic API key — add ANTHROPIC_API_KEY to .env.",
            severity="info",
        )

    cache_key = f"insight:{device.identity.id}:{device.online}"
    cached_raw = await _cache_get(cache_key, settings)
    if cached_raw:
        try:
            data = json.loads(cached_raw)
            return Insight(**data, cached=True)
        except Exception:
            pass

    model = _choose_model(device, history)
    prompt = _build_prompt(device, history)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    message = await client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text: str = message.content[0].text  # type: ignore[union-attr]
    insight = _parse_response(device.identity.id, raw_text, model)

    await _cache_set(cache_key, insight.model_dump_json(), _CACHE_TTL, settings)
    return insight


def _choose_model(device: SpireDevice, history: list[dict[str, Any]]) -> str:
    """
    Route to Sonnet for complex cases; Haiku for routine summaries.

    Complex cases: recent offline events, power draw anomalies,
    multi-hour state changes, or sensors with out-of-range readings.
    """
    api = device.to_api()
    power_draw = api["power_draw"]
    temperature = api["temperature"]
    if not device.online:
        return _SONNET
    if power_draw is not None and power_draw > 2000:
        return _SONNET
    if temperature is not None and (temperature < 10 or temperature > 30):
        return _SONNET
    if api["leak_detected"]:
        return _SONNET
    return _HAIKU


def _build_prompt(device: SpireDevice, history: list[dict[str, Any]]) -> str:
    recent = history[:10] if history else []
    api = device.to_api()
    on_state = device.state.get("on") if device.state else None
    raw_last_seen = api["last_seen"]
    last_seen = (
        raw_last_seen.isoformat() if isinstance(raw_last_seen, datetime) else str(raw_last_seen)
    )
    power_draw = api["power_draw"]
    temperature = api["temperature"]
    humidity = api["humidity"]
    return f"""You are analysing smart device data for a UK property manager.

Device    : {api["name"]}
Type      : {api["type"]}
Vendor    : {device.vendor.vendor}
Online    : {device.online}
Switch    : {"on" if on_state else "off" if on_state is not None else "unknown"}
Power draw: {f"{power_draw:.1f}W" if power_draw is not None else "unknown"}
Temp      : {f"{temperature}°C" if temperature is not None else "N/A"}
Humidity  : {f"{humidity}%" if humidity is not None else "N/A"}
Leak      : {api["leak_detected"]}
Last seen : {last_seen}
History   : {json.dumps(recent)}

Write a brief, plain English insight for the property manager. Focus only on
what is actionable or unusual. If everything is normal, say so briefly.

Respond ONLY in this exact JSON format:
{{"message": "...", "severity": "info"}}

severity must be one of: info, warning, critical
message must be under 120 words."""


def _parse_response(device_id: str, text: str, model: str) -> Insight:
    """Parse Claude's JSON response, falling back gracefully on malformed output."""
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])
        severity: InsightSeverity = data.get("severity", "info")
        if severity not in ("info", "warning", "critical"):
            severity = "info"
        return Insight(
            device_id=device_id,
            message=data.get("message", text[:200]),
            severity=severity,
            model_used=model,
        )
    except Exception:
        return Insight(
            device_id=device_id,
            message=text[:200],
            severity="info",
            model_used=model,
        )


# ── Upstash Redis REST helpers ────────────────────────────────────────────────


async def _cache_get(key: str, settings: Settings) -> str | None:
    if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
        return None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(
                f"{settings.upstash_redis_rest_url}/get/{key}",
                headers={"Authorization": f"Bearer {settings.upstash_redis_rest_token}"},
            )
            if r.status_code == 200:
                result: str | None = r.json().get("result")
                return result
    except Exception as exc:
        logger.debug("Cache get failed: %s", exc)
    return None


async def _cache_set(key: str, value: str, ttl: int, settings: Settings) -> None:
    if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
        return
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.get(
                f"{settings.upstash_redis_rest_url}/set/{key}/{value}/ex/{ttl}",
                headers={"Authorization": f"Bearer {settings.upstash_redis_rest_token}"},
            )
    except Exception as exc:
        logger.debug("Cache set failed: %s", exc)
