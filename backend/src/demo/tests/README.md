# Demo Module Tests

Tests for demo endpoints and mock device fixtures.

## Purpose

Verify:

- Demo endpoints return mock data
- Mock device state changes persist during request lifecycle
- Error handling (404, invalid IDs)
- Endpoint response formats match contracts

## Test Files

```
tests/
├── README.md (this file)
├── test_govee_ble.py      # Govee BLE light demos
└── test_ble_general.py    # Generic Bluetooth device demos
```

## Running Tests

Run all demo tests:

```bash
cd backend && python -m pytest src/demo/tests/
```

Run specific vendor:

```bash
python -m pytest src/demo/tests/test_govee_ble.py
```

## Example Test

```python
async def test_get_govee_devices_returns_mock_list(client: TestClient):
    response = client.get("/demo/govee/devices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Living Room"

async def test_turn_on_govee_light(client: TestClient):
    # Get first device
    get_resp = client.get("/demo/govee/devices")
    device_id = get_resp.json()[0]["id"]

    # Turn on
    on_resp = client.post(f"/demo/govee/lights/{device_id}/on")
    assert on_resp.status_code == 200

    # Verify state changed
    get_resp2 = client.get("/demo/govee/devices")
    updated = next(d for d in get_resp2.json() if d["id"] == device_id)
    assert updated["on"] == True
```

## State Management

Mock device state is stored in module-level dicts and persists during test:

```python
# govee.py
MOCK_GOVEE_DEVICES = [
    {"id": "demo-govee-1", "name": "Living Room", "on": False, ...},
]

# routes.py
@router.post("/demo/govee/lights/{id}/on")
async def turn_on_light(id: str):
    device = next((d for d in MOCK_GOVEY_DEVICES if d["id"] == id), None)
    device["on"] = True  # State persists
    return device
```

## Notes

- Tests use in-memory mock data (no database)
- State changes persist within a test but are fresh for next test
- Endpoints are development-only; tests verify basic contracts

## Related

- Demo module: `backend/src/demo/README.md`
- Backend test setup: `backend/` (pytest.ini, conftest.py)
