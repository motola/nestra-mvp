# TP-Link Integration Tests

Unit tests for TP-Link device adapter and API endpoints.

## Test Coverage

- **Adapter tests** — `TPLinkAdapter` behavior (fetch devices, power control, energy tracking)
- **API endpoint tests** — HTTP request/response contracts
- **Mock TP-Link API** — Fake responses for testing without real TP-Link hardware

## Running Tests

```bash
cd backend && python -m pytest src/integrations/tplink/tests/
```

With coverage:

```bash
python -m pytest src/integrations/tplink/tests/ --cov=src/integrations/tplink
```

## Test Structure

Typical test file organization:

```python
# test_tplink.py

@pytest.fixture
def mock_tplink_client(mocker):
    """Mock TP-Link API."""
    mock_client = MagicMock()
    mock_client.get_devices.return_value = [
        {
            "id": "device1",
            "name": "Living Room Plug",
            "type": "plug",
            "online": True,
            "power_state": "on",
            "power_usage": 45.2,
        }
    ]
    return mock_client

async def test_fetch_devices():
    """Adapter fetches TP-Link devices."""
    adapter = TPLinkAdapter(client=mock_tplink_client)
    devices = await adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )
    assert len(devices) == 1
    assert devices[0].vendor == "tplink"

async def test_turn_on_device():
    """API endpoint turns on device."""
    response = client.post(
        f"/integrations/tplink/devices/{DEVICE_ID}/on"
    )
    assert response.status_code == 200
    assert response.json()["power_state"] == "on"

async def test_get_energy_usage():
    """API endpoint returns energy stats."""
    response = client.get(
        f"/integrations/tplink/devices/{DEVICE_ID}/energy"
    )
    assert response.status_code == 200
    data = response.json()
    assert "power_usage_current" in data
    assert "energy_today" in data
```

## Related

- TP-Link adapter: `backend/src/integrations/tplink/adapter.py`
- Integration base: `backend/src/integrations/base.py`
- Cross-integration tests: `backend/src/integrations/tests/README.md`
