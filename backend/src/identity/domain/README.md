# Identity Domain

Core domain models for users and organizations.

## Models

### User

Individual user account.

```python
class User(BaseModel):
    id: UUID
    email: str                 # Unique email
    display_name: str
    organization_id: UUID      # Multi-tenant: belongs to org
    role: UserRole            # admin, editor, viewer
    created_at: datetime
    updated_at: datetime
```

### Organization

Tenant container for users and resources.

```python
class Organization(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
```

### UserRole (StrEnum)

Authorization levels:

```python
class UserRole(StrEnum):
    ADMIN = "admin"         # Full access: users, config, settings
    EDITOR = "editor"       # Modify devices, automations, properties
    VIEWER = "viewer"       # Read-only: view devices, properties
```

## Design Notes

### Multi-Tenant Isolation

Each user belongs to exactly one organization. All resources (devices, properties, etc) also have `organization_id`.

This ensures:

- User can only see their organization's resources
- Data is isolated at the DB query level
- RLS (Row-Level Security) policies enforce isolation

### Email as Unique Identifier

Email is globally unique and used for login. Prevents duplicate accounts.

### Roles are Simple

Three roles cover most use cases:

- **Admin** — User/org management, all operations
- **Editor** — Control devices, create automations, manage properties
- **Viewer** — Read-only, cannot modify anything

Extend by adding more roles as needed (e.g., `GUEST`, `MAINTENANCE`).

## Related

- Identity module: `backend/src/identity/README.md`
- Authorization (enforce roles): `backend/src/identity/services/README.md`
- Multi-tenant filtering: `backend/src/property/repository/README.md`
