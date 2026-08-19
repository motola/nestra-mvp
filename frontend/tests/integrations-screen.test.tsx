import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { IntegrationsScreen } from "../src/components/integrations/integrations-screen";
import { PropertyProvider } from "../src/lib/property/provider";

describe("IntegrationsScreen", () => {
  it("renders empty state by default", () => {
    render(
      <PropertyProvider>
        <IntegrationsScreen />
      </PropertyProvider>,
    );
    expect(screen.getByRole("heading", { name: "Integrations" })).toBeDefined();
    expect(screen.getByText("No connections yet")).toBeDefined();
  });
});
