export type PropertyStatus = "ok" | "warn" | "alert";
export type PropertyType =
  | "MIXED_USE"
  | "SHORT_TERM_RENTAL"
  | "LONG_TERM_RENTAL"
  | "OWNER_OCCUPIED"
  | "COMMERCIAL";

export interface Property {
  id: string;
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
