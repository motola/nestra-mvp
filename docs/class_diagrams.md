# AlphaCon AI — Phase 1 MVP Class Diagrams (v1.1)

*Canonical class diagram pack. Supersedes v1.0 and all earlier versions. Reflects the decoupled Device model: Devices and Integrations are first-class aggregate roots with polymorphic ownership (Property or Tenant).*

*Renders as Mermaid in any modern markdown viewer (GitHub, GitLab, Notion, IntelliJ, VS Code with Mermaid plugin, Obsidian).*

---

## What's new in v1.1

The single foundational change: **Devices and Integrations are no longer subordinate to Properties.** Both are first-class aggregate roots with polymorphic ownership.

| Concept | v1.0 | v1.1 |
|---|---|---|
| Device parent | Always a Property (`property_id` FK) | Owner is either a Property *or* a Tenant (polymorphic) |
| Device location | Implicit (= Property) | Separate `current_property_id` field, can be null |
| Integration parent | Always a Portfolio | Owner is either a Property/Portfolio *or* a Tenant |
| Bounded context name | "Property & Occupancy" | "Property, Devices & Occupancy" |
| Tenant-owned smart home | Not modelled | First-class — Tenants bring their own Hue/Nest accounts and devices |

This is the right architecture from the start, not a phased upgrade. v1.0 is dead.

---

## Design Conventions

**UML stereotypes:**

| Stereotype | Meaning |
|---|---|
| `<<aggregate root>>` | Entry point to a consistency boundary. External code only references aggregate roots, never their internals. |
| `<<entity>>` | Has identity, lives inside an aggregate. |
| `<<value object>>` | Immutable, no identity, equality by value. |
| `<<interface>>` | Contract that implementations must realize. |
| `<<adapter>>` | Concrete implementation of a vendor adapter interface. |
| `<<enumeration>>` | Closed set of constants. |
| `<<service>>` | Stateless behaviour that doesn't naturally belong to any entity. |
| `<<abstract>>` | Cannot be instantiated directly. |
| `<<polymorphic>>` | Owner is one of multiple aggregate root types — distinguished by an `owner_type` enum. |

**Relationship lines:**

| Symbol | Meaning |
|---|---|
| `*--` | Composition (lifecycle-bound; child cannot exist without parent) |
| `o--` | Aggregation (parent has child, but child has independent lifecycle) |
| `-->` | Directed association (knows about) |
| `..>` | Dependency (uses transiently) |
| `..\|>` | Realization (implements interface) |
| `<\|--` | Inheritance |

**Multiplicity:** standard UML — `1`, `*` (many), `0..1` (optional), `1..*` (one or more).

---

## The conceptual hierarchy

The four-level hierarchy from v1.0 is unchanged. What changes is how Devices and Integrations attach to it.

```mermaid
flowchart TB
    classDef billing fill:#1a365d,stroke:#2d3748,color:#fff,stroke-width:2px
    classDef ops fill:#2c5282,stroke:#2d3748,color:#fff,stroke-width:2px
    classDef physical fill:#2f855a,stroke:#2d3748,color:#fff,stroke-width:2px
    classDef occupancy fill:#744210,stroke:#2d3748,color:#fff,stroke-width:2px
    classDef firstclass fill:#9b2c2c,stroke:#2d3748,color:#fff,stroke-width:2px

    Org["<b>Level 1: Organization</b><br/><i>billing &amp; legal entity</i>"]:::billing
    Port["<b>Level 2: Portfolio</b><br/><i>team + their properties</i>"]:::ops
    Prop["<b>Level 3: Property</b><br/><i>physical building</i>"]:::physical
    Tenant["<b>Level 4: Stay / Tenant</b><br/><i>temporary occupant</i>"]:::occupancy
    Device["<b>Devices</b><br/><i>first-class</i><br/>owned by Property OR Tenant"]:::firstclass
    Integration["<b>Integrations</b><br/><i>first-class</i><br/>owned by Property OR Tenant"]:::firstclass

    Org --> Port
    Port --> Prop
    Prop --> Tenant
    
    Prop -. owns .-> Device
    Tenant -. owns .-> Device
    Prop -. owns .-> Integration
    Tenant -. owns .-> Integration
    Device -. located at .-> Prop
```

Key insight: **Devices and Integrations sit *alongside* the hierarchy, not inside it.** Their owner is one node from the hierarchy (either a Property or a Tenant), but they're not children of any one node.

---

## Bounded Context Map

Six bounded contexts. The Property & Occupancy context from v1.0 is renamed to **Property, Devices & Occupancy** to reflect Device's promotion to first-class status.

```mermaid
flowchart TB
    classDef core fill:#1a365d,stroke:#2d3748,color:#fff,stroke-width:2px
    classDef supporting fill:#2c5282,stroke:#2d3748,color:#fff,stroke-width:1px
    classDef generic fill:#4a5568,stroke:#2d3748,color:#fff,stroke-width:1px

    Identity["<b>Identity &amp; Access</b><br/><i>generic subdomain</i><br/>Organization · Portfolio · User · Memberships · Invitations · Sessions"]:::generic
    PDO["<b>Property, Devices &amp; Occupancy</b><br/><i>core domain</i><br/>Property · Room · Device · DeviceState · Command · Stay · Tenant"]:::core
    Integration["<b>Integration</b><br/><i>core domain</i><br/>Adapters · Credentials · Webhooks · Rate limits<br/>(polymorphically owned)"]:::core
    Agent["<b>Agent / AI</b><br/><i>core domain</i><br/>Conversations · Tools · Routing · Memory<br/>(ownership-aware visibility)"]:::core
    Automation["<b>Automation</b><br/><i>supporting subdomain</i><br/>Triggers · Conditions · Actions · Runs<br/>(polymorphically owned)"]:::supporting
    Audit["<b>Audit &amp; Events</b><br/><i>generic subdomain</i><br/>AuditEvent · DomainEvent bus<br/>(captures ownership at action time)"]:::generic

    Identity --> PDO
    Identity --> Integration
    Identity --> Agent
    Identity --> Automation

    Integration --> PDO
    PDO --> Agent
    PDO --> Automation
    Integration --> Automation
    Agent --> Automation

    PDO -.publishes.-> Audit
    Integration -.publishes.-> Audit
    Agent -.publishes.-> Audit
    Automation -.publishes.-> Audit
    Identity -.publishes.-> Audit
```

