# Property Repository

Data access layer for properties and devices — abstracts database queries.

## Pattern

Repository pattern encapsulates database access logic, allowing services to work with domain models without knowing about SQL/ORM.

## Models

Contains SQLAlchemy ORM models for database tables:

- Device model mapping to `devices` table
- Relationships to `organizations`, `properties`, `integrations`

## Key Methods (Planned)

```python
class DeviceRepository:
    async def create(device: Device) -> Device
    async def get_by_id(device_id: UUID) -> Device | None
    async def list_by_property(property_id: UUID) -> list[Device]
    async def list_by_organization(org_id: UUID) -> list[Device]
    async def list_by_type(device_type: DeviceType) -> list[Device]
    async def update(device: Device) -> Device
    async def delete(device_id: UUID) -> bool
```

## Organization Isolation

All queries automatically filter by `organization_id`:

```python
async def list_by_property(self, property_id: UUID, org_id: UUID) -> list[Device]:
    # Only returns devices belonging to org_id
    return await self.db.query(DeviceModel).filter(
        DeviceModel.property_id == property_id,
        DeviceModel.organization_id == org_id,
    ).all()
```

This ensures multi-tenant isolation at the database layer.

## Related

- Property module: `backend/src/property/README.md`
- Domain models: `backend/src/property/domain/README.md`
- Persistence (ORM models): `backend/src/property/persistence/README.md`
- Services (use repository): `backend/src/property/services/README.md`
