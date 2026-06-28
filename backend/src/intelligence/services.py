"""Intelligence services — Claude API integration and conversation management."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from intelligence.domain import Conversation, Message
from intelligence.models import ConversationModel, MessageModel

logger = logging.getLogger(__name__)


class ConversationService:
    """Manage conversations and messages."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, property_id: UUID, title: str) -> Conversation:
        """Create a new conversation."""
        now = datetime.now(UTC)
        conv = ConversationModel(
            property_id=property_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self.session.add(conv)
        await self.session.flush()
        return Conversation(
            id=conv.id,
            property_id=conv.property_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=0,
        )

    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        """Get a conversation by ID."""
        result = await self.session.execute(
            select(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return None
        return Conversation(
            id=conv.id,
            property_id=conv.property_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages),
        )

    async def add_message(self, conversation_id: UUID, role: str, content: str) -> Message:
        """Add a message to a conversation."""
        now = datetime.now(UTC)
        msg = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=now,
        )
        self.session.add(msg)

        conv = await self.session.execute(
            select(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        conv_model = conv.scalar_one()
        conv_model.updated_at = now
        self.session.add(conv_model)

        await self.session.flush()
        return Message(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
        )

    async def get_messages(self, conversation_id: UUID) -> list[Message]:
        """Get all messages in a conversation."""
        result = await self.session.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at)
        )
        messages = result.scalars().all()
        return [
            Message(
                id=m.id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ]


class ClaudeService:
    """Claude API integration with streaming and tool use."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def stream_response(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list | None = None,  # type: ignore[type-arg]
    ) -> AsyncGenerator[str, None]:
        """Stream a Claude response with optional tool use."""
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)

            stream_context = client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,  # type: ignore[arg-type]
                tools=tools,  # type: ignore[arg-type]
            )
            async with stream_context as stream:
                async for text in stream.text_stream:
                    yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"

                final_message = await stream.get_final_message()
                for block in final_message.content:
                    if block.type == "tool_use":
                        tool_use_data = {
                            "type": "tool_use",
                            "tool_name": block.name,
                            "tool_input": block.input,
                        }
                        yield f"data: {json.dumps(tool_use_data)}\n\n"
        except Exception as exc:
            logger.error("Claude stream error: %s", exc)
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        finally:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
