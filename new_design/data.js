/* Alphacon AI — MVP fixtures. Reflects v1.1 polymorphic ownership. */

const PORTFOLIOS = [
  { id: "pf_north", name: "Northern Portfolio", region: "North England + Scotland", manager: "Theo Adeyemi" },
  { id: "pf_south", name: "Southern Portfolio", region: "London + South West",       manager: "Jules Marais" },
];

const PROPERTIES = [
  { id: "p_maple",      portfolio: "pf_north", name: "Maple Court",      address: "leeds_ls1",       type: "MIXED_USE",         tz: "Europe/London", units: 6,  occupied: 4, alerts: 1, status: "warn",  devices: 38, integrations: 4 },
  { id: "p_ash",        portfolio: "pf_south", name: "Ash Cottage",      address: "oxford_ox4",      type: "SHORT_TERM_RENTAL", tz: "Europe/London", units: 1,  occupied: 1, alerts: 0, status: "ok",    devices: 14, integrations: 3 },
  { id: "p_northbrook", portfolio: "pf_north", name: "Northbrook Mill",  address: "manchester_m1",   type: "LONG_TERM_RENTAL",  tz: "Europe/London", units: 7,  occupied: 5, alerts: 2, status: "alert", devices: 42, integrations: 4 },
  { id: "p_seacombe",   portfolio: "pf_north", name: "Seacombe Wharf",   address: "liverpool_l3",    type: "LONG_TERM_RENTAL",  tz: "Europe/London", units: 8,  occupied: 8, alerts: 0, status: "ok",    devices: 51, integrations: 3 },
  { id: "p_granary",    portfolio: "pf_south", name: "The Old Granary",  address: "bristol_bs1",     type: "SHORT_TERM_RENTAL", tz: "Europe/London", units: 4,  occupied: 3, alerts: 0, status: "ok",    devices: 22, integrations: 3 },
  { id: "p_heron",      portfolio: "pf_south", name: "Heron Place",      address: "london_e1",       type: "LONG_TERM_RENTAL",  tz: "Europe/London", units: 12, occupied: 11,alerts: 0, status: "ok",    devices: 64, integrations: 5 },
  { id: "p_larkspur",   portfolio: "pf_south", name: "Larkspur House",   address: "bath_ba1",        type: "SHORT_TERM_RENTAL", tz: "Europe/London", units: 3,  occupied: 2, alerts: 1, status: "warn",  devices: 18, integrations: 3 },
  { id: "p_willow",     portfolio: "pf_north", name: "Willowbank Lofts", address: "leeds_ls9",       type: "MIXED_USE",         tz: "Europe/London", units: 5,  occupied: 5, alerts: 0, status: "ok",    devices: 31, integrations: 3 },
  { id: "p_hawthorn",   portfolio: "pf_north", name: "Hawthorn Yard",    address: "sheffield_s2",    type: "LONG_TERM_RENTAL",  tz: "Europe/London", units: 4,  occupied: 4, alerts: 0, status: "ok",    devices: 25, integrations: 2 },
  { id: "p_albany",     portfolio: "pf_north", name: "Albany Mews",      address: "edinburgh_eh3",   type: "LONG_TERM_RENTAL",  tz: "Europe/London", units: 6,  occupied: 5, alerts: 0, status: "ok",    devices: 33, integrations: 3 },
  { id: "p_riverside",  portfolio: "pf_north", name: "Riverside Place",  address: "york_yo1",        type: "SHORT_TERM_RENTAL", tz: "Europe/London", units: 5,  occupied: 5, alerts: 0, status: "ok",    devices: 27, integrations: 3 },
  { id: "p_stonecroft", portfolio: "pf_north", name: "Stonecroft",       address: "newcastle_ne1",   type: "OWNER_OCCUPIED",    tz: "Europe/London", units: 7,  occupied: 6, alerts: 0, status: "ok",    devices: 36, integrations: 3 },
];

const ROOMS_MAPLE = [
  { id: "r_3b_living",  name: "Flat 3B · Living",    type: "LIVING",   devices: 4 },
  { id: "r_3b_bed",     name: "Flat 3B · Bedroom",   type: "BEDROOM",  devices: 3 },
  { id: "r_3b_kitchen", name: "Flat 3B · Kitchen",   type: "KITCHEN",  devices: 2 },
  { id: "r_3b_bath",    name: "Flat 3B · Bathroom",  type: "BATHROOM", devices: 2 },
  { id: "r_entry",      name: "Communal · Entry",    type: "ENTRY",    devices: 3 },
  { id: "r_hall",       name: "Communal · Hallway",  type: "OTHER",    devices: 2 },
];

