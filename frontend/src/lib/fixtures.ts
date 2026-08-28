// ─── Portfolio ────────────────────────────────────────────────────────────────

export interface Portfolio {
  id: string;
  name: string;
  region: string;
  manager: string;
}

export const PORTFOLIOS: Portfolio[] = [];

// ─── Property ─────────────────────────────────────────────────────────────────

export type PropertyStatus = "ok" | "warn" | "alert";
export type PropertyType =
  | "MIXED_USE"
  | "SHORT_TERM_RENTAL"
  | "LONG_TERM_RENTAL"
  | "OWNER_OCCUPIED"
  | "COMMERCIAL";

export interface Property {
  id: string;
  portfolio: string;
  name: string;
  address: string;
  type: PropertyType;
  tz: string;
  units: number;
  occupied: number;
  alerts: number;
  status: PropertyStatus;
  devices: number;
  integrations: number;
}

export const PROPERTIES: Property[] = [];

// ─── Rooms ────────────────────────────────────────────────────────────────────

export interface Room {
  id: string;
  name: string;
  type: string;
  devices: number;
}

export const ROOMS_MAPLE: Room[] = [
  { id: "r_3b_living", name: "Flat 3B · Living", type: "LIVING", devices: 4 },
  { id: "r_3b_bed", name: "Flat 3B · Bedroom", type: "BEDROOM", devices: 3 },
  {
    id: "r_3b_kitchen",
    name: "Flat 3B · Kitchen",
    type: "KITCHEN",
    devices: 2,
  },
  { id: "r_3b_bath", name: "Flat 3B · Bathroom", type: "BATHROOM", devices: 2 },
  { id: "r_entry", name: "Communal · Entry", type: "ENTRY", devices: 3 },
  { id: "r_hall", name: "Communal · Hallway", type: "OTHER", devices: 2 },
];

// ─── Devices ──────────────────────────────────────────────────────────────────

export type DeviceCategory =
  | "THERMOSTAT"
  | "LIGHT"
  | "LOCK"
  | "PLUG"
  | "SENSOR_MOTION"
  | "SENSOR_LEAK"
  | "SENSOR_CONTACT"
  | "ENERGY_METER"
  | "SWITCH"
  | "HUB";

export interface Device {
  id: string;
  name: string;
  room: string;
  category: DeviceCategory;
  vendor: string;
  owner: string;
  state: string;
  reachable: boolean;
  alert: boolean;
  lastSeen: string;
  capabilities: string[];
}

export const DEVICES_MAPLE: Device[] = [];

// ─── Integrations ─────────────────────────────────────────────────────────────

export interface Integration {
  id: string;
  vendor: string;
  ownerType: string;
  ownerName: string;
  status: "ACTIVE" | "TOKEN_EXPIRED";
  devices: number;
  scopes: string[];
  lastSync: string;
  connectedAt: string;
  needsReauth?: boolean;
}

export const INTEGRATIONS: Integration[] = [];

// ─── Automations ──────────────────────────────────────────────────────────────

export type AutomationSource = "AGENT" | "MANUAL";

export interface Automation {
  id: string;
  name: string;
  owner: string;
  source: AutomationSource;
  scope: string;
  trigger: string;
  actions: number;
  lastRun: string;
  runs: number;
  enabled: boolean;
}

export const AUTOMATIONS: Automation[] = [
  {
    id: "a1",
    name: "Pre-arrival warm-up",
    owner: "PROPERTY",
    source: "AGENT",
    scope: "Northern Portfolio",
    trigger: "2h before check-in",
    actions: 3,
    lastRun: "yesterday 14:00",
    runs: 124,
    enabled: true,
  },
  {
    id: "a2",
    name: "Vacant cool-down",
    owner: "PROPERTY",
    source: "AGENT",
    scope: "All portfolios",
    trigger: "Check-out + 30 min",
    actions: 2,
    lastRun: "today 11:20",
    runs: 87,
    enabled: true,
  },
  {
    id: "a3",
    name: "Leak → cut water + ping",
    owner: "PROPERTY",
    source: "MANUAL",
    scope: "All portfolios",
    trigger: "Leak sensor wet",
    actions: 3,
    lastRun: "—",
    runs: 0,
    enabled: true,
  },
  {
    id: "a4",
    name: "Daily energy summary",
    owner: "PROPERTY",
    source: "AGENT",
    scope: "Northern Portfolio",
    trigger: "Every day 07:30",
    actions: 1,
    lastRun: "today 07:30",
    runs: 91,
    enabled: true,
  },
  {
    id: "a5",
    name: "Frost protection",
    owner: "PROPERTY",
    source: "MANUAL",
    scope: "All portfolios",
    trigger: "Outdoor < 2°C",
    actions: 2,
    lastRun: "12 Mar 03:14",
    runs: 8,
    enabled: false,
  },
];

