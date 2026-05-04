import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx


class TestLifxClient(unittest.TestCase):
    def _make_response(self, payload: object, status_code: int = 200) -> MagicMock:
        mock = MagicMock(spec=httpx.Response)
        mock.status_code = status_code
        mock.json.return_value = payload
        mock.raise_for_status = MagicMock()
        return mock

    def test_list_lights_returns_raw_json(self) -> None:
        import asyncio

        from demo.lifx import list_lights

        payload = [
            {
                "id": "abc123",
                "label": "Bedroom",
                "power": "on",
                "brightness": 0.8,
                "connected": True,
            }
        ]
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=self._make_response(payload))

        with patch("demo.lifx.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(list_lights())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "Bedroom")

    def test_set_power_sends_correct_payload(self) -> None:
        import asyncio

        from demo.lifx import set_power

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=self._make_response({"results": []}))

        with patch("demo.lifx.httpx.AsyncClient", return_value=mock_client):
            asyncio.run(set_power("abc123", "on"))

        call_kwargs = mock_client.put.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["power"], "on")

    def test_set_brightness_sends_correct_payload(self) -> None:
        import asyncio

        from demo.lifx import set_brightness

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=self._make_response({"results": []}))

        with patch("demo.lifx.httpx.AsyncClient", return_value=mock_client):
            asyncio.run(set_brightness("abc123", 0.5))

        call_kwargs = mock_client.put.call_args.kwargs
        self.assertAlmostEqual(call_kwargs["json"]["brightness"], 0.5)


class TestGoveeClient(unittest.TestCase):
    def _make_response(self, payload: object) -> MagicMock:
        mock = MagicMock(spec=httpx.Response)
        mock.status_code = 200
        mock.json.return_value = payload
        mock.raise_for_status = MagicMock()
        return mock

    def test_list_devices_returns_device_list(self) -> None:
        import asyncio

        from demo.govee import list_devices

        payload = {
            "data": {
                "devices": [
                    {
                        "device": "AA:BB",
                        "model": "H6076",
                        "deviceName": "Strip",
                        "controllable": True,
                    }  # noqa: E501
                ]
            }
        }
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=self._make_response(payload))

        with patch("demo.govee.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(list_devices())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["deviceName"], "Strip")

    def test_set_power_tracks_state(self) -> None:
        import asyncio

        import demo.govee as govee_module
        from demo.govee import set_power

        govee_module._power_state.clear()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=self._make_response({"message": "Success"}))

        with patch("demo.govee.httpx.AsyncClient", return_value=mock_client):
            asyncio.run(set_power("AA:BB", "H6076", on=True))

        self.assertTrue(govee_module._power_state["AA:BB"])

    def test_set_power_off_clears_state(self) -> None:
        import asyncio

        import demo.govee as govee_module
        from demo.govee import set_power

        govee_module._power_state["AA:BB"] = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=self._make_response({"message": "Success"}))

        with patch("demo.govee.httpx.AsyncClient", return_value=mock_client):
            asyncio.run(set_power("AA:BB", "H6076", on=False))

        self.assertFalse(govee_module._power_state["AA:BB"])


class TestDemoRouteNormalisation(unittest.TestCase):
    def test_lifx_to_device_shape(self) -> None:
        from demo.routes import _lifx_to_device

        raw: dict[str, object] = {
            "id": "d073",
            "label": "Kitchen",
            "power": "on",
            "brightness": 0.9,
            "connected": True,
        }
        device = _lifx_to_device(raw)
        self.assertEqual(device.provider, "lifx")
        self.assertTrue(device.power)
        self.assertAlmostEqual(device.brightness or 0, 0.9)

    def test_govee_to_device_shape(self) -> None:
        from demo.routes import _govee_to_device

        raw: dict[str, object] = {
            "device": "AA:BB",
            "model": "H6076",
            "deviceName": "Strip",
            "controllable": True,
            "_power": True,
        }
        device = _govee_to_device(raw)
        self.assertEqual(device.provider, "govee")
        self.assertTrue(device.power)
        self.assertEqual(device.model, "H6076")

    def test_lifx_offline_device(self) -> None:
        from demo.routes import _lifx_to_device

        raw = {"id": "xyz", "label": "Lamp", "power": "off", "brightness": 0.0, "connected": False}
        device = _lifx_to_device(raw)
        self.assertFalse(device.reachable)
        self.assertFalse(device.power)


if __name__ == "__main__":
    unittest.main()