---

## 1. Identity & Access

Unchanged from v1.0. Same four-level access hierarchy with Memberships and Property Assignments. (Reproduced here for completeness — if you're already familiar, skip to context 2.)

```mermaid
classDiagram
    direction TB

    class Organization {
        <<aggregate root>>
        +id: UUID
        +name: str
        +slug: str
        +legal_name: str
        +status: OrgStatus
        +subscription_tier: SubscriptionTier
        +created_at: datetime
        +list_portfolios() Portfolio[]
        +list_org_members() OrgMembership[]
        +list_pending_invitations() Invitation[]
    }

    class Portfolio {
        <<aggregate root>>
        +id: UUID
        +organization_id: UUID
        +name: str
        +description: str
        +is_default: bool
        +created_at: datetime
        +archived_at: datetime
        +list_properties() Property[]
        +list_members() PortfolioMembership[]
        +property_count() int
    }

    class User {
        <<aggregate root>>
        +id: UUID
        +email: str
        +full_name: str
        +password_hash: str
        +auth_method: AuthMethod
        +last_login_at: datetime
        +is_active: bool
        +is_tenant_only: bool
        +org_memberships() OrgMembership[]
        +portfolio_memberships() PortfolioMembership[]
        +property_assignments() PropertyAssignment[]
        +tenant_records() Tenant[]
        +owned_devices() Device[]
        +owned_integrations() Integration[]
        +can(action: str, resource) bool
    }

    class OrgMembership {
        <<entity>>
        +user_id: UUID
        +organization_id: UUID
        +org_role: OrgRole
        +joined_at: datetime
        +invited_by: UUID
    }

    class PortfolioMembership {
        <<entity>>
        +id: UUID
        +user_id: UUID
        +portfolio_id: UUID
        +organization_id: UUID
        +portfolio_role: PortfolioRole
        +joined_at: datetime
    }

    class PropertyAssignment {
        <<entity>>
        +id: UUID
        +user_id: UUID
        +property_id: UUID
        +portfolio_id: UUID
        +organization_id: UUID
        +property_role: PropertyRole
        +scope_constraints: ScopeConstraint
        +assigned_at: datetime
        +expires_at: datetime
        +is_active() bool
    }

    class Invitation {
        <<aggregate root>>
        +id: UUID
        +organization_id: UUID
        +email: str
        +invitation_type: InvitationType
        +pending_assignments: PendingAssignment[]
        +token_hash: str
        +expires_at: datetime
        +status() InvitationStatus
        +accept(user: User) void
    }

    class Session {
        <<entity>>
        +id: UUID
        +user_id: UUID
        +active_organization_id: UUID
        +auth_method: AuthMethod
        +issued_at: datetime
        +expires_at: datetime
    }

    class ScopeConstraint {
        <<value object>>
        +allowed_capabilities: Set~Capability~
        +device_categories: Set~DeviceCategory~
        +time_window: TimeWindow
    }

    class OrgRole {
        <<enumeration>>
        OWNER
        ORG_ADMIN
        BILLING
    }

    class PortfolioRole {
        <<enumeration>>
        PORTFOLIO_ADMIN
        PORTFOLIO_MANAGER
        PORTFOLIO_MEMBER
        PORTFOLIO_VIEWER
    }

    class PropertyRole {
        <<enumeration>>
        PROPERTY_MANAGER
        OPERATOR
        CONTRACTOR
        PROPERTY_VIEWER
    }

    class AuthMethod {
        <<enumeration>>
        PASSWORD
        MAGIC_LINK
        GOOGLE_SSO
        APPLE_SSO
    }

    Organization "1" o-- "*" Portfolio
    Organization "1" o-- "*" OrgMembership
    Organization "1" o-- "*" Invitation
    Portfolio "1" o-- "*" PortfolioMembership
    User "1" o-- "*" OrgMembership
    User "1" o-- "*" PortfolioMembership
    User "1" o-- "*" PropertyAssignment
    User "1" *-- "*" Session
    PropertyAssignment "1" *-- "0..1" ScopeConstraint
    OrgMembership --> OrgRole
    PortfolioMembership --> PortfolioRole
    PropertyAssignment --> PropertyRole
    Session --> AuthMethod
    User --> AuthMethod

    note for User "User now also tracks owned_devices()<br/>and owned_integrations() — Tenants<br/>can own first-class Devices and<br/>Integrations directly."
```

---

## 2. Property, Devices & Occupancy

Core domain. Renamed from v1.0's "Property & Occupancy" because Device is now too significant to be hidden in a sub-bullet of the name. Three sub-models live here: **Property** (physical container), **Device** (first-class, polymorphically owned), and **Stay/Tenant** (occupancy).

### 2a. Property and Rooms

Property is now a clean entity — it has Rooms, hosts Stays, and is *physically referenced by* Devices via `current_property_id`. It does not own Devices in the parent-child sense.

```mermaid
classDiagram
    direction TB

    class Property {
        <<aggregate root>>
        +id: UUID
        +portfolio_id: UUID
        +organization_id: UUID
        +name: str
        +address: Address
        +timezone: str
        +property_type: PropertyType
        +created_at: datetime
        +archived_at: datetime
        +list_rooms() Room[]
        +list_devices_present() Device[]
        +list_property_owned_devices() Device[]
        +current_stay() Stay
        +upcoming_stays() Stay[]
        +archive() void
        +rename(name: str) void
    }

    class Address {
        <<value object>>
        +line1: str
        +line2: str
        +city: str
        +postcode: str
        +country: str
        +latitude: float
        +longitude: float
        +to_string() str
    }

    class Room {
        <<entity>>
        +id: UUID
        +property_id: UUID
        +name: str
        +room_type: RoomType
        +rename(name: str) void
    }

    class PropertyType {
        <<enumeration>>
        SHORT_TERM_RENTAL
        LONG_TERM_RENTAL
        OWNER_OCCUPIED
        MIXED_USE
        COMMERCIAL
    }

    class RoomType {
        <<enumeration>>
        BEDROOM
        BATHROOM
        KITCHEN
        LIVING
        ENTRY
        GARAGE
        OUTDOOR
        OTHER
    }

    Property "1" *-- "1" Address
    Property "1" *-- "*" Room
    Property --> PropertyType
    Room --> RoomType

    note for Property "list_devices_present() returns ALL Devices<br/>currently located here (Property-owned<br/>AND Tenant-owned). list_property_owned_devices()<br/>returns only Devices owned by this Property."
```

### 2b. Device (first-class, polymorphic owner)

This is the heart of the v1.1 change. Device is now an aggregate root with two distinct relationships: an owner (polymorphic) and a current location (the Property it physically sits in).

```mermaid
classDiagram
    direction TB

    class Device {
        <<aggregate root>>
        <<polymorphic>>
        +id: UUID
        +organization_id: UUID
        +owner_type: DeviceOwnerType
        +owner_id: UUID
        +current_property_id: UUID
        +room_id: UUID
        +integration_id: UUID
        +category: DeviceCategory
        +capabilities: Set~Capability~
        +display_name: str
        +manufacturer: str
        +model: str
        +vendor_id: str
        +vendor_device_id: str
        +reachable: bool
        +last_seen_at: datetime
        +created_at: datetime
        +current_state() DeviceState
        +supports(capability: Capability) bool
        +is_property_owned() bool
        +is_tenant_owned() bool
        +owner() Property | User
        +relocate_to(property_id: UUID) void
        +transfer_ownership(new_owner_type, new_owner_id) void
        +rename(name: str) void
        +mark_unreachable() void
    }

    class DeviceState {
        <<value object>>
        +device_id: UUID
        +captured_at: datetime
        +values: Map~Capability, Value~
        +source: StateSource
        +get(capability: Capability) Value
        +is_stale(max_age_s: int) bool
    }

    class Command {
        <<aggregate root>>
        +id: UUID
        +device_id: UUID
        +device_owner_snapshot: DeviceOwnerRef
        +current_property_id_snapshot: UUID
        +organization_id: UUID
        +capability: Capability
        +payload: Map
        +issued_by: ActorRef
        +issued_at: datetime
        +status: CommandStatus
        +validate() bool
        +mark_executing() void
        +complete(result: CommandResult) void
    }

    class CommandResult {
        <<value object>>
        +command_id: UUID
        +status: CommandStatus
        +executed_at: datetime
        +vendor_request_id: str
        +error_code: str
        +error_message: str
        +state_after: DeviceState
    }

    class DeviceOwnerRef {
        <<value object>>
        +owner_type: DeviceOwnerType
        +owner_id: UUID
        +captured_at: datetime
    }

    class DeviceOwnerType {
        <<enumeration>>
        PROPERTY
        TENANT
    }

    class DeviceCategory {
        <<enumeration>>
        THERMOSTAT
        LOCK
        LIGHT
        SWITCH
        PLUG
        SENSOR_CONTACT
        SENSOR_MOTION
        SENSOR_LEAK
        ENERGY_METER
        HUB
    }

    class Capability {
        <<enumeration>>
        ON_OFF
        BRIGHTNESS
        COLOR
        LOCK
        TEMPERATURE_READ
        TEMPERATURE_SET
        HVAC_MODE
        HUMIDITY
        BATTERY
        CONTACT
        MOTION
        LEAK
        ENERGY_USAGE
    }

    class CommandStatus {
        <<enumeration>>
        PENDING
        EXECUTING
        SUCCEEDED
        FAILED
        TIMED_OUT
        CANCELLED
    }

    class StateSource {
        <<enumeration>>
        WEBHOOK
        POLL
        COMMAND_RESPONSE
        CACHED
    }

    Device "1" --> "*" DeviceState : captures
    Device "1" --> "*" Command : receives
    Command "1" --> "0..1" CommandResult : produces
    Command "1" *-- "1" DeviceOwnerRef : snapshots owner
    Device --> DeviceOwnerType
    Device --> DeviceCategory
    Device --> Capability
    Command --> Capability
    Command --> CommandStatus
    DeviceState --> StateSource

    note for Device "owner_type + owner_id is a polymorphic<br/>reference — points to either a Property<br/>or a User (Tenant). current_property_id<br/>is independent: the physical location<br/>right now, can be NULL (device in transit)."
    note for Command "device_owner_snapshot captures who<br/>owned the device AT THE TIME the command<br/>was issued. Even if ownership changes<br/>later, audit history stays accurate."
```

**Key decisions:**

- **Polymorphic owner**: `owner_type` discriminates between PROPERTY and TENANT. The `owner_id` field holds either a Property's UUID or a User's UUID. The `owner()` method resolves to the right entity.
- **Current location is separate from ownership.** A Tenant-owned Device has `owner_id = the Tenant's User ID` permanently, but `current_property_id` updates if the Tenant moves to a different AlphaCon Property.
- **Current location can be NULL.** Tenant-owned Devices between rentals have no current Property — that's a valid state, not an error.
- **Commands snapshot ownership at issue time.** Even if a Device's ownership changes later (rare but possible — a Tenant gifts their Device to the Property when they leave), audit history shows who owned it when each command was issued.
- **Org ID is on Device.** This is critical for RLS — even Tenant-owned Devices carry the Organization ID of the Property they're currently located in, so isolation works cleanly. When a Tenant moves between Organizations (e.g., from one property management company to another that also uses AlphaCon), the org_id updates with the location.

### 2c. Stay and Tenant

Stays and Tenants are largely unchanged from v1.0, except Tenants now explicitly can own Devices and Integrations (visible via `User.owned_devices()` and `User.owned_integrations()` from the Identity context).

```mermaid
classDiagram
    direction TB

    class Stay {
        <<aggregate root>>
        +id: UUID
        +property_id: UUID
        +portfolio_id: UUID
        +organization_id: UUID
        +check_in_at: datetime
        +check_out_at: datetime
        +status: StayStatus
        +source: BookingSource
        +source_reference: str
        +preferences: StayPreferences
        +created_at: datetime
        +list_tenants() Tenant[]
        +duration_days() int
        +is_short_term() bool
        +is_active(now: datetime) bool
        +cancel(reason: str) void
        +extend(new_checkout: datetime) void
        +complete() void
    }

    class Tenant {
        <<entity>>
        +id: UUID
        +stay_id: UUID
        +property_id: UUID
        +user_id: UUID
        +tenant_role: TenantRole
        +full_name: str
        +email: str
        +phone: str
        +access_pin: EncryptedStr
        +invited_at: datetime
        +accepted_at: datetime
        +revoke_access() void
    }

    class StayPreferences {
        <<value object>>
        +preferred_temperature_c: float
        +preferred_arrival_temperature_c: float
        +arrival_lighting: LightingPreset
        +quiet_hours: TimeWindow
    }

    class StayStatus {
        <<enumeration>>
        UPCOMING
        ACTIVE
        COMPLETED
        CANCELLED
        NO_SHOW
    }

    class BookingSource {
        <<enumeration>>
        AIRBNB
        VRBO
        BOOKING_COM
        DIRECT
        MANUAL
    }

    class TenantRole {
        <<enumeration>>
        PRIMARY_TENANT
        CO_TENANT
    }

    Stay "1" *-- "1..*" Tenant
    Stay "1" *-- "0..1" StayPreferences
    Stay --> StayStatus
    Stay --> BookingSource
    Tenant --> TenantRole

    note for Tenant "Tenant.user_id references a User (Identity context).<br/>That User can own first-class Devices and<br/>Integrations independently of any Property —<br/>they follow the User across Stays."
```

### 2d. The full Property/Device/Stay relationship

Putting it all together — how Property, Device, Stay, and Tenant relate in v1.1:

```mermaid
classDiagram
    direction LR

    class Property {
        <<aggregate root>>
        id
        portfolio_id
    }

    class Device {
        <<aggregate root>>
        id
        owner_type: PROPERTY|TENANT
        owner_id
        current_property_id
    }

    class Stay {
        <<aggregate root>>
        id
        property_id
    }

    class Tenant {
        <<entity>>
        id
        user_id
    }

    class User {
        <<aggregate root>>
        id
    }

    Property "1" o-- "*" Device : owns when owner_type=PROPERTY
    User "1" o-- "*" Device : owns when owner_type=TENANT
    Property "0..1" <-- "*" Device : currently located at (current_property_id)
    Property "1" o-- "*" Stay
    Stay "1" *-- "*" Tenant
    Tenant "1" --> "1" User : is

    note for Device "Two relationships to Property:<br/>1. Ownership (when owner_type=PROPERTY)<br/>2. Physical location (current_property_id)<br/>These are independent."
```

---

## 3. Integration

Same polymorphic-owner pattern as Device. An Integration is a vendor connection that's owned by either a Property/Portfolio (host's vendor account) or a Tenant (their personal vendor account).

