"""Intelligence API routes — chat and conversation endpoints."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from intelligence.domain import ChatRequest, Conversation
from intelligence.services import ClaudeService, ConversationService
from shared.db import SessionLocal

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


async def _get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


@router.post("/conversations")
async def create_conversation(
    property_id: UUID,
    session: AsyncSession = Depends(_get_session),  # noqa: B008
) -> Conversation:
    """Create a new conversation for a property."""
    service = ConversationService(session)
    conv = await service.create_conversation(property_id, title="New Conversation")
    await session.commit()
    return conv


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(_get_session),  # noqa: B008
) -> Conversation | None:
    """Get a conversation by ID."""
    service = ConversationService(session)
    return await service.get_conversation(conversation_id)


@router.post("/conversations/{conversation_id}/messages")
async def chat(
    conversation_id: UUID,
    request: ChatRequest,
    session: AsyncSession = Depends(_get_session),  # noqa: B008
) -> StreamingResponse:
    settings = get_settings()
    """Stream a chat response for a conversation."""
    conv_service = ConversationService(session)
    claude_service = ClaudeService(settings)

    conv = await conv_service.get_conversation(conversation_id)
    if not conv:
        raise ValueError(f"Conversation {conversation_id} not found")

    await conv_service.add_message(conversation_id, "user", request.message)
    await session.commit()

    system_prompt = (
        "You are Nestra, an AI assistant for property managers. "
        "Help them understand smart home devices, interpret alerts, and take action. "
        "Be concise, practical, and professional."
    )

    messages = [{"role": m.role, "content": m.content} for m in request.history]
    messages.append({"role": "user", "content": request.message})

    async def stream_and_save() -> AsyncGenerator[str, None]:
        full_response = ""
        async for chunk in claude_service.stream_response(system_prompt, messages):
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()
                try:
                    data = json.loads(data_str)
                    if data.get("type") == "text" and data.get("text"):
                        full_response += data["text"]
                except json.JSONDecodeError:
                    pass
            yield chunk

        if full_response:
            await conv_service.add_message(conversation_id, "assistant", full_response)
            await session.commit()

    return StreamingResponse(
        stream_and_save(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
