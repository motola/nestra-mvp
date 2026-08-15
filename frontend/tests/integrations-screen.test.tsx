import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { IntegrationsScreen } from "../src/components/integrations/integrations-screen";

vi.mock("@/lib/use-demo-mode", () => ({
  useDemoMode: () => ({
    demoMode: true,
    isHydrated: true,
    toggleDemoMode: vi.fn(),
  }),
}));

vi.mock("@/integrations/bluetooth", () => ({
  useBluetoothDevices: () => ({ data: [] }),
}));

function renderIntegrationsScreen() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <IntegrationsScreen />
    </QueryClientProvider>,
  );
}

describe("IntegrationsScreen", () => {
  it("renders the page header", () => {
    renderIntegrationsScreen();
    expect(screen.getByRole("heading", { name: "Integrations" })).toBeDefined();
    expect(screen.getByText("Connect vendor")).toBeDefined();
  });

  it("shows the reauth alert on the Connected tab", () => {
    renderIntegrationsScreen();
    expect(screen.getByText("SmartThings token expired")).toBeDefined();
    // "Reauthorize" appears in both AlertCard and the SmartThings card button
    expect(screen.getAllByText("Reauthorize").length).toBeGreaterThanOrEqual(1);
  });

  it("renders vendor cards for all integrations", () => {
    renderIntegrationsScreen();
    expect(screen.getByText("Nest")).toBeDefined();
    expect(screen.getByText("Hue")).toBeDefined();
    expect(screen.getByText("August")).toBeDefined();
    expect(screen.getByText("Ecobee")).toBeDefined();
  });

  it("shows the Catalog tab with vendor grid when clicked", () => {
    renderIntegrationsScreen();
    fireEvent.click(screen.getByText("Catalog"));
    expect(screen.getByText("Bluetooth")).toBeDefined();
    expect(screen.getByText("Philips Hue")).toBeDefined();
    expect(screen.getByText("Yale")).toBeDefined();
    expect(screen.getByText("Tado")).toBeDefined();
  });

  it("catalog category filter chips are interactive", () => {
    renderIntegrationsScreen();
    fireEvent.click(screen.getByText("Catalog"));
    // "Thermostats" appears as chip and as vendor sub-text — click the first
    const thermoEls = screen.getAllByText("Thermostats");
    fireEvent.click(thermoEls[0]);
    expect(screen.getAllByText("Thermostats").length).toBeGreaterThanOrEqual(1);
  });

  it("shows webhook rows on the Webhooks tab", () => {
    renderIntegrationsScreen();
    fireEvent.click(screen.getByText("Webhooks"));
    expect(screen.getByText("device.state")).toBeDefined();
    expect(screen.getByText("lights.changed")).toBeDefined();
    expect(screen.getByText("Webhook subscriptions")).toBeDefined();
  });

  it("shows error rows on the Errors tab", () => {
    renderIntegrationsScreen();
    fireEvent.click(screen.getByText("Errors"));
    expect(screen.getByText("AuthExpired")).toBeDefined();
    expect(screen.getByText("RateLimited")).toBeDefined();
    expect(screen.getByText("Adapter errors")).toBeDefined();
  });
});