const DEVICES_MAPLE = [
  { id: "d1",  name: "Living thermostat",   room: "Flat 3B · Living",    category: "THERMOSTAT",   vendor: "Nest",        owner: "property", state: "20°C · heat",     reachable: true,  alert: true,  lastSeen: "2m ago",   capabilities: ["TEMPERATURE_SET","HVAC_MODE"] },
  { id: "d2",  name: "Living lamp",         room: "Flat 3B · Living",    category: "LIGHT",        vendor: "Hue",         owner: "property", state: "Off",             reachable: true,  alert: false, lastSeen: "5m ago",   capabilities: ["ON_OFF","BRIGHTNESS","COLOR"] },
  { id: "d3",  name: "Floor lamp",          room: "Flat 3B · Living",    category: "LIGHT",        vendor: "Hue",         owner: "property", state: "Off",             reachable: true,  alert: false, lastSeen: "5m ago",   capabilities: ["ON_OFF","BRIGHTNESS"] },
  { id: "d4",  name: "TV plug",             room: "Flat 3B · Living",    category: "PLUG",         vendor: "Shelly",      owner: "property", state: "Off · 0.0W",      reachable: true,  alert: false, lastSeen: "8m ago",   capabilities: ["ON_OFF","ENERGY_USAGE"] },
  { id: "d5",  name: "Bedroom thermostat",  room: "Flat 3B · Bedroom",   category: "THERMOSTAT",   vendor: "Nest",        owner: "property", state: "18°C · auto",     reachable: true,  alert: false, lastSeen: "2m ago",   capabilities: ["TEMPERATURE_SET","HVAC_MODE"] },
  { id: "d6",  name: "Bedside lamp",        room: "Flat 3B · Bedroom",   category: "LIGHT",        vendor: "Hue",         owner: "property", state: "Off",             reachable: true,  alert: false, lastSeen: "12m ago",  capabilities: ["ON_OFF","BRIGHTNESS","COLOR"] },
  { id: "d7",  name: "Air purifier",        room: "Flat 3B · Bedroom",   category: "PLUG",         vendor: "Shelly",      owner: "property", state: "On · 18W",        reachable: true,  alert: false, lastSeen: "1m ago",   capabilities: ["ON_OFF","ENERGY_USAGE"] },
  { id: "d8",  name: "Front lock",          room: "Communal · Entry",    category: "LOCK",         vendor: "August",      owner: "property", state: "Locked",          reachable: true,  alert: false, lastSeen: "1h ago",   capabilities: ["LOCK"] },
  { id: "d9",  name: "Entry motion",        room: "Communal · Entry",    category: "SENSOR_MOTION",vendor: "SmartThings", owner: "property", state: "Clear",           reachable: true,  alert: false, lastSeen: "3m ago",   capabilities: ["MOTION","BATTERY"] },
  { id: "d10", name: "Leak — under sink",   room: "Flat 3B · Kitchen",   category: "SENSOR_LEAK",  vendor: "SmartThings", owner: "property", state: "Dry",             reachable: true,  alert: false, lastSeen: "10m ago",  capabilities: ["LEAK","BATTERY"] },
  { id: "d11", name: "Kitchen ceiling",     room: "Flat 3B · Kitchen",   category: "LIGHT",        vendor: "Hue",         owner: "property", state: "Off",             reachable: true,  alert: false, lastSeen: "5m ago",   capabilities: ["ON_OFF","BRIGHTNESS"] },
  { id: "d12", name: "Bathroom contact",    room: "Flat 3B · Bathroom",  category: "SENSOR_CONTACT",vendor:"SmartThings", owner: "property", state: "Closed",          reachable: true,  alert: false, lastSeen: "1h ago",   capabilities: ["CONTACT","BATTERY"] },
  { id: "d13", name: "Energy meter",        room: "Communal · Entry",    category: "ENERGY_METER", vendor: "Shelly",      owner: "property", state: "1.2 kW",          reachable: true,  alert: false, lastSeen: "30s ago",  capabilities: ["ENERGY_USAGE"] },
  { id: "d14", name: "Hallway motion",      room: "Communal · Hallway",  category: "SENSOR_MOTION",vendor: "SmartThings", owner: "property", state: "Clear",           reachable: false, alert: true,  lastSeen: "2d ago",   capabilities: ["MOTION","BATTERY"] },
];

