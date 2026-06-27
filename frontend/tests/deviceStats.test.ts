import { describe, expect, it } from "vitest";
import { summarizeDevices } from "@/lib/deviceStats";
import type { SpireDevice, VendorName } from "@/lib/types";

function device(
  vendor: VendorName,
  online: boolean,
  id = `${vendor}-${online}`,
): SpireDevice {
  return {
    id,
    vendor_id: id,
    vendor,
    name: id,
    type: "plug",
    online,
    controllable: true,
    state: {},
    power_draw: null,
    temperature: null,
    humidity: null,
    leak_detected: null,
    property_id: null,
    room_id: null,
    last_seen: "2026-01-01T00:00:00Z",
    supported_commands: [],
  };
}

describe("summarizeDevices", () => {
  it("counts real hardware separately from demo devices", () => {
    const summary = summarizeDevices([
      device("shelly", true, "shelly-1"),
      device("matter", false, "matter-1"),
      device("demo", true, "demo-1"),
      device("demo", true, "demo-2"),
    ]);

    expect(summary.real).toBe(2);
    expect(summary.demo).toBe(2);
  });

  it("derives online and offline from real hardware only, ignoring demo state", () => {
    const summary = summarizeDevices([
      device("shelly", true, "shelly-1"),
      device("matter", false, "matter-1"),
      // Demo devices are online but must not inflate the online figure.
      device("demo", true, "demo-1"),
    ]);

    expect(summary.online).toBe(1);
    expect(summary.offline).toBe(1);
    expect(summary.online + summary.offline).toBe(summary.real);
  });

  it("returns all zeros for an empty list", () => {
    expect(summarizeDevices([])).toEqual({
      real: 0,
      online: 0,
      offline: 0,
      demo: 0,
    });
  });

  it("handles a demo-only portfolio without reporting connected hardware", () => {
    const summary = summarizeDevices([
      device("demo", true, "demo-1"),
      device("demo", false, "demo-2"),
    ]);

    expect(summary.real).toBe(0);
    expect(summary.online).toBe(0);
    expect(summary.offline).toBe(0);
    expect(summary.demo).toBe(2);
  });
});
