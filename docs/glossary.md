Glossary for Alphacon AI System
This glossary defines the key terms used across the AlphaCon AI system. It explains what
each concept means and how it relates to others within the data model and user
experience.
Its purpose is intended to ensure that everyone, including engineers, product teams, and
stakeholders, uses the same definitions when designing, building, and discussing the
system. Standardising terminology, it reduces confusion, improves communication, and
helps maintain consistency across the platform.
Core Hierarchy
Identity & Access
Property
Stay & Tenant
Devices
Agent / AI
Integration
Automation
Audit & Events
Conclusion
Core Hierarchy
This section defines the foundational structure of the AlphaCon AI system. It outlines how
entities are organised from the highest level (Organisation) down to the individual occupant
(Tenant). Understanding this hierarchy is essential
b
ecause all data relationships, permissions,
and system
b
ehaviours are
built on top of it.
Term Definition
Organisation It represents the top-
level
b
illing and legal entity(the
"company account"). Owns portfolios, users,
integrations, and data b
oundaries.
PortfolioA grouping of properties under a team or operational
unit (e.g., city, brand, region). Where day-to
-day work
happens. A Portfolio always b
elongs to exactly one
Organisation.
PropertyA physical location (home, apartment, building) where
devices and stays exist. Belongs to exactly one
Portfolio, but a portfolio can have many properties.
StayA time
-b
e.g., Airb
tenancy).
ound occupancy of a property (under 30 days,
b
n
) or long-term (30+ days, e.g., a 12-
month
TenantA person occupying a Property during a Stay. The
system treats Tenants as real users with their own login
during their Stay.
Identity & Access
This section defines how users are identified and what they are allowed to do within the system.
It covers authentication, roles, and permission controls that determine access across
organisations, portfolios, and properties.
Term Definition
UserAuthenticated identity in the system. Can
b
e staff
(operators, managers) or a Tenant occupying a Property
during a Stay.
Tenant-
only
User
b
Mem
ership Property
Assignment
A restricted User created via the Stay flow. Authenticates
via magic link (short-term Stay) or full account (long-
term Stay). Limited to actions within their active Stay.
The record that links a User to an Organisation or
Portfolio, carrying their role within it. The mem
b
ership
and the role live on the same record; you can't have one
without the other. Example: "Sarah is a mem
b
er of the
Manchester Portfolio as a Portfolio Admin" is one record:
PortfolioMem
ership { user: Sarah,
b
portfolio
:
Man
chester, role:
PORTFOLIO_
ADMIN } .
The record that links a User to a single specific Property
when their access is property-specific rather than
Portfolio
-wide. Same idea as a Mem
b
ership, just
narrower in scope. Example: Mike the cleaner has
PropertyAssignment { user:
Mike, property
:
Cottage 1, role: C
ONTRA
CTOR, time_window:
weekdays 9–2 pm, expires: 31 Dec
}. He
cannot see the other 11 properties in the Portfolio, only
Cottage 1, during his shift.
Org Role Role at organisation level (OWNER, ORG_
ADMIN,
BILLING).
Portfolio Role Role within a Portfolio: PORTFOLIO_
ADMIN ,
PORTFOLIO_MANAGER , PORTFOLIO_MEMBER ,
PORTFOLIO_VIEWER . Applies to every Property in the
Portfolio.
Property Role Role scoped to a single Property: PROPERTY_MANAGER ,
OPERATOR , C
ONTRA
CTOR , PROPERTY_VIEWER . Used
for narrow exceptions like cleaners or individual property
owners.
Tenant Role Role held by a Tenant during their Stay:
PRIMARY_TENANT (the lead guest) or C
(other named occupants on the same
b
O_TENANT
ooking).
Scope
Constraint
Optional limits attached to an assignment: which
capab
ilities (e.g., locks only), which device categories,
which time windows (e.g., weekdays 9–2 pm). Used for
Contractors and Tenants.
InvitationA pending invite sent by email. Holds the role and
assignments the invitee will receive on acceptance. Has
an expiry and can
b
e revoked.
SessionAn active login. Carries the User's currently active
Organisation and authentication method.
Property
This section defines what a Property is and what it contains. A Property is the physical container
that devices may sit inside, but they are not necessarily owned by it.
Term Definition
PropertyA physical
building or unit with an address. Belongs to exactly
one Portfolio. Contains Rooms, hosts Stays, and has Devices
physically located within it (some owned by the Property
itself, some owned by current Tenants).
RoomA logical grouping within a Property (e.g., "Master Bedroom").
Devices may b
e associated with a Room for organisational
purposes. Optional.
Property
Address
The physical location of a Property, line 1, line 2, city,
postcode, country, plus geographic coordinates.
Property
Type
The intended use of a Property: SHORT_TERM_RENTAL ,
LONG_TERM_RENTAL , OWNER_O
CCUPIED, MIXED_USE, or
C
OMMERCIAL . Influences default automations and
b
on
oarding flows.
Stay & Tenant
This section defines the occupancy layer of the system, how b
people staying in a Property interact with AlphaCon AI.
ookings are represented and how
Term Definition
StayA
b
ooking against a Property, with a check-
in and
check-
out time. Multiple Stays happen at the same
Property over time; each is a separate record.
Stay Status The lifecycle of a Stay: UPC
OMING ,
CTIVE ,
C
OMPLETED, C
AN
CELLED, or NO_SHOW .
Stay Duration The length of a Stay (
check_out_at −
check_in_at ). Drives b
ehaviour throughout the
system. Short-term = under 30 days, long-term = 30
days or more. This is computed from duration, not
stored as a separate field, so it always reflects the
current b
ooking.
Booking Source Where a Stay originated: AIRBNB , VRBO,
BOOKING_
C
OM , DIRECT , or MANUAL .
A
Stay
Preferences
Optional values attached to a Stay (preferred
temperature, arrival lighting, quiet hours) that the
automation engine reads while the Stay is active.
TenantA person occupying the Property during a Stay. Has a
Tenant role, time
-scoped device access, and access
automatically revokes at check-
out.
Primary Tenant Co
-Tenant Tenant Device
Access
Magic Link The lead guest on a b
level access during the Stay.
ooking. Has the
broadest tenant-
Other named occupants on the same
b
ooking. Same
default access as the Primary Tenant; the host can
choose to restrict.
What a Tenant can do with Devices during their Stay.
Differs depending on who owns the Device:
For Property-
owned Devices (the host's kit), Tenants
get scoped access. Short-term Tenants typically
thermostat + lights, long-term Tenants broader. The
host configures the limits.
For Tenant-
owned or Stay-
owned Devices (the
Tenant's own kit), Tenants have full control; they own
them. The host cannot control these without explicit
permission from the Tenant.
The default authentication method for short-term
Tenants. A one
-tap login link is sent in the
b
ooking
confirmation email; no account creation is required.
Devices
This section defines Devices as first-class entities in AlphaCon AI. Devices are not sub
ordinate
to Properties; they have their own identity, their own owner, and their own physical location, and
these can change independently. This decoupling supports real
-world scenarios where Tenants
bring their own smart-
home equipment into rented properties.
Term Definition
DeviceA controllab
le or o
bservab
le physical IoT unit (e.g.,
lock, thermostat, light, sensor). A first-class entity with
its own identity. Has an owner (Property or Tenant)
and a current physical location (a Property).
Device
Ownership
Device Owner Property-
owned
Device
Tenant-
owned
Device
Who a Device
b
elongs to. Determines who can fully
control it, who sees its state and history, and what
happens to it over time. One of: PROPERTY (host's
installed kit, persists across Stays) or TENANT (a
Tenant's personal kit, follows the Tenant).
The specific entity that owns a Device
—
either a
Property record (for PROPERTY ownership) or a User
record (for TENANT ownership). Stored as a
polymorphic reference: owner_type + owner_id .
A Device installed by the host or property manager.
Belongs to the Property itself. Persists across Stays,
every Tenant who occupies the Property may interact
with it (within scope). Examples: built-
in thermostats,
smart locks, leak sensors, and hallway lights installed
by the host.
A Device that a Tenant has personally added to
AlphaCon. Belongs to the Tenant. Follows the Tenant if
they move to a different AlphaCon Property; leaves
with them when they move out. The host can see that
the Device exists, but cannot read its state or send
commands to it without explicit Tenant permission.
Examples: a long-term Tenant's personal Hue
bul
bs, a
guest's portab
le smart air purifier.
Current Location Where the Device is physically situated right now,
typically a Property. Separate from ownership. A
Tenant-
owned Device's current location is the
Property they're currently staying at; if the Tenant
moves to a new AlphaCon Property, the current
location updates while ownership stays with the
Tenant. A Device can also have no current location
(e.g., a Tenant-
owned Device
b
etween rentals).
Device Category The kind of device (e.g., THERMOSTAT , LO
CK,
LIGHT , SENSOR_LE
AK ). Determines which
Capab
ilities it offers. Independent of ownership.
Capab
ilityA specific feature or function a Device supports (e.g.,
ON_OFF , BRIGHTNESS , TEMPERATURE_SET ,
LO
CK). All values are normalised across vendors
(Celsius for temperature, 0–100 for brightness).
Device StateA snapshot of a Device's current readings or status at
a specific point in time, stored as capab
ility-keyed
values. Visib
ility of state is governed by ownership and
access scope.
CommandAn instruction sent to a Device to act (e.g., lock the
door, set the temperature). Has a lifecycle: pending →
executing → succeeded or failed. Authorisation is
checked against the issuer's relationship to the
Device's owner.
Command Result The outcome of executing a Command, including
success/failure, vendor confirmation, and the resulting
Device State.
Agent / AI
This section defines how the AI agent operates within the system. It covers how users interact
with the agent, how decisions are made, and how actions are executed through tools and
memory.
Term Definition
Conversati
on
An interaction session
b
etween a User and the AI agent.
Scoped to a Property and (when applicab
le) a Stay.
MessageA single turn within a Conversation: user input, agent
response, or tool result.
Persona The agent's b
(for staff), C
ON
HOME_
ASSISTANT conversation start.
ehaviour mode for a Conversation: CIERGE (for short-term Tenants), or
(for long-term Tenants). Set at
OPERATOR
ToolAn executab
le function the AI can call (e.g., set thermostat,
list devices, read state). Tools are filtered by the User's
permissions b
efore
b
eing shown to the agent.
Tool CallA single invocation of a Tool
by the agent during a
Conversation.
Agent RunA single execution cycle of the AI model, one prompt sent to
Claude and the response received. One user turn can
produce multiple Agent Runs (tool
-use loops, escalation).
Model Tier The class of model used for an Agent Run: HAIKU (fast,
cheap, simple reads), SONNET (default for most queries), or
OPUS (complex multi-step reasoning).
Memory
Item
Stored contextual knowledge is used to improve responses.
Includes conversation history, device events, user notes,
and automation outcomes. Scoped to an Organisation,
Property, and (when applicab
le) Stay.
Prompt
Cache
A performance optimisation that reuses stab
le parts of the
prompt (system prompt, tool catalogue, tenant context)
across requests to reduce LLM cost and latency.
Integration
This section defines how AlphaCon AI connects to external systems and device vendors. It
standardises communication with third-party platforms and ensures that external devices can
b
e discovered, monitored, and controlled reliab
ly.
Term Definition
IntegrationA connection
b
etween an Organisation/Portfolio and a
third-party vendor (e.g., Nest, Hue, August). Holds
credentials and is the source of truth for which Devices are
linked.
Integration
Ownership
Who does an integration
b
elong to? One of: PROPERTY (or
Portfolio
-scoped the host's vendor account, used to
populate Property-
owned Devices) or TENANT (a Tenant's
personal vendor account, used to populate Tenant-
owned
Devices). Mirrors Device Ownership.
A vendor connection was added by the host. The Devices it
discovers are Property-
owned. Persists across Stays.
Property-
owned
Integration
Tenant-
owned
Integration
A vendor connection added by a Tenant during their Stay.
The Devices it discovers are Tenant-
owned. Disconnects
with the Tenant when their Stay ends or they remove it.
Vendor
Adapter
A standardised interface for interacting with different
vendors. Each vendor (Nest, Eco
b
ee, Hue, etc.) has its own
Adapter implementation hidden
b
ehind a common contract.
We
b
hookAn event sent by a vendor to notify the system of changes
(e.g., a temperature change, a door unlocked). Verified by
signature
b
efore
b
eing processed.
Credentials OAuth tokens used to authenticate with external vendors.
Encrypted at rest, refreshed automatically b
efore expiry.
Rate Limit
Budget
The remaining num
b
er of API requests AlphaCon can make
to a vendor within a given time window. Used to prevent
quota exhaustion.
Automation
This section defines how tasks are automated within the system. Automations allow the platform
to respond to events and execute actions without manual intervention, improving efficiency and
consistency.
Term Definition
Automati
on
A rule
-based workflow made up of a Trigger, optional
Conditions, and one or more Actions. Scoped to a Property.
Trigger The event that starts an Automation: SCHEDULE (cron
-
based), EVENT (device state change), or STAY (e.g., "2
hours b
efore check-
in").
ConditionA rule that must b
e satisfied b
"if no one is home" or "b
efore Actions are executed (e.g.,
etween 10 pm and 7 am").
Action The operation performed when Conditions are met (e.g., set
thermostat, lock doors, send notification).
Automati
on Run
A record of a single Automation execution, including which
Trigger fired it, the Conditions evaluated, and the outcome of
each Action.
Audit & Events
This section defines how system activity is tracked and how internal events are communicated.
It ensures traceab
ility, accountab
ility, and supports system orchestration through event-driven
design.
Term Definition
Audit EventAn immutab
authority.
le record of an action performed in the system.
Includes who acted, what they did, when, and under what
Domain
Event
An internal system event used to trigger downstream
processes and workflows (e.g., DeviceStateChanged ,
StayA
ctivated ). Drives the event bus.
Event Bus The internal mechanism that distributes Domain Events to
subscrib
ers (audit logger, automation engine, we
bsocket
pusher).
ActorRef Identifies who performed an action: a User, Tenant, the
System, the Agent, an Automation, or a Vendor We
b
When the Agent acts, the ActorRef captures b
hook.
oth the agent
and the User on whose
b
ehalf it acted.
Conclusion
After reading this section, if any concepts still feel unclear, the next section provides a clearer
view of how everything connects. It explains “Who’s who” in the AlphaCon AI system and how
different entities relate to each other.