import { describe, expect, it } from "vitest";
import { formatRelativeTime, providerLabel } from "../src/app/demo/types";

describe("formatRelativeTime", () => {
  it("returns 'just now' for times under 10 seconds ago", () => {
    const now = new Date();
    expect(formatRelativeTime(now)).toBe("just now");
  });

  it("returns seconds for times 10–59 seconds ago", () => {
    const past = new Date(Date.now() - 30_000);
    expect(formatRelativeTime(past)).toBe("30s ago");
  });

  it("returns minutes for times 1–59 minutes ago", () => {
    const past = new Date(Date.now() - 5 * 60_000);
    expect(formatRelativeTime(past)).toBe("5m ago");
  });

  it("returns hours for times over an hour ago", () => {
    const past = new Date(Date.now() - 2 * 60 * 60_000);
    expect(formatRelativeTime(past)).toBe("2h ago");
  });
});

describe("providerLabel", () => {
  it("returns LIFX for lifx provider", () => {
    expect(providerLabel("lifx")).toBe("LIFX");
  });

  it("returns Govee for govee provider", () => {
    expect(providerLabel("govee")).toBe("Govee");
  });
});