```mermaid
classDiagram
    direction TB

    class Integration {
        <<aggregate root>>
        <<polymorphic>>
        +id: UUID
        +organization_id: UUID
        +owner_type: IntegrationOwnerType
        +owner_id: UUID
        +vendor_id: str
        +display_name: str
        +status: IntegrationStatus
        +scopes: str[]
        +connected_at: datetime
        +last_sync_at: datetime
        +last_error_at: datetime
        +sync_devices() Device[]
        +disconnect() void
        +mark_token_expired() void
        +reauthorize_url() str
        +is_property_owned() bool
        +is_tenant_owned() bool
        +owner() Portfolio | User
    }

    class Credentials {
        <<value object>>
        +integration_id: UUID
        +access_token: EncryptedStr
        +refresh_token: EncryptedStr
        +expires_at: datetime
        +token_type: str
        +scope: str
        +is_expired() bool
        +needs_refresh(buffer_s: int) bool
    }

    class VendorAdapter {
        <<interface>>
        +vendor_id: str
        +supported_categories: Set~DeviceCategory~
        +build_oauth_url(owner_ref, redirect_uri) str
        +exchange_code(code: str) Credentials
        +refresh(creds: Credentials) Credentials
        +list_devices(creds: Credentials) Device[]
        +get_state(creds, vendor_device_id) DeviceState
        +execute(creds, vendor_device_id, cmd) CommandResult
        +subscribe_events(creds, callback_url) WebhookSubscription
        +health_check() bool
    }

    class NestAdapter {
        <<adapter>>
    }

    class EcobeeAdapter {
        <<adapter>>
    }

    class HueAdapter {
        <<adapter>>
    }

    class AugustAdapter {
        <<adapter>>
    }

    class ShellyAdapter {
        <<adapter>>
    }

    class SmartThingsAdapter {
        <<adapter>>
    }

    class AdapterRegistry {
        <<service>>
        +register(adapter: VendorAdapter) void
        +get(vendor_id: str) VendorAdapter
        +all() VendorAdapter[]
        +supports(category) VendorAdapter[]
    }

    class WebhookSubscription {
        <<entity>>
        +id: UUID
        +integration_id: UUID
        +callback_url: str
        +secret: EncryptedStr
        +vendor_subscription_id: str
        +created_at: datetime
        +verify_signature(payload, sig) bool
        +rotate_secret() void
    }

    class WebhookEvent {
        <<value object>>
        +id: UUID
        +subscription_id: UUID
        +received_at: datetime
        +headers: Map
        +payload: JSON
        +processed_at: datetime
        +to_domain_event() DomainEvent
    }

    class RateLimitBudget {
        <<entity>>
        +integration_id: UUID
        +window_start: datetime
        +window_seconds: int
        +requests_used: int
        +requests_limit: int
        +remaining() int
        +consume(n: int) bool
        +reset() void
    }

    class IntegrationOwnerType {
        <<enumeration>>
        PROPERTY
        TENANT
    }

    class IntegrationStatus {
        <<enumeration>>
        PENDING_OAUTH
        ACTIVE
        TOKEN_EXPIRED
        REVOKED
        ERROR
        DISCONNECTED
    }

    Integration "1" *-- "1" Credentials
    Integration "1" *-- "*" WebhookSubscription
    Integration "1" --> "0..1" RateLimitBudget
    WebhookSubscription "1" --> "*" WebhookEvent
    NestAdapter ..|> VendorAdapter
    EcobeeAdapter ..|> VendorAdapter
    HueAdapter ..|> VendorAdapter
    AugustAdapter ..|> VendorAdapter
    ShellyAdapter ..|> VendorAdapter
    SmartThingsAdapter ..|> VendorAdapter
    AdapterRegistry o-- VendorAdapter
    Integration ..> AdapterRegistry
    Integration --> IntegrationOwnerType
    Integration --> IntegrationStatus

    note for Integration "owner_type + owner_id is polymorphic.<br/>For PROPERTY: owner_id refers to a Portfolio<br/>(or specific Property — see RateLimitBudget).<br/>For TENANT: owner_id refers to a User."
    note for RateLimitBudget "Now per-Integration, not per-vendor-per-org.<br/>A Tenant's personal Nest budget is separate<br/>from the host's Nest budget — same vendor,<br/>two separate quotas."
```