const INTEGRATIONS = [
  { id: "i1", vendor: "Nest",        ownerType: "PROPERTY", ownerName: "Northern Portfolio", status: "ACTIVE",        devices: 18, scopes: ["thermostat:read","thermostat:write"], lastSync: "2 min ago",  connectedAt: "12 Jan 2026" },
  { id: "i2", vendor: "Hue",         ownerType: "PROPERTY", ownerName: "Northern Portfolio", status: "ACTIVE",        devices: 47, scopes: ["lights:full"],                          lastSync: "30 sec ago", connectedAt: "12 Jan 2026" },
  { id: "i3", vendor: "August",      ownerType: "PROPERTY", ownerName: "Northern Portfolio", status: "ACTIVE",        devices: 9,  scopes: ["locks:control"],                        lastSync: "1 min ago",  connectedAt: "18 Jan 2026" },
  { id: "i4", vendor: "Shelly",      ownerType: "PROPERTY", ownerName: "Northern Portfolio", status: "ACTIVE",        devices: 32, scopes: ["devices:read","devices:write"],         lastSync: "1 min ago",  connectedAt: "20 Jan 2026" },
  { id: "i5", vendor: "SmartThings", ownerType: "PROPERTY", ownerName: "Northern Portfolio", status: "TOKEN_EXPIRED", devices: 12, scopes: ["sensors:read"],                         lastSync: "6 h ago",    connectedAt: "22 Jan 2026", needsReauth: true },
  { id: "i6", vendor: "Ecobee",      ownerType: "PROPERTY", ownerName: "Southern Portfolio", status: "ACTIVE",        devices: 7,  scopes: ["thermostat:read","thermostat:write"], lastSync: "5 min ago",  connectedAt: "01 Feb 2026" },
];

const STAYS = [
  { id: "s1", property: "Maple Court", unit: "Flat 3B",  tenant: "Sarah Whitmore",   email: "sarah.w@email.com", role: "Long-term tenant", source: "DIRECT",     check_in: "01 Mar 2026", check_out: "28 Feb 2027", status: "ACTIVE",   devices: 2 },
  { id: "s2", property: "Ash Cottage", unit: "Whole",    tenant: "James Okafor",     email: "j.okafor@email.com",role: "Short-let guest",  source: "AIRBNB",     check_in: "31 Mar 2026", check_out: "04 Apr 2026", status: "ACTIVE",   devices: 0 },
  { id: "s3", property: "Larkspur House",unit:"Flat 1",  tenant: "Priya Reddy",      email: "p.reddy@email.com", role: "Short-let guest",  source: "BOOKING_COM",check_in: "30 Mar 2026", check_out: "02 Apr 2026", status: "ACTIVE",   devices: 0, flag: "Late check-in" },
  { id: "s4", property: "Heron Place", unit: "Flat 7",   tenant: "Daniel Kim",       email: "d.kim@email.com",   role: "Long-term tenant", source: "DIRECT",     check_in: "15 Sep 2025", check_out: "—",          status: "ACTIVE",   devices: 4 },
  { id: "s5", property: "The Old Granary",unit:"Whole",  tenant: "Lina Holt",        email: "lina@email.com",    role: "Short-let guest",  source: "VRBO",       check_in: "02 Apr 2026", check_out: "07 Apr 2026", status: "UPCOMING", devices: 0 },
  { id: "s6", property: "Riverside Place",unit:"Flat 2", tenant: "Aiden Park",       email: "a.park@email.com",  role: "Short-let guest",  source: "AIRBNB",     check_in: "05 Apr 2026", check_out: "08 Apr 2026", status: "UPCOMING", devices: 0 },
  { id: "s7", property: "Maple Court", unit: "Flat 1A",  tenant: "Holly Marsh",      email: "h.marsh@email.com", role: "Short-let guest",  source: "AIRBNB",     check_in: "26 Mar 2026", check_out: "29 Mar 2026", status: "COMPLETED",devices: 0 },
];

const AUTOMATIONS = [
  { id: "a1", name: "Pre-arrival warm-up",     owner: "PROPERTY", source: "AGENT",  scope: "Northern Portfolio", trigger: "2h before check-in",    actions: 3, lastRun: "yesterday 14:00", runs: 124, enabled: true },
  { id: "a2", name: "Vacant cool-down",        owner: "PROPERTY", source: "AGENT",  scope: "All portfolios",     trigger: "Check-out + 30 min",    actions: 2, lastRun: "today 11:20",    runs: 87,  enabled: true },
  { id: "a3", name: "Leak → cut water + ping", owner: "PROPERTY", source: "MANUAL", scope: "All portfolios",     trigger: "Leak sensor wet",       actions: 3, lastRun: "—",               runs: 0,   enabled: true },
  { id: "a4", name: "Daily energy summary",    owner: "PROPERTY", source: "AGENT",  scope: "Northern Portfolio", trigger: "Every day 07:30",       actions: 1, lastRun: "today 07:30",    runs: 91,  enabled: true },
  { id: "a5", name: "Frost protection",        owner: "PROPERTY", source: "MANUAL", scope: "All portfolios",     trigger: "Outdoor < 2°C",         actions: 2, lastRun: "12 Mar 03:14",   runs: 8,   enabled: false },
];

