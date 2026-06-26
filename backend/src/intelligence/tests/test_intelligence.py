"""Intelligence service tests."""

import unittest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from intelligence.services import ConversationService
from shared.db import Base


class TestConversationService(unittest.TestCase):
    """Test conversation management."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test database."""
        cls.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        cls.AsyncSessionLocal = sessionmaker(
            cls.engine, class_=AsyncSession, expire_on_commit=False
        )

    @classmethod
    async def asyncSetUp(self) -> None:
        """Create tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def test_create_conversation(self) -> None:
        """Test creating a conversation."""
        import asyncio

        async def run() -> None:
            async with self.AsyncSessionLocal() as session:
                service = ConversationService(session)
                property_id = uuid4()
                conv = await service.create_conversation(property_id, title="Test Conversation")

                assert conv.id is not None
                assert conv.property_id == property_id
                assert conv.title == "Test Conversation"
                assert conv.message_count == 0

        asyncio.run(run())

    def test_add_message(self) -> None:
        """Test adding messages to a conversation."""
        import asyncio

        async def run() -> None:
            async with self.AsyncSessionLocal() as session:
                service = ConversationService(session)
                property_id = uuid4()
                conv = await service.create_conversation(property_id, title="Test Conversation")

                msg = await service.add_message(conv.id, "user", "Hello, assistant!")

                assert msg.id is not None
                assert msg.conversation_id == conv.id
                assert msg.role == "user"
                assert msg.content == "Hello, assistant!"

        asyncio.run(run())

    def test_get_messages(self) -> None:
        """Test retrieving messages from a conversation."""
        import asyncio

        async def run() -> None:
            async with self.AsyncSessionLocal() as session:
                service = ConversationService(session)
                property_id = uuid4()
                conv = await service.create_conversation(property_id, title="Test Conversation")

                await service.add_message(conv.id, "user", "First message")
                await service.add_message(conv.id, "assistant", "Response")

                messages = await service.get_messages(conv.id)

                assert len(messages) == 2
                assert messages[0].role == "user"
                assert messages[1].role == "assistant"

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