**Key decisions:**

- `Integration.owner_type` mirrors `Device.owner_type`. Same polymorphic pattern.
- For PROPERTY-owned Integrations, the owner is a Portfolio (because Integrations are typically scoped to a team/region, not a single building). A Portfolio's Nest account discovers devices that get assigned to specific Properties within the Portfolio.
- For TENANT-owned Integrations, the owner is a User. When the Tenant disconnects or their Stay ends, the Integration and all its Devices are removed.
- `RateLimitBudget` is now per-Integration, not per-vendor-per-org. A Tenant's personal Nest API quota is tracked separately from the host's, even though they're both calling Nest.
- Same `VendorAdapter` interface serves both ownership types. The Adapter doesn't know or care who owns the Integration — it just authenticates with whatever credentials it's given.

### Adapter error hierarchy (unchanged from v1.0)

```mermaid
classDiagram
    direction TB

    class AdapterError {
        <<abstract>>
        +retriable: bool
        +user_visible: bool
        +message: str
        +vendor_id: str
    }

    class VendorDown {
        +retriable: True
    }

    class RateLimited {
        +retriable: True
        +retry_after_s: int
    }

    class AuthExpired {
        +retriable: True
        +user_visible: True
        +reauth_url: str
    }

    class DeviceOffline {
        +retriable: False
        +user_visible: True
    }

    class CommandRejected {
        +retriable: False
        +user_visible: True
        +reason: str
    }

    class ProtocolError {
        +retriable: False
        +alert_engineering: True
    }

    class TimeoutError {
        +retriable: True
        +elapsed_ms: int
    }

    AdapterError <|-- VendorDown
    AdapterError <|-- RateLimited
    AdapterError <|-- AuthExpired
    AdapterError <|-- DeviceOffline
    AdapterError <|-- CommandRejected
    AdapterError <|-- ProtocolError
    AdapterError <|-- TimeoutError
```