const AUDIT = [
  { time: "today 11:24", actor: { name: "Agent",   kind: "AGENT" },     action: "command.execute",       resource: "Device · Living thermostat",      meta: "Set 14°C · Maple Court Flat 3B · owner: property" },
  { time: "today 11:20", actor: { name: "Automation",kind:"AUTOMATION"},action: "automation.run",        resource: "Vacant cool-down",                meta: "Triggered by stay.completed · 2 actions ok" },
  { time: "today 08:42", actor: { name: "Agent",   kind: "AGENT" },     action: "command.execute",       resource: "Device · Living thermostat",      meta: "Approved by Marcus Chen · Maple Court Flat 3B" },
  { time: "today 08:14", actor: { name: "Agent",   kind: "AGENT" },     action: "insight.publish",       resource: "Insight · Vacant heating waste",  meta: "94% confidence · Maple Court Flat 3B" },
  { time: "today 07:30", actor: { name: "System",  kind: "SYSTEM" },    action: "report.generate",       resource: "Daily energy summary",            meta: "12 properties · 1,247 kWh month-to-date" },
  { time: "today 06:47", actor: { name: "Vendor",  kind: "VENDOR" },    action: "webhook.received",      resource: "Integration · SmartThings",       meta: "Subscription event: hub.offline · Northbrook Mill" },
  { time: "yesterday 18:02", actor: { name: "Marcus Chen", kind: "USER" }, action: "membership.create",   resource: "User · Olu Adebayo → Property Manager", meta: "Maple Court, Heron Place" },
  { time: "yesterday 16:30", actor: { name: "Theo Adeyemi", kind: "USER" }, action: "integration.connect", resource: "Integration · Ecobee",        meta: "Owner: Southern Portfolio · 7 devices imported" },
  { time: "yesterday 09:11", actor: { name: "Marcus Chen", kind: "USER" }, action: "automation.update",   resource: "Frost protection",                meta: "Disabled · changed by Marcus Chen" },
];

const TEAM = [
  { name: "Marcus Chen",   email: "marcus@chen.holdings", role: "OWNER",            scope: "Org · Chen Property Holdings", last: "Active now" },
  { name: "Rina Patel",    email: "rina@chen.holdings",   role: "ORG_ADMIN",        scope: "Org · Chen Property Holdings", last: "2 h ago" },
  { name: "Theo Adeyemi",  email: "theo@chen.holdings",   role: "PORTFOLIO_ADMIN",  scope: "Northern Portfolio",           last: "today 09:14" },
  { name: "Jules Marais",  email: "jules@chen.holdings",  role: "PORTFOLIO_MANAGER",scope: "Southern Portfolio",           last: "yesterday" },
  { name: "Olu Adebayo",   email: "olu@chen.holdings",    role: "PROPERTY_MANAGER", scope: "Maple Court, Heron Place",     last: "today 07:30" },
  { name: "Sam Field",     email: "sam@field.contractor", role: "CONTRACTOR",       scope: "Maple Court · expires 30 Apr", last: "yesterday" },
];

const VENDORS = [
  { id: "v_nest",        name: "Nest",        cats: "Thermostats",                        connected: true,  popular: true },
  { id: "v_ecobee",      name: "Ecobee",      cats: "Thermostats",                        connected: true,  popular: true },
  { id: "v_hue",         name: "Philips Hue", cats: "Lights",                             connected: true,  popular: true },
  { id: "v_august",      name: "August",      cats: "Locks",                              connected: true,  popular: true },
  { id: "v_shelly",      name: "Shelly",      cats: "Plugs · Energy meters",              connected: true,  popular: true },
  { id: "v_smartthings", name: "SmartThings", cats: "Hubs · Sensors · Multi-vendor",      connected: true,  popular: true },
  { id: "v_lifx",        name: "LIFX",        cats: "Lights",                             connected: false, popular: false },
  { id: "v_yale",        name: "Yale",        cats: "Locks",                              connected: false, popular: false },
  { id: "v_tado",        name: "Tado",        cats: "Thermostats",                        connected: false, popular: false },
  { id: "v_aqara",       name: "Aqara",       cats: "Sensors · Plugs",                    connected: false, popular: false },
];

Object.assign(window, {
  PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, STAYS, AUTOMATIONS, AUDIT, TEAM, VENDORS,
});
