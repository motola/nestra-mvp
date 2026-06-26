"""Chat endpoint — agentic portfolio assistant with SSE streaming."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import SessionDep, SettingsDep
from config import Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


async def _build_portfolio_context(settings: Settings, session: AsyncSession) -> str:
    from services.alert_service import list_active_alerts
    from services.property_service import list_properties

    try:
        props = await list_properties(session, settings)
        alerts = await list_active_alerts(session)
    except Exception as exc:
        logger.warning("Could not fetch portfolio context: %s", exc)
        return ""

    if settings.demo_mode:
        from demo.alerts import get_demo_alerts
        from models.alert import Alert

        demo_alerts = [Alert(**a) for a in get_demo_alerts() if not a.get("dismissed")]
        alerts = list(alerts) + demo_alerts

    lines = ["## Your portfolio\n"]
    for p in props:
        status_label = {
            "all_clear": "All Clear",
            "needs_attention": "Needs Attention",
            "critical": "Critical",
        }.get(p.status, p.status)
        lines.append(
            f"- **{p.name}** ({p.address}) — {p.device_count} devices, status: {status_label}"
        )

    if alerts:
        lines.append("\n## Active alerts\n")
        for a in alerts:
            lines.append(
                f"- [{a.severity.upper()}] {a.property_name} / {a.device_name}: {a.message}"
            )

    return "\n".join(lines)


@router.post("/")
async def chat(
    request: ChatRequest, settings: SettingsDep, session: SessionDep
) -> StreamingResponse:
    """Stream a portfolio-aware chat response via SSE."""
    portfolio_context = await _build_portfolio_context(settings, session)

    system_prompt = (
        "You are Nestra, an AI assistant for property managers using the Alphacon platform. "
        "You help them understand their smart home device data, interpret alerts, identify issues, "
        "and take action. Be concise, practical, and professional. "
        "Use plain English — no jargon. When referencing specific properties or devices, "
        "be specific. If asked to take an action you can't perform, say so and "
        "suggest what the user can do manually.\n\n" + portfolio_context
    )

    messages = [{"role": m.role, "content": m.content} for m in request.history]
    messages.append({"role": "user", "content": request.message})

    async def stream() -> AsyncGenerator[str, None]:
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            async with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,  # type: ignore[arg-type]
            ) as stream_ctx:
                async for text in stream_ctx.text_stream:
                    yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"
        except Exception:
            logger.exception("Chat stream error")
            yield f"data: {json.dumps({'type': 'error', 'message': 'An internal error has occurred.'})}\n\n"
        finally:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