---

## 4. Agent / AI

Updated for ownership-aware Device visibility. The agent's tool catalog is filtered by what Devices the actor can see, not just by their role permissions.

```mermaid
classDiagram
    direction TB

    class Conversation {
        <<aggregate root>>
        +id: UUID
        +organization_id: UUID
        +user_id: UUID
        +property_id: UUID
        +stay_id: UUID
        +actor_type: ActorType
        +persona: AgentPersona
        +device_visibility_scope: DeviceVisibilityScope
        +title: str
        +created_at: datetime
        +last_message_at: datetime
        +archived_at: datetime
        +append(message: Message) void
        +recent_turns(n: int) Message[]
        +archive() void
    }

    class Message {
        <<entity>>
        +id: UUID
        +conversation_id: UUID
        +role: MessageRole
        +content: str
        +tool_calls: ToolCall[]
        +created_at: datetime
        +token_count: int
    }

    class AgentRun {
        <<entity>>
        +id: UUID
        +conversation_id: UUID
        +produced_message_id: UUID
        +model: str
        +tier: ModelTier
        +input_tokens: int
        +cached_input_tokens: int
        +cache_creation_tokens: int
        +output_tokens: int
        +cost_pence: float
        +latency_ms: int
        +escalated_from: ModelTier
        +tools_used: str[]
        +started_at: datetime
        +completed_at: datetime
    }

    class Tool {
        <<entity>>
        +name: str
        +description: str
        +parameters_schema: JSONSchema
        +mutates_state: bool
        +requires_confirmation: bool
        +scope: ToolScope
        +execute(args, ctx) ToolResult
    }

    class ToolCall {
        <<value object>>
        +id: UUID
        +message_id: UUID
        +tool_name: str
        +arguments: JSON
        +invoked_at: datetime
    }

    class ToolResult {
        <<value object>>
        +tool_call_id: UUID
        +success: bool
        +output: JSON
        +error: str
        +completed_at: datetime
    }

    class DeviceVisibilityScope {
        <<value object>>
        +include_property_owned: bool
        +include_own_tenant_owned: bool
        +include_others_tenant_owned: bool
        +property_owned_capabilities: Set~Capability~
        +visible_devices_for(actor, property) Device[]
    }

    class ModelRouter {
        <<service>>
        +classify(message, history_len, n_tools, persona) ModelTier
        +should_escalate(response) bool
        +pick_model(tier: ModelTier) str
    }

    class ToolRegistry {
        <<service>>
        +register(tool: Tool) void
        +tools_for(actor, property, stay, visibility) Tool[]
        +get(name: str) Tool
    }

    class PromptCache {
        <<service>>
        +get_system_prompt(persona) str
        +get_tool_catalog(actor_context) str
        +build_cached_blocks(persona, ctx) Block[]
        +invalidate(scope_key) void
    }

    class MemoryItem {
        <<entity>>
        +id: UUID
        +organization_id: UUID
        +property_id: UUID
        +stay_id: UUID
        +scope: MemoryScope
        +content: str
        +embedding: float[]
        +source: MemorySource
        +created_at: datetime
        +similarity_to(query_emb) float
    }

    class MessageRole {
        <<enumeration>>
        SYSTEM
        USER
        ASSISTANT
        TOOL
    }

    class ModelTier {
        <<enumeration>>
        HAIKU
        SONNET
        OPUS
    }

    class AgentPersona {
        <<enumeration>>
        OPERATOR
        CONCIERGE
        HOME_ASSISTANT
    }

    class ToolScope {
        <<enumeration>>
        READ_ONLY
        DEVICE_CONTROL
        AUTOMATION_MANAGEMENT
        ADMIN
    }

    class MemorySource {
        <<enumeration>>
        CONVERSATION
        DEVICE_EVENT
        USER_NOTE
        AUTOMATION_RUN
    }

    class MemoryScope {
        <<enumeration>>
        PROPERTY
        STAY
        TENANT_PRIVATE
    }

    Conversation "1" *-- "*" Message
    Conversation "1" *-- "1" DeviceVisibilityScope
    Message "1" --> "*" ToolCall
    ToolCall "1" --> "1" ToolResult
    Message "1" --> "0..1" AgentRun
    AgentRun --> ModelTier
    Message --> MessageRole
    ToolCall ..> Tool
    ToolRegistry o-- Tool
    Conversation ..> MemoryItem
    MemoryItem --> MemorySource
    MemoryItem --> MemoryScope
    AgentRun ..> ModelRouter
    AgentRun ..> PromptCache
    Conversation --> AgentPersona
    Tool --> ToolScope

    note for DeviceVisibilityScope "Computed at conversation start.<br/>For an Operator: all Property-owned<br/>Devices in their scope, no Tenant-owned.<br/>For a Tenant: their own Devices fully,<br/>Property-owned Devices within Stay scope,<br/>other Tenants' Devices invisible."
    note for MemoryItem "MemoryScope determines who can read it.<br/>TENANT_PRIVATE memory (their own usage<br/>patterns, preferences) never surfaces to<br/>the host. PROPERTY memory persists across<br/>Stays. STAY memory wipes at checkout."
```

