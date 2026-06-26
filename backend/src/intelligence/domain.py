"""Intelligence domain models — conversations and messages."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"frozen": True}


class Conversation(BaseModel):
    """An AI conversation with a property manager."""

    id: UUID
    property_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"frozen": True}


class ChatRequest(BaseModel):
    """Request to send a message in a conversation."""

    message: str
    history: list[Message] = Field(default_factory=list)
