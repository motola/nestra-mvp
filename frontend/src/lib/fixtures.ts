// ─── Portfolio ────────────────────────────────────────────────────────────────

export interface Portfolio {
  id: string;
  name: string;
  region: string;
  manager: string;
}

export const PORTFOLIOS: Portfolio[] = [
  {
    id: "pf_north",
    name: "Northern Portfolio",
    region: "North England + Scotland",
    manager: "Theo Adeyemi",
  },
  {
    id: "pf_south",
    name: "Southern Portfolio",
    region: "London + South West",
    manager: "Jules Marais",
  },
];

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

export const PROPERTIES: Property[] = [
  {
    id: "p_maple",
    portfolio: "pf_north",
    name: "Maple Court",
    address: "leeds_ls1",
    type: "MIXED_USE",
    tz: "Europe/London",
    units: 6,
    occupied: 4,
    alerts: 1,
    status: "warn",
    devices: 38,
    integrations: 4,
  },
  {
    id: "p_ash",
    portfolio: "pf_south",
    name: "Ash Cottage",
    address: "oxford_ox4",
    type: "SHORT_TERM_RENTAL",
    tz: "Europe/London",
    units: 1,
    occupied: 1,
    alerts: 0,
    status: "ok",
    devices: 14,
    integrations: 3,
  },
  {
    id: "p_northbrook",
    portfolio: "pf_north",
    name: "Northbrook Mill",
    address: "manchester_m1",
    type: "LONG_TERM_RENTAL",
    tz: "Europe/London",
    units: 7,
    occupied: 5,
    alerts: 2,
    status: "alert",
    devices: 42,
    integrations: 4,
  },
  {
    id: "p_seacombe",
    portfolio: "pf_north",
    name: "Seacombe Wharf",
    address: "liverpool_l3",
    type: "LONG_TERM_RENTAL",
    tz: "Europe/London",
    units: 8,
    occupied: 8,
    alerts: 0,
    status: "ok",
    devices: 51,
    integrations: 3,
  },
  {
    id: "p_granary",
    portfolio: "pf_south",
    name: "The Old Granary",
    address: "bristol_bs1",
    type: "SHORT_TERM_RENTAL",
    tz: "Europe/London",
    units: 4,
    occupied: 3,
    alerts: 0,
    status: "ok",
    devices: 22,
    integrations: 3,
  },
  {
    id: "p_heron",
    portfolio: "pf_south",
    name: "Heron Place",
    address: "london_e1",
    type: "LONG_TERM_RENTAL",
    tz: "Europe/London",
    units: 12,
    occupied: 11,
    alerts: 0,
    status: "ok",
    devices: 64,
    integrations: 5,
  },
  {
    id: "p_larkspur",
    portfolio: "pf_south",
    name: "Larkspur House",
    address: "bath_ba1",
    type: "SHORT_TERM_RENTAL",
    tz: "Europe/London",
    units: 3,
    occupied: 2,
    alerts: 1,
    status: "warn",
    devices: 18,
    integrations: 3,
  },
  {
    id: "p_willow",
    portfolio: "pf_north",
    name: "Willowbank Lofts",
    address: "leeds_ls9",
    type: "MIXED_USE",
    tz: "Europe/London",
    units: 5,
    occupied: 5,
    alerts: 0,
    status: "ok",
    devices: 31,
    integrations: 3,
  },
  {
    id: "p_hawthorn",
    portfolio: "pf_north",
    name: "Hawthorn Yard",
    address: "sheffield_s2",
    type: "LONG_TERM_RENTAL",
    tz: "Europe/London",
    units: 4,
    occupied: 4,
    alerts: 0,
    status: "ok",
    devices: 25,
    integrations: 2,
  },
  {
    id: "p_albany",
    portfolio: "pf_north",
    name: "Albany Mews",
    address: "edinburgh_eh3",
    type: "LONG_TERM_RENTAL",
    tz: "Europe/London",
    units: 6,
    occupied: 5,
    alerts: 0,
    status: "ok",
    devices: 33,
    integrations: 3,
  },
  {
    id: "p_riverside",
    portfolio: "pf_north",
    name: "Riverside Place",
    address: "york_yo1",
    type: "SHORT_TERM_RENTAL",
    tz: "Europe/London",
    units: 5,
    occupied: 5,
    alerts: 0,
    status: "ok",
    devices: 27,
    integrations: 3,
  },
  {
    id: "p_stonecroft",
    portfolio: "pf_north",
    name: "Stonecroft",
    address: "newcastle_ne1",
    type: "OWNER_OCCUPIED",
    tz: "Europe/London",
    units: 7,
    occupied: 6,
    alerts: 0,
    status: "ok",
    devices: 36,
    integrations: 3,
  },
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

export const DEVICES_MAPLE: Device[] = [
  {
    id: "d1",
    name: "Living thermostat",
    room: "Flat 3B · Living",
    category: "THERMOSTAT",
    vendor: "Nest",
    owner: "property",
    state: "20°C · heat",
    reachable: true,
    alert: true,
    lastSeen: "2m ago",
    capabilities: ["TEMPERATURE_SET", "HVAC_MODE"],
  },
  {
    id: "d2",
    name: "Living lamp",
    room: "Flat 3B · Living",
    category: "LIGHT",
    vendor: "Hue",
    owner: "property",
    state: "Off",
    reachable: true,
    alert: false,
    lastSeen: "5m ago",
    capabilities: ["ON_OFF", "BRIGHTNESS", "COLOR"],
  },
  {
    id: "d3",
    name: "Floor lamp",
    room: "Flat 3B · Living",
    category: "LIGHT",
    vendor: "Hue",
    owner: "property",
    state: "Off",
    reachable: true,
    alert: false,
    lastSeen: "5m ago",
    capabilities: ["ON_OFF", "BRIGHTNESS"],
  },
  {
    id: "d4",
    name: "TV plug",
    room: "Flat 3B · Living",
    category: "PLUG",
    vendor: "Shelly",
    owner: "property",
    state: "Off · 0.0W",
    reachable: true,
    alert: false,
    lastSeen: "8m ago",
    capabilities: ["ON_OFF", "ENERGY_USAGE"],
  },
  {
    id: "d5",
    name: "Bedroom thermostat",
    room: "Flat 3B · Bedroom",
    category: "THERMOSTAT",
    vendor: "Nest",
    owner: "property",
    state: "18°C · auto",
    reachable: true,
    alert: false,
    lastSeen: "2m ago",
    capabilities: ["TEMPERATURE_SET", "HVAC_MODE"],
  },
  {
    id: "d6",
    name: "Bedside lamp",
    room: "Flat 3B · Bedroom",
    category: "LIGHT",
    vendor: "Hue",
    owner: "property",
    state: "Off",
    reachable: true,
    alert: false,
    lastSeen: "12m ago",
    capabilities: ["ON_OFF", "BRIGHTNESS", "COLOR"],
  },
  {
    id: "d7",
    name: "Air purifier",
    room: "Flat 3B · Bedroom",
    category: "PLUG",
    vendor: "Shelly",
    owner: "property",
    state: "On · 18W",
    reachable: true,
    alert: false,
    lastSeen: "1m ago",
    capabilities: ["ON_OFF", "ENERGY_USAGE"],
  },
  {
    id: "d8",
    name: "Front lock",
    room: "Communal · Entry",
    category: "LOCK",
    vendor: "August",
    owner: "property",
    state: "Locked",
    reachable: true,
    alert: false,
    lastSeen: "1h ago",
    capabilities: ["LOCK"],
  },
  {
    id: "d9",
    name: "Entry motion",
    room: "Communal · Entry",
    category: "SENSOR_MOTION",
    vendor: "SmartThings",
    owner: "property",
    state: "Clear",
    reachable: true,
    alert: false,
    lastSeen: "3m ago",
    capabilities: ["MOTION", "BATTERY"],
  },
  {
    id: "d10",
    name: "Leak — under sink",
    room: "Flat 3B · Kitchen",
    category: "SENSOR_LEAK",
    vendor: "SmartThings",
    owner: "property",
    state: "Dry",
    reachable: true,
    alert: false,
    lastSeen: "10m ago",
    capabilities: ["LEAK", "BATTERY"],
  },
  {
    id: "d11",
    name: "Kitchen ceiling",
    room: "Flat 3B · Kitchen",
    category: "LIGHT",
    vendor: "Hue",
    owner: "property",
    state: "Off",
    reachable: true,
    alert: false,
    lastSeen: "5m ago",
    capabilities: ["ON_OFF", "BRIGHTNESS"],
  },
  {
    id: "d12",
    name: "Bathroom contact",
    room: "Flat 3B · Bathroom",
    category: "SENSOR_CONTACT",
    vendor: "SmartThings",
    owner: "property",
    state: "Closed",
    reachable: true,
    alert: false,
    lastSeen: "1h ago",
    capabilities: ["CONTACT", "BATTERY"],
  },
  {
    id: "d13",
    name: "Energy meter",
    room: "Communal · Entry",
    category: "ENERGY_METER",
    vendor: "Shelly",
    owner: "property",
    state: "1.2 kW",
    reachable: true,
    alert: false,
    lastSeen: "30s ago",
    capabilities: ["ENERGY_USAGE"],
  },
  {
    id: "d14",
    name: "Hallway motion",
    room: "Communal · Hallway",
    category: "SENSOR_MOTION",
    vendor: "SmartThings",
    owner: "property",
    state: "Clear",
    reachable: false,
    alert: true,
    lastSeen: "2d ago",
    capabilities: ["MOTION", "BATTERY"],
  },
];