// ─── Vendors ──────────────────────────────────────────────────────────────────

export interface Vendor {
  id: string;
  name: string;
  cats: string;
  connected: boolean;
  popular: boolean;
}

export const VENDORS: Vendor[] = [
  {
    id: "v_nest",
    name: "Nest",
    cats: "Thermostats",
    connected: false,
    popular: true,
  },
  {
    id: "v_ecobee",
    name: "Ecobee",
    cats: "Thermostats",
    connected: false,
    popular: true,
  },
  {
    id: "v_hue",
    name: "Philips Hue",
    cats: "Lights",
    connected: false,
    popular: true,
  },
  {
    id: "v_august",
    name: "August",
    cats: "Locks",
    connected: false,
    popular: true,
  },
  {
    id: "v_shelly",
    name: "Shelly",
    cats: "Plugs & meters",
    connected: false,
    popular: true,
  },
  {
    id: "v_smartthings",
    name: "SmartThings",
    cats: "Hubs & bridges · Sensors",
    connected: false,
    popular: true,
  },
  {
    id: "v_lifx",
    name: "LIFX",
    cats: "Lights",
    connected: false,
    popular: false,
  },
  {
    id: "v_yale",
    name: "Yale",
    cats: "Locks",
    connected: false,
    popular: false,
  },
  {
    id: "v_tado",
    name: "Tado",
    cats: "Thermostats",
    connected: false,
    popular: false,
  },
  {
    id: "v_aqara",
    name: "Aqara",
    cats: "Sensors · Plugs & meters",
    connected: false,
    popular: false,
  },
  {
    id: "v_govee",
    name: "Govee",
    cats: "Lights · Sensors",
    connected: false,
    popular: true,
  },
  {
    id: "v_alexa",
    name: "Alexa",
    cats: "Voice · Smart home",
    connected: false,
    popular: true,
  },
  {
    id: "v_hive",
    name: "Hive",
    cats: "Thermostats · Lights",
    connected: false,
    popular: false,
  },
  {
    id: "v_bluetooth",
    name: "Bluetooth",
    cats: "Low energy protocol",
    connected: false,
    popular: false,
  },
  {
    id: "v_wifi",
    name: "WiFi",
    cats: "Network protocol",
    connected: false,
    popular: true,
  },
  {
    id: "v_zigbee",
    name: "Zigbee",
    cats: "Mesh protocol",
    connected: false,
    popular: false,
  },
  {
    id: "v_zwave",
    name: "Z-Wave",
    cats: "Mesh protocol",
    connected: false,
    popular: false,
  },
  {
    id: "v_eve",
    name: "Eve",
    cats: "HomeKit devices",
    connected: false,
    popular: false,
  },
  {
    id: "v_nanoleaf",
    name: "Nanoleaf",
    cats: "Lights",
    connected: false,
    popular: true,
  },
  {
    id: "v_drayton",
    name: "Drayton Wiser",
    cats: "Thermostats",
    connected: false,
    popular: true,
  },
  {
    id: "v_arlo",
    name: "Arlo",
    cats: "Cameras · Security",
    connected: false,
    popular: true,
  },
  {
    id: "v_sonos",
    name: "Sonos",
    cats: "Audio · Speakers",
    connected: false,
    popular: true,
  },
  {
    id: "v_homekit",
    name: "Apple HomeKit",
    cats: "Multi-vendor · Ecosystem",
    connected: false,
    popular: true,
  },
  {
    id: "v_lutron",
    name: "Lutron",
    cats: "Lights",
    connected: false,
    popular: false,
  },
  {
    id: "v_leviton",
    name: "Leviton",
    cats: "Plugs & meters",
    connected: false,
    popular: false,
  },
  {
    id: "v_inovelli",
    name: "Inovelli",
    cats: "Plugs & meters",
    connected: false,
    popular: false,
  },
  {
    id: "v_kasa",
    name: "Kasa (TP-Link)",
    cats: "Plugs & meters · Lights",
    connected: false,
    popular: true,
  },
  {
    id: "v_meross",
    name: "Meross",
    cats: "Plugs & meters",
    connected: false,
    popular: false,
  },
  {
    id: "v_ge_cstart",
    name: "GE Cync",
    cats: "Lights",
    connected: false,
    popular: false,
  },
  {
    id: "v_eaton",
    name: "Eaton Smart Home",
    cats: "Electrical Devices",
    connected: false,
    popular: false,
  },
];

