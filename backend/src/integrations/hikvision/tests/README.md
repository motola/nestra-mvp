# Hikvision Integration Tests

Unit tests for Hikvision camera adapter and API endpoints.

## Test Coverage

- **Adapter tests** — `HikvisionAdapter` behavior (fetch cameras, record control)
- **API endpoint tests** — HTTP request/response contracts
- **Mock Hikvision API** — Fake responses for testing without real Hikvision cameras

## Running Tests

```bash
cd backend && python -m pytest src/integrations/hikvision/tests/
```

With coverage:

```bash
python -m pytest src/integrations/hikvision/tests/ --cov=src/integrations/hikvision
```

## Test Structure

Typical test file organization:

```python
# test_hikvision.py

@pytest.fixture
def mock_hikvision_client(mocker):
    """Mock Hikvision API."""
    mock_client = MagicMock()
    mock_client.get_cameras.return_value = [
        {
            "id": "camera1",
            "name": "Front Door",
            "ip": "192.168.1.100",
            "online": True,
            "recording": True,
        }
    ]
    return mock_client

async def test_fetch_devices():
    """Adapter fetches cameras from Hikvision."""
    adapter = HikvisionAdapter(client=mock_hikvision_client)
    devices = await adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )
    assert len(devices) == 1
    assert devices[0].device_type == DeviceType.CAMERA

async def test_start_recording():
    """API endpoint starts recording."""
    response = client.post(
        f"/integrations/hikvision/cameras/{CAMERA_ID}/record/start"
    )
    assert response.status_code == 200
    assert response.json()["recording"] is True
```

## Related

- Hikvision adapter: `backend/src/integrations/hikvision/adapter.py`
- Integration base: `backend/src/integrations/base.py`
- Cross-integration tests: `backend/src/integrations/tests/README.md`
