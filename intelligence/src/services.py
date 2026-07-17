"""Intelligence services — Claude API integration and conversation management."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.clients import ClaudeClient
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


class ClaudeIntegration:
    """Claude API integration with streaming and tool use."""

    def __init__(self, claude_client: ClaudeClient):
        self.claude_client = claude_client

    async def stream_response(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list | None = None,  # type: ignore[type-arg]
    ) -> AsyncGenerator[str, None]:
        """Stream a Claude response with optional tool use."""
        try:
            response = await self.claude_client.create_message(
                messages=messages,  # type: ignore[arg-type]
                system=system_prompt,
                tools=tools,  # type: ignore[arg-type]
            )

            for block in response.content:
                if block.type == "text":
                    yield f"data: {json.dumps({'type': 'text', 'text': block.text})}\n\n"
                elif block.type == "tool_use":
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
