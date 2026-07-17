# TP-Link Smart Devices Integration (Backend)

REST API endpoints for managing TP-Link smart plugs, lights, and switches.

## Overview

TP-Link integration for smart home devices. Sync plugs and lights, monitor energy usage, and control power state.

## Endpoints

### GET /integrations/tplink/devices

List all TP-Link devices for a property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property
- `device_type` (string, optional): Filter by type (plug, light, switch)

**Response:** 200 OK

```json
[
  {
    "id": "device-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "tplink_id": "tplink_xyz789",
    "name": "Living Room Plug",
    "type": "plug",
    "model": "HS100",
    "online": true,
    "power_state": "on",
    "power_usage": 45.2,
    "energy_today": 2.1,
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/tplink/devices

Add a TP-Link device to a property.

**Request:**

```json
{
  "tplink_id": "tplink_xyz789",
  "name": "Living Room Plug",
  "type": "plug",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** 201 Created

```json
{
  "id": "device-uuid",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "tplink_id": "tplink_xyz789",
  "name": "Living Room Plug",
  "type": "plug",
  "online": true,
  "power_state": "on",
  "power_usage": 45.2,
  "last_sync": "2026-06-24T14:30:00Z",
  "created_at": "2026-06-24T14:30:00Z"
}
```

### POST /integrations/tplink/devices/{device_id}/on

Turn on device.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Living Room Plug turned on",
  "power_state": "on",
  "power_usage": 45.2
}
```

### POST /integrations/tplink/devices/{device_id}/off

Turn off device.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Living Room Plug turned off",
  "power_state": "off",
  "power_usage": 0
}
```

### GET /integrations/tplink/devices/{device_id}/energy

Get energy usage statistics.

**Response:** 200 OK

```json
{
  "device_id": "device-uuid",
  "power_usage_current": 45.2,
  "power_usage_average": 38.5,
  "energy_today": 2.1,
  "energy_this_month": 45.3,
  "last_sync": "2026-06-24T14:30:00Z"
}
```

## Files

| File                   | Purpose                             |
| ---------------------- | ----------------------------------- |
| `adapter.py`           | TPLinkAdapter implementing protocol |
| `domain.py`            | TPLinkDevice Pydantic model         |
| `models.py`            | TPLinkDeviceModel SQLAlchemy ORM    |
| `schemas.py`           | Request/response DTOs               |
| `routes.py`            | FastAPI router with endpoints       |
| `tests/test_tplink.py` | Test cases for all flows            |
| `README.md`            | This file                           |

## Types

### TPLinkDevice (domain.py)

```python
class TPLinkDevice(BaseModel):
    id: UUID
    property_id: UUID
    integration_id: UUID
    tplink_id: str              # Unique to TP-Link
    name: str
    type: Literal["plug", "light", "switch"]
    model: str
    online: bool
    power_state: Literal["on", "off"]
    power_usage: float          # Watts
    energy_today: float         # kWh
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
```

## Testing

Run tests:

```bash
cd backend && python -m pytest src/integrations/tplink/
```

Test coverage includes:

- Adding device
- Power control (on/off)
- Energy usage tracking
- List devices with filtering
- Online status monitoring

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
