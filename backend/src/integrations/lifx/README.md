# LIFX Integration (Backend)

REST API endpoints for managing LIFX smart lights.

## Overview

LIFX integration for WiFi-connected smart lights. Control via cloud API with no hub required.

## Endpoints

### GET /integrations/lifx/devices

List all LIFX devices for a property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "device-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "lifx_id": "d073d5014bfe",
    "name": "Bedroom Light",
    "device_type": "light",
    "online": true,
    "raw_state": {
      "on": true,
      "brightness": 0.8,
      "color": { "hue": 0, "saturation": 1, "kelvin": 3500 }
    },
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/lifx/devices

Add a LIFX device to a property.

**Request:**

```json
{
  "lifx_id": "d073d5014bfe",
  "name": "Bedroom Light",
  "device_type": "light",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** 201 Created

### POST /integrations/lifx/devices/{device_id}/on

Turn on LIFX light.

**Response:** 200 OK

### POST /integrations/lifx/devices/{device_id}/off

Turn off LIFX light.

**Response:** 200 OK

## Files

| File         | Purpose                                              |
| ------------ | ---------------------------------------------------- |
| `adapter.py` | LifxAdapter implementing IntegrationAdapter protocol |
| `models.py`  | LifxDeviceModel SQLAlchemy ORM                       |
| `schemas.py` | Request/response DTOs                                |
| `routes.py`  | FastAPI router with endpoints                        |
| `tests/`     | Test cases                                           |
| `README.md`  | This file                                            |

## Features

- **Cloud API** — Control via LIFX cloud (requires API token)
- **No Hub** — WiFi-connected, communicates directly
- **Color Tuning** — Hue, saturation, kelvin temperature
- **Brightness Control** — Smooth dimming

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
