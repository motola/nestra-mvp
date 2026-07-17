# Identity Repository

Data access layer for users and organizations.

## Pattern

Repository pattern abstracts database queries, allowing services to work with domain models.

## Key Methods (Planned)

```python
class UserRepository:
    async def create(user: User) -> User
    async def get_by_id(user_id: UUID) -> User | None
    async def get_by_email(email: str) -> User | None
    async def list_by_organization(org_id: UUID) -> list[User]
    async def update(user: User) -> User
    async def delete(user_id: UUID) -> bool

class OrganizationRepository:
    async def create(org: Organization) -> Organization
    async def get_by_id(org_id: UUID) -> Organization | None
    async def list_by_user(user_id: UUID) -> list[Organization]
    async def update(org: Organization) -> Organization
    async def delete(org_id: UUID) -> bool
```

## Models

SQLAlchemy ORM models:

- `UserModel` mapping to `users` table
- `OrganizationModel` mapping to `organizations` table

**Constraints:**

- Email is unique (no duplicate logins)
- Foreign key: user.organization_id → organization.id

## Related

- Identity module: `backend/src/identity/README.md`
- Domain models: `backend/src/identity/domain/README.md`
- Services (use repository): `backend/src/identity/services/README.md`