// ─── Team ─────────────────────────────────────────────────────────────────────

export type TeamRole =
  | "OWNER"
  | "ORG_ADMIN"
  | "PORTFOLIO_ADMIN"
  | "PORTFOLIO_MANAGER"
  | "PROPERTY_MANAGER"
  | "CONTRACTOR";

export interface TeamMember {
  name: string;
  email: string;
  role: TeamRole;
  scope: string;
  last: string;
}

export const TEAM: TeamMember[] = [
  {
    name: "Marcus Chen",
    email: "marcus@chen.holdings",
    role: "OWNER",
    scope: "Org · Chen Property Holdings",
    last: "Active now",
  },
  {
    name: "Rina Patel",
    email: "rina@chen.holdings",
    role: "ORG_ADMIN",
    scope: "Org · Chen Property Holdings",
    last: "2 h ago",
  },
  {
    name: "Theo Adeyemi",
    email: "theo@chen.holdings",
    role: "PORTFOLIO_ADMIN",
    scope: "Northern Portfolio",
    last: "today 09:14",
  },
  {
    name: "Jules Marais",
    email: "jules@chen.holdings",
    role: "PORTFOLIO_MANAGER",
    scope: "Southern Portfolio",
    last: "yesterday",
  },
  {
    name: "Olu Adebayo",
    email: "olu@chen.holdings",
    role: "PROPERTY_MANAGER",
    scope: "Maple Court, Heron Place",
    last: "today 07:30",
  },
  {
    name: "Sam Field",
    email: "sam@field.contractor",
    role: "CONTRACTOR",
    scope: "Maple Court · expires 30 Apr",
    last: "yesterday",
  },
];

// ─── Audit log ────────────────────────────────────────────────────────────────

export type AuditActorKind =
  | "AGENT"
  | "AUTOMATION"
  | "USER"
  | "SYSTEM"
  | "VENDOR";

export interface AuditActor {
  name: string;
  kind: AuditActorKind;
}

export interface AuditEntry {
  time: string;
  actor: AuditActor;
  action: string;
  resource: string;
  meta: string;
}

export const AUDIT: AuditEntry[] = [
  {
    time: "today 11:24",
    actor: { name: "Agent", kind: "AGENT" },
    action: "command.execute",
    resource: "Device · Living thermostat",
    meta: "Set 14°C · Maple Court Flat 3B · owner: property",
  },
  {
    time: "today 11:20",
    actor: { name: "Automation", kind: "AUTOMATION" },
    action: "automation.run",
    resource: "Vacant cool-down",
    meta: "Triggered by stay.completed · 2 actions ok",
  },
  {
    time: "today 08:42",
    actor: { name: "Agent", kind: "AGENT" },
    action: "command.execute",
    resource: "Device · Living thermostat",
    meta: "Approved by Marcus Chen · Maple Court Flat 3B",
  },
  {
    time: "today 08:14",
    actor: { name: "Agent", kind: "AGENT" },
    action: "insight.publish",
    resource: "Insight · Vacant heating waste",
    meta: "94% confidence · Maple Court Flat 3B",
  },
  {
    time: "today 07:30",
    actor: { name: "System", kind: "SYSTEM" },
    action: "report.generate",
    resource: "Daily energy summary",
    meta: "12 properties · 1,247 kWh month-to-date",
  },
  {
    time: "today 06:47",
    actor: { name: "Vendor", kind: "VENDOR" },
    action: "webhook.received",
    resource: "Integration · SmartThings",
    meta: "Subscription event: hub.offline · Northbrook Mill",
  },
  {
    time: "yesterday 18:02",
    actor: { name: "Marcus Chen", kind: "USER" },
    action: "membership.create",
    resource: "User · Olu Adebayo → Property Manager",
    meta: "Maple Court, Heron Place",
  },
  {
    time: "yesterday 16:30",
    actor: { name: "Theo Adeyemi", kind: "USER" },
    action: "integration.connect",
    resource: "Integration · Ecobee",
    meta: "Owner: Southern Portfolio · 7 devices imported",
  },
  {
    time: "yesterday 09:11",
    actor: { name: "Marcus Chen", kind: "USER" },
    action: "automation.update",
    resource: "Frost protection",
    meta: "Disabled · changed by Marcus Chen",
  },
];