**Key decisions:**

- **`DeviceVisibilityScope` is a new value object** computed at conversation start. It encodes "what Devices does this actor see, and what can they do with each." Persists for the conversation — every tool call inside the conversation respects the same scope.
- **The agent never even sees Devices outside its scope.** A Tenant talking to the agent doesn't get Devices owned by other Tenants in their tool catalog. Claude doesn't know they exist. This is enforcement by *invisibility*, not by *refusal*.
- **`MemoryScope` separates Tenant-private memory from Property memory.** A long-term Tenant's usage patterns ("David likes the bedroom at 18°C, lights off by 11pm") are scoped TENANT_PRIVATE — never available to the host's queries about the Property.

---

## 5. Automation

Updated to support polymorphic ownership: an Automation is owned by either a Property (host's automations, persist across Stays) or a Tenant (Tenant's automations, scoped to their Stay).

```mermaid
classDiagram
    direction TB

    class Automation {
        <<aggregate root>>
        <<polymorphic>>
        +id: UUID
        +organization_id: UUID
        +owner_type: AutomationOwnerType
        +owner_id: UUID
        +scoped_property_id: UUID
        +name: str
        +description: str
        +enabled: bool
        +created_at: datetime
        +last_run_at: datetime
        +trigger: Trigger
        +conditions: Condition[]
        +actions: Action[]
        +enable() void
        +disable() void
        +run(context: RunContext) AutomationRun
        +is_property_owned() bool
        +is_tenant_owned() bool
    }

    class Trigger {
        <<abstract>>
        +id: UUID
        +automation_id: UUID
        +matches(event: DomainEvent) bool
    }

    class ScheduleTrigger {
        +cron_expression: str
        +timezone: str
        +next_run_at() datetime
    }

    class EventTrigger {
        +event_type: str
        +device_id: UUID
        +capability: Capability
    }

    class StayTrigger {
        +stay_event: StayEventType
        +offset_minutes: int
    }

    class Condition {
        <<abstract>>
        +id: UUID
        +automation_id: UUID
        +order: int
        +evaluate(context: RunContext) bool
    }

    class StateCondition {
        +device_id: UUID
        +capability: Capability
        +operator: ComparisonOp
        +value: Any
    }

    class TimeCondition {
        +between_start: time
        +between_end: time
        +days_of_week: int[]
    }

    class Action {
        <<abstract>>
        +id: UUID
        +automation_id: UUID
        +order: int
        +execute(context: RunContext) ActionResult
        +validate_authority(automation: Automation) bool
    }

    class DeviceAction {
        +device_id: UUID
        +capability: Capability
        +payload: Map
    }

    class NotificationAction {
        +channel: NotificationChannel
        +recipient: str
        +template: str
    }

    class AutomationRun {
        <<entity>>
        +id: UUID
        +automation_id: UUID
        +triggered_at: datetime
        +completed_at: datetime
        +status: RunStatus
        +trigger_event: JSON
        +action_results: ActionResult[]
        +error: str
    }

    class ActionResult {
        <<value object>>
        +action_id: UUID
        +success: bool
        +executed_at: datetime
        +output: JSON
        +error: str
    }

    class RunContext {
        <<value object>>
        +organization_id: UUID
        +property_id: UUID
        +stay_id: UUID
        +trigger_event: DomainEvent
        +device_states: Map
        +current_time: datetime
    }

    class AutomationOwnerType {
        <<enumeration>>
        PROPERTY
        TENANT
    }

    class StayEventType {
        <<enumeration>>
        BEFORE_CHECK_IN
        AT_CHECK_IN
        DURING_STAY
        AT_CHECK_OUT
        AFTER_CHECK_OUT
    }

    class ComparisonOp {
        <<enumeration>>
        EQ
        NEQ
        GT
        GTE
        LT
        LTE
        IN
    }

    class NotificationChannel {
        <<enumeration>>
        EMAIL
        SMS
        PUSH
        SLACK
    }

    class RunStatus {
        <<enumeration>>
        TRIGGERED
        EVALUATING
        EXECUTING
        SUCCEEDED
        FAILED
        SKIPPED_CONDITIONS
        UNAUTHORIZED
    }

    Automation "1" *-- "1" Trigger
    Automation "1" *-- "*" Condition
    Automation "1" *-- "*" Action
    Trigger <|-- ScheduleTrigger
    Trigger <|-- EventTrigger
    Trigger <|-- StayTrigger
    Condition <|-- StateCondition
    Condition <|-- TimeCondition
    Action <|-- DeviceAction
    Action <|-- NotificationAction
    Automation "1" --> "*" AutomationRun
    AutomationRun "1" *-- "*" ActionResult
    Automation --> AutomationOwnerType
    StayTrigger --> StayEventType
    StateCondition --> ComparisonOp
    NotificationAction --> NotificationChannel
    AutomationRun --> RunStatus

    note for Automation "owner_type=PROPERTY: persists across<br/>Stays, configured by Portfolio operators.<br/>owner_type=TENANT: scoped to a Stay,<br/>auto-deleted when Stay completes."
    note for Action "validate_authority() checks the Automation's<br/>owner has rights over the target Device.<br/>A Tenant Automation cannot act on another<br/>Tenant's Device or on a Property-owned<br/>Device outside its Stay scope."
```

