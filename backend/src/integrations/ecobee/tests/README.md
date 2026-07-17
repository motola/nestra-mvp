# Ecobee Integration Tests

Unit tests for Ecobee thermostat adapter and API endpoints.

## Test Coverage

- **Adapter tests** — `EcobeeAdapter` behavior (fetch thermostats, set temperature/mode)
- **API endpoint tests** — HTTP request/response contracts
- **Mock Ecobee API** — Fake responses for testing without real Ecobee hardware

## Running Tests

```bash
cd backend && python -m pytest src/integrations/ecobee/tests/
```

With coverage:

```bash
python -m pytest src/integrations/ecobee/tests/ --cov=src/integrations/ecobee
```

## Test Structure

Typical test file organization:

```python
# test_ecobee.py

@pytest.fixture
def mock_ecobee_client(mocker):
    """Mock Ecobee API."""
    mock_client = MagicMock()
    mock_client.get_thermostats.return_value = [
        {
            "id": "thermostat1",
            "name": "Main Floor",
            "currentTemp": 72,
            "desiredTemp": 70,
            "mode": "heat",
        }
    ]
    return mock_client

async def test_fetch_devices():
    """Adapter fetches thermostats."""
    adapter = EcobeeAdapter(client=mock_ecobee_client)
    devices = await adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )
    assert len(devices) == 1
    assert devices[0].device_type == DeviceType.THERMOSTAT

async def test_set_temperature():
    """API endpoint sets target temperature."""
    response = client.post(
        f"/integrations/ecobee/thermostats/{THERMOSTAT_ID}/temperature",
        json={"target_temp": 72},
    )
    assert response.status_code == 200
    assert response.json()["target_temp"] == 72
```

## Related

- Ecobee adapter: `backend/src/integrations/ecobee/adapter.py`
- Integration base: `backend/src/integrations/base.py`
- Cross-integration tests: `backend/src/integrations/tests/README.md`
