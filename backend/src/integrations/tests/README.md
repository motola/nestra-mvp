# Integration Tests

Cross-integration tests for device sync pipeline and adapter factory.

## Purpose

Test integration-level functionality that spans multiple vendors:

- Device sync pipeline (fetch from vendor → normalize → store)
- Adapter factory (creating vendor-specific adapters)
- Device repository operations
- Multi-vendor device filtering and queries

## Structure

```
tests/
├── README.md (this file)
└── test_device_sync_pipeline.py   # Device sync end-to-end
```

## Key Tests

### test_device_sync_pipeline.py

End-to-end device sync pipeline:

```python
async def test_sync_devices_from_august():
    # 1. Set up August adapter with mock client
    # 2. Call fetch_devices()
    # 3. Verify returned Device objects
    # 4. Store in repository
    # 5. Query and verify persistence

async def test_sync_devices_from_multiple_integrations():
    # Sync from August and Bluetooth simultaneously
    # Verify all devices in unified Device schema
    # Query by property returns all devices

async def test_adapter_factory_creates_correct_adapter():
    # Factory.get("august") returns AugustAdapter
    # Factory.get("bluetooth") returns BluetoothAdapter
    # Unknown vendor raises error
```

## Running Tests

Run all integration tests:

```bash
cd backend && python -m pytest src/integrations/tests/
```

Run specific test file:

```bash
python -m pytest src/integrations/tests/test_device_sync_pipeline.py
```

Run with verbose output:

```bash
python -m pytest -v src/integrations/tests/
```

## Vendor-Specific Tests

Each vendor directory has its own test file:

- `august/tests/test_august.py` — August-specific tests
- `bluetooth/tests/test_bluetooth.py` — Bluetooth-specific tests
- `ecobee/tests/test_ecobee.py` — Ecobee-specific tests
- etc.

These test adapter-specific logic (parsing vendor APIs, control commands).

## Mocking Strategy

Integration tests use mocks for:

- HTTP client (don't call real vendor APIs)
- Database repository (in-memory mock)
- Clock (freeze time for reproducibility)

Example mock setup:

```python
@pytest.fixture
def august_adapter(mocker):
    # Mock Anthropic SDK
    mock_client = MagicMock()
    mock_client.get_devices.return_value = [
        {"id": "lock1", "name": "Front Door", "online": True, ...}
    ]

    adapter = AugustAdapter(client=mock_client)
    return adapter

async def test_fetch_devices_from_august(august_adapter):
    devices = await august_adapter.fetch_devices(
        organization_id=ORG_ID,
        property_id=PROP_ID,
        integration_id=INT_ID,
    )

    assert len(devices) == 1
    assert devices[0].device_type == DeviceType.LOCK
    assert devices[0].vendor == "august"
```

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Device sync pipeline: `backend/src/integrations/sync.py`
- Adapter factory: `backend/src/integrations/factory.py`
- Property repository: `backend/src/property/repository/README.md`
