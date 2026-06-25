import unittest
from uuid import uuid4

from config import get_settings


class TestAugustLocks(unittest.TestCase):
    """Test August Smart Lock operations."""

    def setUp(self) -> None:
        """Clear mock storage before each test."""
        import integrations.august.routes as routes

        routes._MOCK_LOCKS.clear()
        routes._MOCK_INTEGRATIONS.clear()
        self.settings = get_settings()

    def test_add_lock_success(self) -> None:
        """Test successfully adding an August Smart Lock."""
        import asyncio

        from integrations.august.routes import add_lock
        from integrations.august.schemas import AugustLockIn

        lock_in = AugustLockIn(
            lock_id="august_123",
            name="Front Door",
            location="Building A, Unit 101",
            property_id=uuid4(),
            battery_level=95,
            is_locked=True,
            model="August Pro",
        )

        result = asyncio.run(add_lock(lock_in, self.settings))

        self.assertIsNotNone(result.id)
        self.assertEqual(result.name, "Front Door")
        self.assertEqual(result.battery_level, 95)
        self.assertTrue(result.is_locked)

    def test_add_duplicate_lock_fails(self) -> None:
        """Test that adding same lock twice fails."""
        import asyncio

        from fastapi import HTTPException

        from integrations.august.routes import add_lock
        from integrations.august.schemas import AugustLockIn

        lock_id = "august_123"
        lock_in = AugustLockIn(
            lock_id=lock_id,
            name="Front Door",
            location="Building A",
            property_id=uuid4(),
        )

        asyncio.run(add_lock(lock_in, self.settings))

        # Try to add same lock again
        with self.assertRaises(HTTPException) as context:
            asyncio.run(add_lock(lock_in, self.settings))

        self.assertEqual(context.exception.status_code, 409)

    def test_lock_device_success(self) -> None:
        """Test successfully locking a device."""
        import asyncio

        from integrations.august.routes import add_lock, lock_device
        from integrations.august.schemas import AugustLockIn

        lock_in = AugustLockIn(
            lock_id="august_123",
            name="Front Door",
            location="Building A",
            property_id=uuid4(),
            is_locked=False,
        )

        added_lock = asyncio.run(add_lock(lock_in, self.settings))
        result = asyncio.run(lock_device(added_lock.id, self.settings))

        self.assertEqual(result.status, "success")
        self.assertIn("locked", result.message.lower())

    def test_unlock_device_success(self) -> None:
        """Test successfully unlocking a device."""
        import asyncio

        from integrations.august.routes import add_lock, unlock_device
        from integrations.august.schemas import AugustLockIn

        lock_in = AugustLockIn(
            lock_id="august_123",
            name="Front Door",
            location="Building A",
            property_id=uuid4(),
            is_locked=True,
        )

        added_lock = asyncio.run(add_lock(lock_in, self.settings))
        result = asyncio.run(unlock_device(added_lock.id, self.settings))

        self.assertEqual(result.status, "success")
        self.assertIn("unlocked", result.message.lower())

    def test_list_locks_by_property(self) -> None:
        """Test listing locks filtered by property."""
        import asyncio

        from integrations.august.routes import add_lock, list_locks
        from integrations.august.schemas import AugustLockIn

        property_1 = uuid4()
        property_2 = uuid4()

        lock1 = AugustLockIn(
            lock_id="lock_001",
            name="Door 1",
            location="Building A",
            property_id=property_1,
        )
        lock2 = AugustLockIn(
            lock_id="lock_002",
            name="Door 2",
            location="Building B",
            property_id=property_2,
        )

        asyncio.run(add_lock(lock1, self.settings))
        asyncio.run(add_lock(lock2, self.settings))

        all_locks = asyncio.run(list_locks(None, self.settings))
        self.assertEqual(len(all_locks), 2)

        locks_p1 = asyncio.run(list_locks(property_1, self.settings))
        self.assertEqual(len(locks_p1), 1)
        self.assertEqual(locks_p1[0].property_id, property_1)

    def test_remove_lock_success(self) -> None:
        """Test successfully removing a lock."""
        import asyncio

        from integrations.august.routes import add_lock, remove_lock
        from integrations.august.schemas import AugustLockIn

        lock_in = AugustLockIn(
            lock_id="august_123",
            name="Front Door",
            location="Building A",
            property_id=uuid4(),
        )

        added_lock = asyncio.run(add_lock(lock_in, self.settings))
        result = asyncio.run(remove_lock(added_lock.id, self.settings))

        self.assertEqual(result.status, "success")
        self.assertIn("removed", result.message.lower())


if __name__ == "__main__":
    unittest.main()