**Key decisions:**

- Tenant-owned Automations were deferred in v1.0 — in v1.1 the schema supports them, MVP can ship with creation restricted to Portfolio operators if you want to keep scope tight, and unlock Tenant-created automations in 1.5 by lifting that restriction. No schema migration needed.
- `Action.validate_authority()` is the runtime check that an automation's owner has rights over the target Device. Tenant automations can only target their own Devices and Property-owned Devices within their Stay scope.

---

## 6. Audit & Domain Events

Updated to capture Device ownership at action time, plus new ownership-related domain events.

```mermaid
classDiagram
    direction TB

    class AuditEvent {
        <<entity>>
        +id: UUID
        +occurred_at: datetime
        +organization_id: UUID
        +portfolio_id: UUID
        +property_id: UUID
        +actor: ActorRef
        +action: str
        +resource_type: str
        +resource_id: str
        +resource_owner_snapshot: ResourceOwnerRef
        +metadata: JSON
        +ip_address: str
        +user_agent: str
    }

    class ActorRef {
        <<value object>>
        +type: ActorType
        +id: str
        +display_name: str
        +on_behalf_of: ActorRef
        +acting_role: str
    }

    class ResourceOwnerRef {
        <<value object>>
        +owner_type: str
        +owner_id: str
        +owner_display_name: str
    }

    class DomainEvent {
        <<abstract>>
        +id: UUID
        +organization_id: UUID
        +occurred_at: datetime
        +event_type: str
        +payload: JSON
    }

    class DeviceStateChanged {
        +device_id: UUID
        +device_owner: ResourceOwnerRef
        +current_property_id: UUID
        +previous_state: DeviceState
        +new_state: DeviceState
    }

    class DeviceOwnershipTransferred {
        +device_id: UUID
        +previous_owner: ResourceOwnerRef
        +new_owner: ResourceOwnerRef
        +reason: str
    }

    class DeviceRelocated {
        +device_id: UUID
        +previous_property_id: UUID
        +new_property_id: UUID
    }

    class CommandIssued {
        +command_id: UUID
        +device_id: UUID
        +device_owner: ResourceOwnerRef
    }

    class CommandCompleted {
        +command_id: UUID
        +result: CommandResult
    }

    class StayCreated {
        +stay_id: UUID
        +property_id: UUID
    }

    class StayActivated {
        +stay_id: UUID
    }

    class StayCompleted {
        +stay_id: UUID
    }

    class IntegrationConnected {
        +integration_id: UUID
        +integration_owner: ResourceOwnerRef
        +vendor_id: str
        +device_count: int
    }

    class IntegrationDisconnected {
        +integration_id: UUID
        +reason: str
    }

    class AutomationTriggered {
        +automation_id: UUID
        +automation_owner: ResourceOwnerRef
        +trigger_event_id: UUID
    }

    class AgentInteractionCompleted {
        +conversation_id: UUID
        +run_id: UUID
        +cost_pence: float
    }

    class EventBus {
        <<service>>
        +publish(event: DomainEvent) void
        +subscribe(event_type, handler) Subscription
    }

    class ActorType {
        <<enumeration>>
        USER
        TENANT
        SYSTEM
        AGENT
        AUTOMATION
        VENDOR_WEBHOOK
    }

    DomainEvent <|-- DeviceStateChanged
    DomainEvent <|-- DeviceOwnershipTransferred
    DomainEvent <|-- DeviceRelocated
    DomainEvent <|-- CommandIssued
    DomainEvent <|-- CommandCompleted
    DomainEvent <|-- StayCreated
    DomainEvent <|-- StayActivated
    DomainEvent <|-- StayCompleted
    DomainEvent <|-- IntegrationConnected
    DomainEvent <|-- IntegrationDisconnected
    DomainEvent <|-- AutomationTriggered
    DomainEvent <|-- AgentInteractionCompleted
    AuditEvent "1" *-- "1" ActorRef
    AuditEvent "1" *-- "0..1" ResourceOwnerRef
    ActorRef --> ActorType
    AuditEvent ..> DomainEvent
    EventBus ..> DomainEvent

    note for AuditEvent "resource_owner_snapshot captures who<br/>owned the resource (Device/Integration/<br/>Automation) at action time. Distinguishes<br/>'David turned off his own light' from<br/>'David turned off the host's light'."
    note for DeviceOwnershipTransferred "Fires when a Device's ownership changes —<br/>e.g., a Tenant gifts their device to the<br/>Property when they leave. Drives downstream<br/>cleanup (memory rescoping, automation review)."
```

**Key decisions:**

- **`ResourceOwnerRef` snapshots** are critical for audit accuracy. Even if a Device's ownership transfers later, audit history shows what was true at the time of each action.
- **Three new domain events**: `DeviceOwnershipTransferred` (gifts/sales), `DeviceRelocated` (Tenant moves between properties), and the existing events now carry owner context.
- **The audit log can answer questions the v1.0 model couldn't**: "show me all actions David took on Property-owned Devices vs his own Devices" is a clean filter.

---

## 7. Cross-Context Aggregate Roots (Bird's Eye)

The minimum set of references that cross context boundaries.

```mermaid
classDiagram
    direction LR

    class Organization
    class Portfolio
    class User
    class Property
    class Device
    class Integration
    class Stay
    class Tenant
    class Conversation
    class Automation
    class AuditEvent

    Organization "1" --> "*" Portfolio
    Organization "1" --> "*" User : through Membership
    Portfolio "1" --> "*" Property
    Portfolio "1" --> "*" Integration : when owner_type=PROPERTY
    Property "1" --> "*" Device : when owner_type=PROPERTY (ownership)
    Property "0..1" <-- "*" Device : current_property_id (location)
    Property "1" --> "*" Stay
    Stay "1" --> "*" Tenant
    Tenant "1" --> "1" User : auth identity
    User "1" --> "*" Device : when owner_type=TENANT
    User "1" --> "*" Integration : when owner_type=TENANT
    Integration "1" --> "*" Device : populates
    Property "1" --> "*" Conversation : scoped to
    Property "1" --> "*" Automation : when owner_type=PROPERTY
    User "1" --> "*" Automation : when owner_type=TENANT
    Conversation ..> Device : via tools (visibility-filtered)
    Automation ..> Device : commands (authority-checked)
    Stay "1" --> "*" Conversation : during

    note for Device "Two relationships shown:<br/>1. Ownership (Property OR User)<br/>2. Physical location (Property)"
    note for Organization "Every aggregate root carries organization_id.<br/>RLS enforces isolation at the database level."
```

