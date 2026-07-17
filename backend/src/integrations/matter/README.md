# Matter Integration (Backend)

REST API endpoints for managing Matter protocol devices.

## Overview

Matter protocol integration for smart home devices. Universal protocol supported by major manufacturers.

## Endpoints

### GET /integrations/matter/devices

List all Matter devices for a property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "device-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "matter_id": "node-123",
    "name": "Kitchen Light",
    "device_type": "light",
    "online": true,
    "raw_state": {
      "on": true,
      "brightness": 254
    },
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/matter/devices

Add a Matter device to a property.

**Request:**

```json
{
  "matter_id": "node-123",
  "name": "Kitchen Light",
  "device_type": "light",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** 201 Created

### POST /integrations/matter/devices/{device_id}/on

Turn on Matter device.

**Response:** 200 OK

### POST /integrations/matter/devices/{device_id}/off

Turn off Matter device.

**Response:** 200 OK

## Files

| File         | Purpose                                                |
| ------------ | ------------------------------------------------------ |
| `adapter.py` | MatterAdapter implementing IntegrationAdapter protocol |
| `models.py`  | MatterDeviceModel SQLAlchemy ORM                       |
| `schemas.py` | Request/response DTOs                                  |
| `routes.py`  | FastAPI router with endpoints                          |
| `tests/`     | Test cases                                             |
| `README.md`  | This file                                              |

## Features

- **Universal Protocol** — Works with any Matter-certified device
- **Controller-Based** — Requires Matter controller/bridge
- **Wide Support** — Philips Hue, IKEA Tradfri, Eve, etc.

## Requirements

- Matter controller (Home Hub, smart display, etc.)
- Matter device credentials/certificates
- Network access to controller

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
