/**
 * Alphacon platform types — mirrors the backend Pydantic models exactly.
 * Nothing in the frontend should reference a vendor-specific field name.
 * All vendor data arrives pre-normalised via the backend abstraction layer.
 */

export type DeviceType = "plug" | "light" | "sensor" | "lock" | "thermostat";
export type VendorName = "govee" | "shelly" | "lifx" | "matter" | "demo";
export type PropertyStatus = "all_clear" | "needs_attention" | "critical";
export type AlertSeverity = "info" | "warning" | "critical";
export type InsightSeverity = "info" | "warning" | "critical";

export interface SpireDevice {
  id: string;
  vendor_id: string;
  vendor: VendorName;
  name: string;
  type: DeviceType;
  online: boolean;
  controllable: boolean;
  state: Record<string, unknown>;
  power_draw: number | null;
  temperature: number | null;
  humidity: number | null;
  leak_detected: boolean | null;
  property_id: string | null;
  room_id?: string | null;
  last_seen: string;
  supported_commands: string[];
}

export interface Property {
  id: string;
  name: string;
  address: string;
  organisation_id: string | null;
  device_count: number;
  alert_count: number;
  status: PropertyStatus;
  is_demo: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatStreamEvent {
  type: "text" | "error" | "done";
  text?: string;
  message?: string;
}

export interface Room {
  id: string;
  property_id: string;
  name: string;
  floor: number | null;
  device_count: number;
  alert_count: number;
}

export interface Alert {
  id: string;
  device_id: string;
  device_name: string;
  property_id: string;
  property_name: string;
  type: string;
  severity: AlertSeverity;
  message: string;
  created_at: string;
  dismissed: boolean;
}

export interface Insight {
  device_id: string;
  message: string;
  severity: InsightSeverity;
  generated_at: string;
  cached: boolean;
  model_used: string;
}

export interface VendorIntegration {
  vendor: VendorName;
  display_name: string;
  description: string;
  connected: boolean;
}

export interface ScannedDevice {
  vendor: string;
  name: string;
  model: string;
  ip: string;
  mac: string;
  raw: Record<string, unknown>;
}

export interface SavedDevice {
  id: string;
  property_id: string | null;
  room_id?: string | null;
  vendor: string;
  vendor_id: string | null;
  name: string;
  model: string | null;
  ip_address: string | null;
  mac: string | null;
  created_at: string;
}

export interface ProvisionEvent {
  type: "status" | "device" | "error" | "done";
  message?: string;
  device?: ScannedDevice;
}

export interface CommissionedDeviceInfo {
  id: string;
  name: string;
  vendor: string;
  vendor_id: string;
  property_id: string | null;
  room_id?: string | null;
}

export interface CommissionEvent {
  type: "status" | "device" | "error" | "done";
  message?: string;
  device?: CommissionedDeviceInfo;
}

export interface ShellyDeviceState {
  device_id: string;
  on: boolean;
  power: number;
  voltage: number;
  current: number;
  energy: number;
  online: boolean;
}

export interface PowerHistoryPoint {
  recorded_at: string;
  value: string;
}

export interface MatterDeviceState {
  device_id: string;
  node_id: string;
  online: boolean;
  on_off: boolean | null;
  brightness: number | null;
}

export interface StateHistoryEvent {
  id: string;
  device_id: string;
  property_id: string | null;
  event_type: string;
  value: string | null;
  recorded_at: string;
}

export type IntelligenceSeverity = "info" | "warning" | "critical";
export type IntelligenceType =
  | "maintenance_prediction"
  | "risk_score"
  | "occupancy_pattern"
  | "environmental";

export interface IntelligenceItem {
  id: string;
  property_id: string;
  property_name: string;
  type: IntelligenceType;
  severity: IntelligenceSeverity;
  title: string;
  detail: string;
  generated_at: string;
  metric: number | null;
  unit: string | null;
}
