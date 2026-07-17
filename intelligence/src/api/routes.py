"""Intelligence API routes — chat and conversation endpoints."""

from __future__ import annotations

import json
import os
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from shared.clients import ClaudeClient
from shared.db import SessionLocal
from intelligence.domain import ChatRequest, Conversation
from intelligence.executor import DeviceExecutor
from intelligence.services import ClaudeIntegration, ConversationService
from intelligence.tools import DEVICE_TOOLS

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
    """Stream a chat response for a conversation."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    claude_client = ClaudeClient(api_key=api_key)
    conv_service = ConversationService(session)
    claude_integration = ClaudeIntegration(claude_client)

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

    executor = DeviceExecutor(session)

    async def stream_and_save() -> AsyncGenerator[str, None]:
        full_response = ""
        tool_uses: list[dict[str, object]] = []

        async for chunk in claude_integration.stream_response(
            system_prompt, messages, tools=DEVICE_TOOLS
        ):
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()
                try:
                    data = json.loads(data_str)
                    if data.get("type") == "text" and data.get("text"):
                        full_response += data["text"]
                    elif data.get("type") == "tool_use":
                        tool_uses.append(data)
                except json.JSONDecodeError:
                    pass
            yield chunk

        for tool_use in tool_uses:
            tool_name = tool_use.get("tool_name")
            tool_input = tool_use.get("tool_input", {})
            if isinstance(tool_name, str) and isinstance(tool_input, dict):
                result = await executor.execute_tool(tool_name, tool_input)
            else:
                result = "Error: Invalid tool use format"
            tool_result = {
                "type": "tool_result",
                "tool_name": tool_name,
                "result": result,
            }
            yield f"data: {json.dumps(tool_result)}\n\n"

        if full_response or tool_uses:
            response_text = full_response or f"Executed {len(tool_uses)} tool(s)"
            await conv_service.add_message(conversation_id, "assistant", response_text)
            await session.commit()

    return StreamingResponse(
        stream_and_save(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
