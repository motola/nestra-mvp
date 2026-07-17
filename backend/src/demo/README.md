# Demo Module

Development and demo endpoints for testing device interactions without real hardware.

## Overview

Provides mock devices and test data for frontend development and demos. **Not for production** — endpoints will be removed before launch.

## Structure

```
demo/
├── README.md (this file)
├── __init__.py
├── routes.py        # FastAPI demo endpoints
├── govee.py         # Govee light demo fixtures
├── govee_ble.py     # Govee BLE demo fixtures
├── ble_general.py   # Generic Bluetooth demo fixtures
└── tests/
    ├── test_govee_ble.py
    └── test_ble_general.py
```

## Demo Endpoints

Router mounted at root (included in `main.py`).

### Govee Lights (HTTP)

- `GET /demo/govee/devices` — List mock Govee lights
- `POST /demo/govee/lights/{id}/on` — Turn on light
- `POST /demo/govee/lights/{id}/off` — Turn off light
- `POST /demo/govee/lights/{id}/brightness` — Set brightness (0-100)

### Govee Lights (BLE)

- `GET /demo/govee-ble/devices` — List mock Govee BLE lights
- `POST /demo/govee-ble/lights/{id}/on` — Turn on
- `POST /demo/govee-ble/lights/{id}/brightness` — Set brightness

### Generic Bluetooth Devices

- `GET /demo/bluetooth/devices` — List mock Bluetooth devices (various types)
- `POST /demo/bluetooth/{id}/on` — Power on generic Bluetooth device
- `POST /demo/bluetooth/{id}/off` — Power off

## Usage

Endpoints return mock device state without calling real APIs:

```bash
curl http://localhost:8000/demo/govee/devices

# Response:
[
  {
    "id": "demo-govee-1",
    "name": "Living Room Light",
    "type": "light",
    "online": true,
    "brightness": 75,
    "color": "#ff6b6b"
  },
  ...
]
```

## Mock Data

### govee.py

Fixtures for Govee smart lights (HTTP API):

```python
MOCK_GOVEE_DEVICES = [
    {
        "id": "demo-govee-1",
        "name": "Living Room",
        "type": "light",
        "online": True,
        "brightness": 75,
        "color": "#ff6b6b",
    },
    ...
]
```

### govee_ble.py

Fixtures for Govee BLE lights (Bluetooth Low Energy):

```python
MOCK_GOVEE_BLE_DEVICES = [
    {
        "id": "demo-govee-ble-1",
        "name": "Desk Lamp",
        "type": "light",
        "online": True,
        "rssi": -45,
        "brightness": 50,
    },
    ...
]
```

### ble_general.py

Generic Bluetooth device fixtures (various types):

```python
MOCK_BLE_DEVICES = [
    {
        "id": "demo-ble-1",
        "mac": "AA:BB:CC:DD:EE:FF",
        "name": "Smart Speaker",
        "type": "speaker",
        "online": True,
        "rssi": -55,
    },
    ...
]
```

## Adding Demo Endpoints

1. Create fixture file (e.g., `lifx.py`)
2. Define mock device state
3. Add route handlers in `routes.py`:

```python
from demo.lifx import MOCK_LIFX_DEVICES

@router.get("/demo/lifx/devices")
async def get_lifx_devices() -> list:
    return MOCK_LIFX_DEVICES

@router.post("/demo/lifx/lights/{id}/on")
async def turn_on_lifx_light(id: str) -> dict:
    device = next((d for d in MOCK_LIFX_DEVICES if d["id"] == id), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device["on"] = True
    return {"status": "success", "device": device}
```

4. Add tests in `tests/test_lifx.py`

## Testing

Run demo tests:

```bash
cd backend && python -m pytest src/demo/tests/
```

Tests verify:

- Endpoints return mock data
- State changes persist during request
- Error handling (404, etc)

## Future: Remove Before Production

Demo endpoints will be removed before launch:

- Delete `backend/src/demo/` directory
- Remove demo router from `main.py`
- Replace with real device integration tests

## Related

- Backend overview: `backend/src/README.md`
- Property integration: `backend/src/property/README.md`
- Integrations (real adapters): `backend/src/integrations/README.md`
