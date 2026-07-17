# Shelly Integration (Backend)

REST API endpoints and local network control for Shelly smart devices.

## Overview

Direct local-network integration for Shelly smart plugs and relays. Communicate via local RPC API (no cloud dependency).

## Endpoints

### GET /integrations/shelly/devices

List all Shelly devices for a property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "device-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "shelly_id": "shellyplug-abc123",
    "name": "Living Room Plug",
    "ip_address": "192.168.1.50",
    "online": true,
    "raw_state": {
      "on": true,
      "power": 45.2,
      "voltage": 230.0,
      "current": 0.2,
      "energy": 1250.5
    },
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/shelly/devices

Add a Shelly device to a property.

**Request:**

```json
{
  "shelly_id": "shellyplug-abc123",
  "name": "Living Room Plug",
  "ip_address": "192.168.1.50",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** 201 Created

```json
{
  "id": "device-uuid",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "shelly_id": "shellyplug-abc123",
  "name": "Living Room Plug",
  "ip_address": "192.168.1.50",
  "online": true,
  "raw_state": {},
  "last_sync": "2026-06-24T14:30:00Z",
  "created_at": "2026-06-24T14:30:00Z"
}
```

### POST /integrations/shelly/devices/{device_id}/on

Turn on Shelly device.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Living Room Plug turned on"
}
```

### POST /integrations/shelly/devices/{device_id}/off

Turn off Shelly device.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Living Room Plug turned off"
}
```

## Files

| File         | Purpose                                                |
| ------------ | ------------------------------------------------------ |
| `adapter.py` | ShellyAdapter implementing IntegrationAdapter protocol |
| `models.py`  | ShellyDeviceModel SQLAlchemy ORM                       |
| `schemas.py` | Request/response DTOs                                  |
| `routes.py`  | FastAPI router with endpoints                          |
| `tests/`     | Test cases                                             |
| `README.md`  | This file                                              |

## Features

- **Local Network Only** — Direct RPC communication, no cloud dependency
- **Power Monitoring** — Track real-time power draw
- **Relay Control** — Turn on/off via local network
- **State Tracking** — Voltage, current, energy consumption

## Device Type

Shelly devices map to `DeviceType.PLUG` in the unified device schema.

## Testing

Run tests:

```bash
cd backend && python -m pytest src/integrations/shelly/tests/
```

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
- IntegrationAdapter protocol: `backend/src/integrations/base.py`