**The rule:** code in context A may hold `aggregate_b_id: UUID` referencing an aggregate in context B, but never directly imports B's internals. Context boundaries are crossed via repository lookups or domain events.

---

## RLS Implications of the Decoupled Model

Decoupling Devices and Integrations from strict Property hierarchy adds nuance to row-level security. Here's how it works cleanly:

```sql
-- Devices: visible to anyone who can see EITHER
--   (a) the Device's owner-Property (PROPERTY-owned), OR
--   (b) the Device's owner-User (TENANT-owned), if that User is the current session

CREATE POLICY device_isolation ON devices
USING (
    organization_id = current_setting('app.current_organization_id')::uuid
    AND (
        -- Property-owned: visible if user has access to the owner Property
        (owner_type = 'PROPERTY' AND owner_id IN (
            SELECT property_id FROM accessible_properties_for_current_user()
        ))
        OR
        -- Tenant-owned: visible to the owning User
        (owner_type = 'TENANT' AND owner_id = current_setting('app.current_user_id')::uuid)
        OR
        -- Tenant-owned: visible to host operators of the Property where it's located
        (owner_type = 'TENANT' AND current_property_id IN (
            SELECT property_id FROM accessible_properties_for_current_user()
        ) AND current_setting('app.current_user_role') IN ('PORTFOLIO_ADMIN', 'PORTFOLIO_MANAGER', 'PROPERTY_MANAGER'))
    )
);
```

The third clause is the privacy-aware host visibility: the host can see *that* a Tenant-owned Device exists in their Property, but separate column-level policies hide state and command history from them. The agent's `DeviceVisibilityScope` enforces stricter rules at the application layer for tool selection.

---

## What's Explicitly Out of Phase 1

| Deferred to | Concern |
|---|---|
| Phase 1.5 | Tenant-created Automations (schema supports it; restrict in MVP) |
| Phase 1.5 | `TENANT_VISITOR` role (let-a-friend-in-for-dinner case) |
| Phase 1.5 | Booking-platform integrations (Airbnb/Vrbo/Booking.com → Stay creation) |
| Phase 1.5 | Long-term Stay data portability (GDPR right-to-portability) |
| Phase 1.5 | Tenant-to-Property device gifting flow (when Tenant leaves device behind) |
| Phase 2 | `Camera` device category and video/snapshot capabilities |
| Phase 2 | `LocalHubAdapter` for direct Zigbee/Z-Wave/Matter |
| Phase 2 | Long-term `MemoryItem` with hybrid retrieval |
| Phase 2 | Energy meter analytics, occupancy inference |
| Phase 2 | Sub-Stays (long-term tenant inviting house-sitter) |
| Phase 2 | Cross-Organization device portability (Tenant moving between AlphaCon-using companies) |
| Phase 3 | Proprietary `AlphaConHubDevice` and direct hardware control |
| Later | MFA, hardware security keys |
| Later | Custom roles / RBAC editor |
| Later | SCIM / SSO provisioning for enterprise |
| Later | Outbound webhooks (third parties subscribing to our events) |

---

## Implementation Notes

**Suggested module layout (updated for v1.1):**

```
alphacon/
  identity/                 # Context 1
    organizations.py
    portfolios.py
    users.py
    memberships.py
    invitations.py
    sessions.py
    permissions.py
  properties_devices_occupancy/   # Context 2 — renamed for clarity
    properties.py
    rooms.py
    devices/
      canonical.py            # Device aggregate root
      ownership.py            # DeviceOwnerType, polymorphic resolution
      states.py
      commands.py
    occupancy/
      stays.py
      tenants.py
  integrations/             # Context 3
    base.py                 # VendorAdapter Protocol
    registry.py
    ownership.py            # IntegrationOwnerType, polymorphic resolution
    nest.py
    ecobee.py
    hue.py
    august.py
    shelly.py
    smartthings.py
    webhooks.py
    errors.py
  agent/                    # Context 4
    conversations.py
    visibility.py           # DeviceVisibilityScope
    tools.py
    router.py
    prompt_cache.py
    personas.py
    memory.py
  automations/              # Context 5
    automations.py          # Polymorphic owner
    triggers/
    conditions/
    actions/
      authority.py          # validate_authority logic
    runner.py
  audit/                    # Context 6
    events.py
    bus.py
    log.py
  shared/
    types.py                # ActorRef, ResourceOwnerRef, common value objects
    db.py                   # org_scope context manager (RLS)
    polymorphic.py          # generic polymorphic owner helpers
```

**Polymorphic owner helper:** define a single utility that resolves `(owner_type, owner_id)` into an entity. Used by Device, Integration, and Automation. One implementation, three users.

```python
# shared/polymorphic.py
from typing import Protocol, TypeVar, Generic

OwnerEnum = TypeVar("OwnerEnum")

class PolymorphicOwner(Generic[OwnerEnum]):
    """Resolves polymorphic owner references into actual entities."""

    def resolve(self, owner_type: OwnerEnum, owner_id: UUID) -> AggregateRoot:
        match owner_type:
            case "PROPERTY": return PropertyRepo.get(owner_id)
            case "TENANT":   return UserRepo.get(owner_id)
            case "PORTFOLIO": return PortfolioRepo.get(owner_id)
            case _: raise UnknownOwnerType(owner_type)
```

---

## Versioning

- **v1.0** — initial four-level hierarchy, Devices subordinate to Properties.
- **v1.1** *(this document)* — Devices and Integrations promoted to first-class with polymorphic ownership.
- v1.2 will incorporate any changes from the upcoming Postgres ER diagram exercise.
- v1.3 will incorporate any changes from sequence diagram modelling.

This is the canonical reference. v1.0 is dead; ignore it.