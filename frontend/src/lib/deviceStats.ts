import type { AlphaconDevice } from "@/lib/types";

export interface DeviceSummary {
  /** Physical hardware connected (excludes seeded demo devices). */
  real: number;
  /** Online count among real hardware only. */
  online: number;
  /** Offline count among real hardware only. */
  offline: number;
  /** Seeded demo / sample devices. */
  demo: number;
}

/**
 * Counts physical hardware separately from seeded demo devices so the Devices
 * page agrees with the Integrations page on what is actually connected. Online
 * and offline reflect real hardware only — demo devices carry synthetic state
 * that must never inflate the connectivity figures the operator relies on.
 */
export function summarizeDevices(devices: AlphaconDevice[]): DeviceSummary {
  const real = devices.filter((d) => d.vendor !== "demo");
  const online = real.filter((d) => d.online).length;
  return {
    real: real.length,
    online,
    offline: real.length - online,
    demo: devices.length - real.length,
  };
}
