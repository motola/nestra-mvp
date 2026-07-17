# Shelly Integration Tests

Unit tests for Shelly adapter and API endpoints.

## Test Coverage

- **Adapter tests** — `ShellyAdapter` behavior (fetch devices, turn on/off)
- **API endpoint tests** — HTTP request/response contracts
- **Mock local network** — Fake RPC responses for testing without real hardware

## Running Tests

```bash
cd backend && python -m pytest src/integrations/shelly/tests/
```

With coverage:

```bash
python -m pytest src/integrations/shelly/tests/ --cov=src/integrations/shelly
```

## Test Structure

Typical test file organization:

```python
# test_shelly.py

@pytest.fixture
def mock_shelly_controller(mocker):
    """Mock Shelly RPC responses."""
    mock_controller = MagicMock()
    mock_controller.get_state.return_value = {
        "on": True,
        "power": 45.2,
        "voltage": 230.0,
        "current": 0.2,
        "energy": 1250.5,
    }
    return mock_controller

async def test_fetch_devices():
    """Adapter fetches Shelly devices."""
    adapter = ShellyAdapter()
    devices = await adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )
    # Verify devices are in unified Device schema

async def test_turn_on_device():
    """API endpoint turns on device."""
    response = client.post("/integrations/shelly/devices/{id}/on")
    assert response.status_code == 200
```

## Related

- Shelly adapter: `backend/src/integrations/shelly/adapter.py`
- Integration base: `backend/src/integrations/base.py`
- Cross-integration tests: `backend/src/integrations/tests/README.md`
