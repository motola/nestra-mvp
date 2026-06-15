import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard } from "../src/components/ui/stat-card";
import { Tag } from "../src/components/ui/tag";
import { AlertCard } from "../src/components/ui/alert-card";

describe("StatCard", () => {
  it("renders label and value", () => {
    render(<StatCard label="Properties" value={12} sub="72 units total" />);
    expect(screen.getByText("Properties")).toBeDefined();
    expect(screen.getByText("12")).toBeDefined();
    expect(screen.getByText("72 units total")).toBeDefined();
  });

  it("renders with a unit suffix", () => {
    render(
      <StatCard label="Occupancy" value={87} unit="%" sub="vs last month" />,
    );
    expect(screen.getByText("87")).toBeDefined();
    expect(screen.getByText("%")).toBeDefined();
  });
});

describe("Tag", () => {
  it("renders ok variant", () => {
    render(<Tag variant="ok">All clear</Tag>);
    expect(screen.getByText("All clear")).toBeDefined();
  });

  it("renders with a dot", () => {
    const { container } = render(
      <Tag variant="warn" withDot>
        1 alert
      </Tag>,
    );
    const dot = container.querySelector(".rounded-full");
    expect(dot).not.toBeNull();
  });
});

describe("AlertCard", () => {
  it("renders title, desc, and action buttons", () => {
    render(
      <AlertCard
        severity="amber"
        title="Vacant heating on"
        desc="Unit has been vacant for 4 days."
        meta="Energy · Today 08:14"
        actions={["Turn off", "Dismiss"]}
      />,
    );
    expect(screen.getByText("Vacant heating on")).toBeDefined();
    expect(screen.getByText("Turn off")).toBeDefined();
    expect(screen.getByText("Dismiss")).toBeDefined();
  });
});
