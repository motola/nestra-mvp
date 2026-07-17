# Bluetooth Integration Tests

Unit tests for Bluetooth device adapter and API endpoints.

## Test Coverage

- **Adapter tests** — `BluetoothAdapter` behavior (discover devices, pair/unpair)
- **API endpoint tests** — HTTP request/response contracts
- **Mock Bluetooth API** — Fake device discovery for testing without real hardware

## Running Tests

```bash
cd backend && python -m pytest src/integrations/bluetooth/tests/
```

With coverage:

```bash
python -m pytest src/integrations/bluetooth/tests/ --cov=src/integrations/bluetooth
```

## Test Files

- `test_bluetooth.py` — Adapter and endpoint tests

## Test Structure

Typical test file organization:

```python
# test_bluetooth.py

@pytest.fixture
def mock_bluetooth_client(mocker):
    """Mock Bluetooth discovery."""
    mock_client = MagicMock()
    mock_client.scan.return_value = [
        {"mac": "AA:BB:CC:DD:EE:FF", "name": "Light", "rssi": -45}
    ]
    return mock_client

async def test_fetch_devices():
    """Adapter discovers Bluetooth devices."""
    adapter = BluetoothAdapter(client=mock_bluetooth_client)
    devices = await adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )
    assert len(devices) > 0
    assert devices[0].vendor == "bluetooth"

async def test_pair_device():
    """API endpoint pairs a device."""
    response = client.post("/integrations/bluetooth/pair", json={
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "name": "My Light",
        "property_id": str(PROP_ID),
    })
    assert response.status_code == 201
    assert response.json()["status"] == "paired"
```

## Related

- Bluetooth adapter: `backend/src/integrations/bluetooth/adapter.py`
- Integration base: `backend/src/integrations/base.py`
- Cross-integration tests: `backend/src/integrations/tests/README.md`
