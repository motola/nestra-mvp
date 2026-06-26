import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PropertyCard } from "../src/components/ui/property-card";
import { DataTable } from "../src/components/ui/data-table";
import { Tabs } from "../src/components/ui/tabs";

const MOCK_PROPERTY = {
  id: "p_test",
  portfolio: "pf_north",
  name: "Test House",
  address: "london_e1",
  type: "LONG_TERM_RENTAL" as const,
  tz: "Europe/London",
  units: 4,
  occupied: 3,
  alerts: 1,
  status: "warn" as const,
  devices: 20,
  integrations: 2,
};

describe("PropertyCard", () => {
  it("renders name, address and type tag", () => {
    render(<PropertyCard {...MOCK_PROPERTY} />);
    expect(screen.getByText("Test House")).toBeDefined();
    expect(screen.getByText("london_e1")).toBeDefined();
    expect(screen.getByText("long term rental")).toBeDefined();
  });

  it("shows warn alert tag when alerts > 0", () => {
    render(<PropertyCard {...MOCK_PROPERTY} />);
    expect(screen.getByText("1 alert")).toBeDefined();
  });

  it("shows all clear tag when no alerts", () => {
    render(<PropertyCard {...MOCK_PROPERTY} alerts={0} status="ok" />);
    expect(screen.getByText("All clear")).toBeDefined();
  });

  it("calls onClick when clicked", () => {
    const handler = vi.fn();
    render(<PropertyCard {...MOCK_PROPERTY} onClick={handler} />);
    fireEvent.click(screen.getByText("Test House"));
    expect(handler).toHaveBeenCalledOnce();
  });
});

describe("DataTable", () => {
  const columns = [
    { k: "name", label: "Name", w: "1fr" },
    { k: "value", label: "Value", w: "1fr" },
  ];
  const rows = [
    { name: "Alpha", value: "1" },
    { name: "Beta", value: "2" },
  ];

  it("renders column headers", () => {
    render(<DataTable columns={columns} rows={rows} />);
    expect(screen.getByText("Name")).toBeDefined();
    expect(screen.getByText("Value")).toBeDefined();
  });

  it("renders row data", () => {
    render(<DataTable columns={columns} rows={rows} />);
    expect(screen.getByText("Alpha")).toBeDefined();
    expect(screen.getByText("Beta")).toBeDefined();
  });

  it("calls onRowClick when a row is clicked", () => {
    const handler = vi.fn();
    render(<DataTable columns={columns} rows={rows} onRowClick={handler} />);
    fireEvent.click(screen.getByText("Alpha"));
    expect(handler).toHaveBeenCalledWith(rows[0]);
  });
});

describe("Tabs", () => {
  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "devices", label: "Devices", count: 38 },
  ];

  it("renders tab labels", () => {
    render(<Tabs value="overview" onChange={() => {}} tabs={tabs} />);
    expect(screen.getByText("Overview")).toBeDefined();
    expect(screen.getByText("Devices")).toBeDefined();
  });

  it("renders count badge when provided", () => {
    render(<Tabs value="overview" onChange={() => {}} tabs={tabs} />);
    expect(screen.getByText("38")).toBeDefined();
  });

  it("calls onChange when a tab is clicked", () => {
    const handler = vi.fn();
    render(<Tabs value="overview" onChange={handler} tabs={tabs} />);
    fireEvent.click(screen.getByText("Devices"));
    expect(handler).toHaveBeenCalledWith("devices");
  });
});
