# Govee Integration (Backend)

REST API endpoints for managing Govee smart lights and devices.

## Overview

Govee integration for smart lights, LED strips, and RGB bulbs. Control via cloud API.

## Endpoints

### GET /integrations/govee/devices

List all Govee devices for a property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "device-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "govee_id": "aac200015f67",
    "name": "Living Room Light",
    "device_type": "light",
    "online": true,
    "raw_state": {
      "on": true,
      "brightness": 100,
      "color": { "r": 255, "g": 200, "b": 100 }
    },
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/govee/devices

Add a Govee device to a property.

**Request:**

```json
{
  "govee_id": "aac200015f67",
  "name": "Living Room Light",
  "device_type": "light",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** 201 Created

### POST /integrations/govee/devices/{device_id}/on

Turn on Govee device.

**Response:** 200 OK

### POST /integrations/govee/devices/{device_id}/off

Turn off Govee device.

**Response:** 200 OK

## Files

| File         | Purpose                                               |
| ------------ | ----------------------------------------------------- |
| `adapter.py` | GoveeAdapter implementing IntegrationAdapter protocol |
| `models.py`  | GoveeDeviceModel SQLAlchemy ORM                       |
| `schemas.py` | Request/response DTOs                                 |
| `routes.py`  | FastAPI router with endpoints                         |
| `tests/`     | Test cases                                            |
| `README.md`  | This file                                             |

## Features

- **Cloud API** — Control via Govee cloud (requires API key)
- **Color Control** — Set brightness, color, effects
- **Device Types** — Lights, LED strips, RGB bulbs
- **Scene Support** — Trigger scenes via API

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
