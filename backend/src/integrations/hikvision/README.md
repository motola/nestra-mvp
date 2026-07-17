# Hikvision Cameras Integration (Backend)

REST API endpoints for managing Hikvision IP cameras.

## Overview

Hikvision integration for security camera management. Sync cameras, monitor status, trigger recordings, and manage settings.

## Endpoints

### GET /integrations/hikvision/cameras

List all Hikvision cameras for a property.

**Query Parameters:**

- `property_id` (UUID, optional): Filter by property

**Response:** 200 OK

```json
[
  {
    "id": "camera-uuid",
    "property_id": "550e8400-e29b-41d4-a716-446655440000",
    "hikvision_id": "hikvision_abc123",
    "name": "Front Door",
    "location": "Main Entrance",
    "model": "DS-2CD2143G0-I",
    "ip_address": "192.168.1.100",
    "online": true,
    "recording": true,
    "resolution": "1920x1080",
    "frame_rate": 30,
    "last_sync": "2026-06-24T14:30:00Z",
    "created_at": "2026-06-24T14:30:00Z"
  }
]
```

### POST /integrations/hikvision/cameras

Add a Hikvision camera to a property.

**Request:**

```json
{
  "hikvision_id": "hikvision_abc123",
  "name": "Front Door",
  "location": "Main Entrance",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "ip_address": "192.168.1.100"
}
```

**Response:** 201 Created

```json
{
  "id": "camera-uuid",
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "hikvision_id": "hikvision_abc123",
  "name": "Front Door",
  "online": true,
  "recording": true,
  "last_sync": "2026-06-24T14:30:00Z",
  "created_at": "2026-06-24T14:30:00Z"
}
```

### POST /integrations/hikvision/cameras/{camera_id}/record/start

Start recording on camera.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Front Door recording started",
  "camera_id": "camera-uuid",
  "recording": true
}
```

### POST /integrations/hikvision/cameras/{camera_id}/record/stop

Stop recording on camera.

**Response:** 200 OK

```json
{
  "status": "success",
  "message": "Front Door recording stopped",
  "camera_id": "camera-uuid",
  "recording": false
}
```

## Files

| File                      | Purpose                                |
| ------------------------- | -------------------------------------- |
| `adapter.py`              | HikvisionAdapter implementing protocol |
| `domain.py`               | HikvisionCamera Pydantic model         |
| `models.py`               | HikvisionCameraModel SQLAlchemy ORM    |
| `schemas.py`              | Request/response DTOs                  |
| `routes.py`               | FastAPI router with endpoints          |
| `tests/test_hikvision.py` | Test cases for all flows               |
| `README.md`               | This file                              |

## Types

### HikvisionCamera (domain.py)

```python
class HikvisionCamera(BaseModel):
    id: UUID
    property_id: UUID
    integration_id: UUID
    hikvision_id: str           # Unique to Hikvision
    name: str
    location: str
    model: str
    ip_address: str
    online: bool
    recording: bool
    resolution: str             # "1920x1080", etc
    frame_rate: int
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
```

## Testing

Run tests:

```bash
cd backend && python -m pytest src/integrations/hikvision/
```

Test coverage includes:

- Adding camera
- Start/stop recording
- List cameras with filtering
- Online status tracking
- Retrieve live feed info

## Related

- Integrations overview: `backend/src/integrations/README.md`
- Property API: `backend/src/property/api/routes.py`
- Device domain: `backend/src/property/domain/README.md`
