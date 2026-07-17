# Missing Implementation - NEM-28

## Servers Status

- ✅ **Backend** (port 8000) - Running
- ✅ **Intelligence** (port 8001) - Running

## What's Working

- Backend health endpoint: `/health` ✅
- Intelligence health endpoint: `/health` ✅
- Backend routes structure (property, identity, integrations)
- Intelligence route structure (stub endpoints)

## What's Missing / TODO

### Backend Integration

1. **Database Connection**
   - PostgreSQL async connection setup
   - Database migrations (Alembic)
   - Table creation for all models

2. **Integration Implementations**
   - [ ] Shelly adapter - needs HTTP client setup for RPC calls
   - [ ] Govee adapter - needs cloud API integration
   - [ ] LIFX adapter - needs cloud API integration
   - [ ] Matter adapter - needs Matter controller connection
   - **Existing (stubs)**:
     - August Smart Locks (needs completion)
     - Bluetooth (needs completion)
     - Ecobee (needs completion)
     - Hikvision (needs completion)
     - TP-Link (needs completion)

3. **Property/Device Management**
   - Device repository implementation
   - Device sync pipeline
   - Device state tracking
   - Device control execution

4. **Identity/Auth**
   - User registration/login endpoints
   - Session management
   - Role-based access control
   - JWT token generation

### Intelligence Service

1. **Database Integration**
   - Connect to backend PostgreSQL
   - Create conversation and message tables
   - Conversation persistence

2. **Claude API Integration**
   - Implement ClaudeIntegration service fully
   - Tool execution engine
   - Conversation streaming

3. **Device Control Flow**
   - Connect to backend device repository
   - Tool execution against real devices
   - Device state feedback

4. **API Endpoints**
   - `/conversations` - POST (create)
   - `/conversations/{id}` - GET (retrieve)
   - `/conversations/{id}/messages` - POST (chat with streaming)

### Shared Infrastructure

1. **Clients**
   - ✅ HttpClient created
   - ✅ ClaudeClient created
   - Need: Integration with services

2. **Database**
   - Need: Shared configuration between backend and intelligence

### Cross-Service Communication

- [ ] Backend → Intelligence HTTP calls for AI tasks
- [ ] Intelligence → Backend HTTP calls for device queries
- [ ] Async job queuing (optional, for device sync)

## Quick Start for Development

### Backend

```bash
cd backend
python run_tests.py  # Verify tests pass
python -m uvicorn src.main:app --port 8000
```

### Intelligence

```bash
cd intelligence
python -m uvicorn src.main:app --port 8001
```

### Test Servers

```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
```

## Priority Roadmap

### Phase 1: Core Infrastructure (Critical)

1. Database setup and migrations
2. User authentication (login/register)
3. Basic property and device CRUD

### Phase 2: Device Integration (High)

1. Complete at least 1-2 integration adapters (Shelly, August)
2. Device sync pipeline
3. Device state queries

### Phase 3: AI Intelligence (High)

1. Connect Intelligence service to backend DB
2. Implement conversation persistence
3. Implement Claude tool use for device control

### Phase 4: Full Integration (Medium)

1. Complete remaining adapters
2. Complex device scenarios (multi-device commands)
3. Automation rules engine

## Environment Setup

### Backend (.env)

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/alphacon_dev
REDIS_URL=redis://localhost:6379
SECRET_KEY=test-secret-key-for-local-development
DEBUG=True
ANTHROPIC_API_KEY=sk-...
```

### Intelligence (.env)

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/alphacon_dev
ANTHROPIC_API_KEY=sk-...
DEBUG=True
```

## Architecture Notes

- **Unified Device Schema**: All devices (August, Shelly, Govee, etc.) map to single `Device` model
- **Vendor-Specific State**: Device-specific data stored in `raw_state` dict, not separate tables
- **IntegrationAdapter Protocol**: Each vendor implements common interface for fetch_devices, fetch_state, execute
- **Service Isolation**: Backend and Intelligence are separate services communicating via HTTP
- **Shared Clients**: Both services use HttpClient and ClaudeClient from shared/ directory
