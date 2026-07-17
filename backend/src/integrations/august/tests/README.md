# August Integration Tests

Unit tests for August Smart Lock adapter and API endpoints.

## Test Coverage

- **Adapter tests** — `AugustAdapter` behavior (fetch devices, execute commands)
- **API endpoint tests** — HTTP request/response contracts
- **Mock August API** — Fake responses for testing without real August hardware

## Running Tests

```bash
cd backend && python -m pytest src/integrations/august/tests/
```

With coverage:

```bash
python -m pytest src/integrations/august/tests/ --cov=src/integrations/august
```

## Test Structure

Typical test file organization:

```python
# test_august.py

@pytest.fixture
def mock_august_client(mocker):
    """Mock August API responses."""
    mock_client = MagicMock()
    mock_client.get_locks.return_value = [
        {"id": "lock1", "name": "Front Door", "online": True, ...}
    ]
    return mock_client

async def test_fetch_devices():
    """Adapter can fetch locks from August API."""
    adapter = AugustAdapter(client=mock_august_client)
    devices = await adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )
    assert len(devices) == 1
    assert devices[0].device_type == DeviceType.LOCK

async def test_lock_device():
    """Adapter can lock a device."""
    adapter = AugustAdapter(client=mock_august_client)
    device = Device(...)
    success = await adapter.execute(device, "lock", {})
    assert success is True
```

## Related

- August adapter: `backend/src/integrations/august/adapter.py`
- Integration base: `backend/src/integrations/base.py`
- Cross-integration tests: `backend/src/integrations/tests/README.md`
