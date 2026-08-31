# Backend API Endpoint Alignment

## Current Implementation Status

### ✅ Fully Implemented Endpoints

#### Portfolio & Property Management

- `GET /portfolios` - List portfolios (query param: organization_id)
- `POST /portfolios` - Create portfolio
- `GET /portfolios/{portfolio_id}` - Get portfolio
- `PUT /portfolios/{portfolio_id}` - Update portfolio (query param: organization_id)
- `GET /portfolios/{portfolio_id}/properties` - List properties (query param: organization_id)
- `POST /portfolios/{portfolio_id}/properties` - Create property
- `PUT /portfolios/{portfolio_id}/properties/{property_id}` - Update property (query param: organization_id)
- `GET /properties/{property_id}/devices` - List all devices for property

#### Device Management

- `POST /devices/bluetooth/create` - Create Bluetooth device
- `POST /devices/shelly/create` - Create Shelly device
- `POST /devices/{device_id}/control` - Control device
- `GET /devices/{device_id}` - Get device details (with placement, integrations, capabilities)

#### Capabilities

- `GET /capabilities/` - List all capabilities (paginated)
- `GET /capabilities/{capability_id}` - Get capability details
- `POST /devices/{device_id}/discover` - Auto-discover device capabilities
- `GET /devices/{device_id}/capabilities` - Get device capabilities

#### Commands & Automation

- `POST /commands/devices/{device_id}/commands` - Execute command
- `GET /commands/devices/{device_id}/commands` - Command history (paginated)
- `GET /commands/{command_id}` - Command details
- `GET /commands/{command_id}/executions` - Execution history
- `PUT /commands/{command_id}/cancel` - Cancel pending command

#### Occupancy Management

- `GET /occupancy/tenants/` - List tenants
- `POST /occupancy/tenants/` - Create tenant
- `GET /occupancy/tenants/{tenant_id}` - Get tenant
- `PUT /occupancy/tenants/{tenant_id}` - Update tenant
- `DELETE /occupancy/tenants/{tenant_id}` - Delete tenant (soft)

- `GET /occupancy/rooms/` - List rooms
- `POST /occupancy/rooms/` - Create room
- `GET /occupancy/rooms/{room_id}` - Get room
- `PUT /occupancy/rooms/{room_id}` - Update room

- `GET /occupancy/stays/` - List stays (paginated)
- `POST /occupancy/stays/` - Create stay
- `GET /occupancy/stays/{stay_id}` - Get stay
- `PUT /occupancy/stays/{stay_id}` - Update stay

#### Access Control

- `POST /access/devices/{device_id}/access-grants` - Grant device access
- `GET /access/devices/{device_id}/access-grants` - List grants (paginated)
- `PUT /access/access-grants/{grant_id}` - Update grant
- `DELETE /access/access-grants/{grant_id}` - Revoke access

- `POST /access/devices/{device_id}/share-links` - Create share link
- `GET /access/devices/{device_id}/share-links` - List share links (paginated)
- `POST /access/share-links/{token}/claim` - Claim share link
- `DELETE /access/share-links/{token}` - Revoke share link

#### Audit Logging

- `GET /access/audit/events` - Query audit log (paginated, filterable)
- `GET /access/audit/events/{event_id}` - Event details
- `GET /access/audit/summary` - Organization statistics
- `GET /access/audit/events/device/{device_id}` - Device activity
- `GET /access/audit/events/user/{user_id}` - User activity

### 📱 Frontend API Client Status

**Implemented**: `frontend/src/lib/api/portfolios.ts`

- Portfolio and Property CRUD operations
- Aligned with backend endpoints ✅

**Missing**: Device management API client

- Should wrap device creation, control, history
- Location: `frontend/src/lib/api/devices.ts` (needs creation)

**Missing**: Occupancy API client

- Should wrap tenant, room, stay operations
- Location: `frontend/src/lib/api/occupancy.ts` (needs creation)

**Missing**: Access control API client

- Should wrap grants and share links
- Location: `frontend/src/lib/api/access.ts` (needs creation)

## Database Tables

### Fully Created (Phases 1-5)

- organizations
- users
- portfolios
- properties
- devices, device_placements, device_integrations, device_capabilities, device_current_states, device_state_events
- integrations
- capabilities
- commands, command_execution_logs
- tenants, rooms, stays, stay_rooms, stay_tenants, stay_preferences
- device_access_grants
- magic_link_tokens
- audit_events

## Next Steps: Phase 6

**Frontend Integration**: Create API clients and UI components for:

1. Device management dashboard
2. Command execution UI
3. Occupancy tracking
4. Access control UI
5. Audit log viewer

**Backend Enhancements**:

1. Add batch operations (bulk create/update)
2. Add filtering/search on list endpoints
3. Add export functionality for audit logs
4. Add webhook support for event notifications

## Authentication Notes

All endpoints require `Authorization: Bearer {token}` header
Organization scope validation via `org_scope` context manager
