"""Intelligence API routes — chat and conversation endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from domain import ChatRequest, Conversation

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/conversations")
async def create_conversation(
    property_id: UUID,
) -> dict[str, str]:
    """Create a new conversation for a property."""
    # TODO: Integrate with backend database
    return {"status": "ok", "message": "TODO: Implement conversation creation"}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
) -> dict[str, str]:
    """Get a conversation by ID."""
    # TODO: Integrate with backend database
    return {"status": "ok", "message": "TODO: Implement conversation retrieval"}


@router.post("/conversations/{conversation_id}/messages")
async def chat(
    conversation_id: UUID,
    request: ChatRequest,
) -> dict[str, str]:
    """Send a message in a conversation."""
    # TODO: Integrate with Claude API and backend
    return {
        "status": "ok",
        "message": f"TODO: Process message: {request.message}",
    }
