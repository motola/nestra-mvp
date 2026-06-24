import unittest
from uuid import uuid4

from config import get_settings


class TestHikvisionCameras(unittest.TestCase):
    """Test Hikvision Camera operations."""

    def setUp(self) -> None:
        """Clear mock storage."""
        import integrations.hikvision.routes as routes

        routes._MOCK_CAMERAS.clear()
        routes._MOCK_INTEGRATIONS.clear()
        self.settings = get_settings()

    def test_add_camera_success(self) -> None:
        """Test adding a camera."""
        import asyncio

        from integrations.hikvision.routes import add_camera
        from integrations.hikvision.schemas import HikvisionCameraIn

        camera_in = HikvisionCameraIn(
            camera_id="hik_123",
            name="Entrance",
            property_id=uuid4(),
            location="Front Door",
        )

        result = asyncio.run(add_camera(camera_in, self.settings))

        self.assertIsNotNone(result.id)
        self.assertEqual(result.name, "Entrance")
        self.assertTrue(result.is_online)

    def test_list_cameras(self) -> None:
        """Test listing cameras."""
        import asyncio

        from integrations.hikvision.routes import add_camera, list_cameras
        from integrations.hikvision.schemas import HikvisionCameraIn

        prop_id = uuid4()
        camera_in = HikvisionCameraIn(
            camera_id="hik_123",
            name="Entrance",
            property_id=prop_id,
        )

        asyncio.run(add_camera(camera_in, self.settings))
        cameras = asyncio.run(list_cameras(prop_id, self.settings))

        self.assertEqual(len(cameras), 1)


if __name__ == "__main__":
    unittest.main()
