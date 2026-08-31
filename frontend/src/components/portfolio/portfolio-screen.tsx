"use client"; // Client: portfolio selection, property browsing

import { useCallback, useEffect, useState } from "react";
import {
  Plus,
  Download,
  LayoutGrid,
  ChevronRight,
  List,
  ArrowLeft,
} from "lucide-react";
import { cn } from "@/lib/cn";
import type { Property, PropertyType } from "@/lib/fixtures";
import {
  createPortfolio,
  listPortfolios,
  listProperties,
  updatePortfolio,
  updateProperty,
  createProperty,
} from "@/lib/api/portfolios";
import type {
  Portfolio as ApiPortfolio,
  Property as ApiProperty,
} from "@/lib/api/portfolios";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { PropertyCard } from "@/components/ui/property-card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";
import { useAuth } from "@/lib/auth/provider";
import { AddPortfolioForm } from "@/components/portfolio/add-portfolio-form";
import { EditPortfolioForm } from "@/components/portfolio/edit-portfolio-form";
import { PropertyForm } from "@/components/portfolio/property-form";
import { logger } from "@/lib/logger";

// ─── API → display adapter ────────────────────────────────────────────────────

const PROPERTY_TYPES: PropertyType[] = [
  "MIXED_USE",
  "SHORT_TERM_RENTAL",
  "LONG_TERM_RENTAL",
  "OWNER_OCCUPIED",
  "COMMERCIAL",
];

/**
 * Map an API property onto the shape the cards, table and property provider
 * expect. Occupancy, device and alert counts come from subsystems that are not
 * exposed by the API yet, so they read as zero until those land.
 */
function toDisplayProperty(p: ApiProperty): Property {
  return {
    id: p.id,
    portfolio: p.portfolio_id,
    name: p.name,
    address: p.address,
    type: PROPERTY_TYPES.includes(p.property_type as PropertyType)
      ? (p.property_type as PropertyType)
      : "MIXED_USE",
    tz: p.timezone,
    units: p.units,
    occupied: 0,
    alerts: 0,
    status: "ok",
    devices: 0,
    integrations: 0,
  };
}

// ─── Table columns for list view ─────────────────────────────────────────────

const TABLE_COLUMNS: TableColumn<Property>[] = [
  {
    k: "name",
    label: "Property",
    w: "1.4fr",
    render: (r) => (
      <div>
        <div className="font-serif text-[16px] text-text">{r.name}</div>
        <div className="font-mono text-[11px] uppercase tracking-[0.08em] text-text-3 mt-0.5">
          {r.address}
        </div>
      </div>
    ),
  },
  {
    k: "type",
    label: "Type",
    w: "0.9fr",
    render: (r) => (
      <span className="text-[12px] text-text-2">
        {r.type.replace(/_/g, " ").toLowerCase()}
      </span>
    ),
  },
  {
    k: "units",
    label: "Units",
    w: "0.5fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">{r.units}</span>
    ),
  },
  {
    k: "occupied",
    label: "Occupied",
    w: "0.7fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">
        {r.occupied}/{r.units}
      </span>
    ),
  },
  {
    k: "devices",
    label: "Devices",
    w: "0.6fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">{r.devices}</span>
    ),
  },
  {
    k: "integrations",
    label: "Integrations",
    w: "0.7fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">
        {r.integrations}
      </span>
    ),
  },
  {
    k: "status",
    label: "Status",
    w: "0.8fr",
    render: (r) =>
      r.alerts > 0 ? (
        <Tag variant={r.status === "alert" ? "alert" : "warn"} withDot>
          {r.alerts} alert{r.alerts > 1 ? "s" : ""}
        </Tag>
      ) : (
        <Tag variant="ok" withDot>
          All clear
        </Tag>
      ),
  },
  {
    k: "actions",
    label: "",
    w: "30px",
    align: "right",
    render: () => (
      <ChevronRight size={14} strokeWidth={1.5} className="text-text-3" />
    ),
  },
];

// ─── Filter chips ─────────────────────────────────────────────────────────────

type StatusFilter = "all" | "ok" | "warn" | "alert";

const FILTERS: { id: StatusFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "ok", label: "Clear" },
  { id: "warn", label: "Attention" },
  { id: "alert", label: "Critical" },
];

function FilterChips({
  properties,
  active,
  onChange,
}: {
  properties: Property[];
  active: StatusFilter;
  onChange: (f: StatusFilter) => void;
}) {
  return (
    <div className="flex gap-1.5 items-center flex-wrap">
      {FILTERS.map(({ id, label }) => {
        const on = active === id;
        const count =
          id === "all"
            ? properties.length
            : properties.filter((p) => p.status === id).length;
        return (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={cn(
              "inline-flex items-center gap-2 rounded-[9px] px-3 py-1.5 text-[12px] font-medium",
              "border cursor-pointer font-sans transition-colors duration-[120ms]",
              on
                ? "bg-graphite text-white border-graphite"
                : "bg-surface text-text-2 border-border hover:border-border-strong",
            )}
          >
            {label}
            <span className="font-mono text-[10px] opacity-80">{count}</span>
          </button>
        );
      })}
    </div>
  );
}

// ─── Portfolio list view ──────────────────────────────────────────────────────

function PortfolioListView({
  portfolios,
  properties,
  onPortfolioClick,
}: {
  portfolios: ApiPortfolio[];
  properties: Property[];
  onPortfolioClick: (portfolioId: string) => void;
}) {
  return (
    <div
      className="grid gap-3"
      style={{
        gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
      }}
    >
      {portfolios.map((pf) => {
        const props = properties.filter((p) => p.portfolio === pf.id);
        const units = props.reduce((s, p) => s + p.units, 0);
        const occ = props.reduce((s, p) => s + p.occupied, 0);
        const alerts = props.reduce((s, p) => s + p.alerts, 0);

        return (
          <div
            key={pf.id}
            onClick={() => onPortfolioClick(pf.id)}
            className="bg-surface-2 border border-border rounded-panel p-[18px] cursor-pointer hover:border-border-strong hover:bg-surface transition-colors"
          >
            <div className="flex items-center gap-3 mb-3.5">
              <div className="w-8 h-8 rounded-[8px] bg-graphite flex items-center justify-center shrink-0">
                <LayoutGrid size={15} strokeWidth={1.5} color="#ffffff" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-serif text-[18px] text-text m-0 truncate">
                  {pf.name}
                </p>
                <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mt-0.5 m-0">
                  {pf.description || "Portfolio"}
                </p>
              </div>
            </div>

            <div className="h-px bg-border my-3.5" />

            <div className="flex flex-col gap-2.5">
              <div className="flex justify-between text-[12px]">
                <span className="text-text-2">Properties</span>
                <span className="font-mono font-semibold text-text">
                  {props.length}
                </span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span className="text-text-2">Units</span>
                <span className="font-mono font-semibold text-text">
                  {units}
                </span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span className="text-text-2">Occupied</span>
                <span className="font-mono font-semibold text-text">
                  {occ}/{units}
                </span>
              </div>
            </div>

            <div className="h-px bg-border my-3.5" />

            <div className="flex items-center justify-between">
              {alerts > 0 ? (
                <Tag variant="warn" withDot>
                  {alerts} alert{alerts > 1 ? "s" : ""}
                </Tag>
              ) : (
                <Tag variant="ok" withDot>
                  All clear
                </Tag>
              )}
              <ChevronRight
                size={16}
                strokeWidth={1.5}
                className="text-text-3"
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Portfolio detail view ────────────────────────────────────────────────────

function PortfolioDetailView({
  portfolio,
  properties: props,
  onBack,
  onPortfolioUpdate,
  onPropertyCreate,
}: {
  portfolio: ApiPortfolio;
  properties: Property[];
  onBack: () => void;
  onPortfolioUpdate: () => Promise<void>;
  onPropertyCreate: () => Promise<void>;
}) {
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [showEditPortfolio, setShowEditPortfolio] = useState(false);
  const [showPropertyForm, setShowPropertyForm] = useState(false);
  const [editingProperty, setEditingProperty] = useState<Property | null>(null);
  const { organization } = useAuth();
  const filtered =
    filter === "all" ? props : props.filter((p) => p.status === filter);

  return (
    <>
      <PageHeader
        eyebrow={portfolio.description?.toUpperCase() || "PORTFOLIO"}
        title={portfolio.name}
        sub={`${props.length} properties · ${props.reduce((s, p) => s + p.units, 0)} units · ${props.reduce((s, p) => s + p.devices, 0)} devices`}
        primary={
          <Button
            variant="primary"
            icon={Plus}
            onClick={() => {
              setEditingProperty(null);
              setShowPropertyForm(true);
            }}
          >
            Add property
          </Button>
        }
        secondary={
          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={() => setShowEditPortfolio(true)}
            >
              Edit
            </Button>
            <Button variant="secondary" icon={Download}>
              Export CSV
            </Button>
          </div>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-[13px] text-text-2 hover:text-text transition-colors"
          >
            <ArrowLeft size={14} strokeWidth={1.5} />
            Back to portfolios
          </button>

          <div className="flex items-center justify-between flex-wrap gap-3 flex-1 justify-end">
            <FilterChips
              properties={props}
              active={filter}
              onChange={setFilter}
            />

            {/* Grid / list toggle */}
            <div className="flex gap-1.5 p-[3px] bg-surface border border-border rounded-[9px]">
              {(["grid", "list"] as const).map((v) => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={cn(
                    "flex items-center gap-1.5 px-2.5 py-1 rounded-[7px] text-[12px] capitalize",
                    "border cursor-pointer font-sans transition-colors duration-[120ms]",
                    view === v
                      ? "bg-bg border-border text-text"
                      : "border-transparent text-text-3 hover:text-text-2",
                  )}
                >
                  {v === "grid" ? (
                    <LayoutGrid size={12} strokeWidth={1.5} />
                  ) : (
                    <List size={12} strokeWidth={1.5} />
                  )}
                  {v}
                </button>
              ))}
            </div>
          </div>
        </div>

        {view === "grid" ? (
          <div
            className="grid gap-3"
            style={{
              gridTemplateColumns: "repeat(auto-fill, minmax(230px, 1fr))",
            }}
          >
            {filtered.map((p) => (
              <PropertyCard key={p.id} {...p} />
            ))}
          </div>
        ) : (
          <DataTable columns={TABLE_COLUMNS} rows={filtered} />
        )}
      </div>

      {showEditPortfolio && (
        <EditPortfolioForm
          initialName={portfolio.name}
          initialDescription={portfolio.description}
          onClose={() => setShowEditPortfolio(false)}
          onSubmit={async (data) => {
            if (!organization?.id) {
              const error = new Error(
                "Organization not loaded. Please refresh the page.",
              );
              logger.error("Organization not loaded", error);
              throw error;
            }
            await updatePortfolio(portfolio.id, data);
            await onPortfolioUpdate();
          }}
        />
      )}

      {showPropertyForm && (
        <PropertyForm
          mode={editingProperty ? "edit" : "create"}
          initialData={editingProperty}
          onClose={() => {
            setShowPropertyForm(false);
            setEditingProperty(null);
          }}
          onSubmit={async (data) => {
            if (!organization?.id) {
              const error = new Error(
                "Organization not loaded. Please refresh the page.",
              );
              logger.error("Organization not loaded", error);
              throw error;
            }

            if (editingProperty) {
              await updateProperty(portfolio.id, editingProperty.id, {
                name: data.name,
                address: data.address,
                property_type: data.type,
                units: data.units,
              });
            } else {
              await createProperty(portfolio.id, {
                organization_id: organization.id,
                portfolio_id: portfolio.id,
                name: data.name,
                address: data.address,
                property_type: data.type,
                units: data.units,
              });
            }

            await onPropertyCreate();
          }}
        />
      )}
    </>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function PortfolioScreen() {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | null>(
    null,
  );
  const [showAddForm, setShowAddForm] = useState(false);
  const [portfolios, setPortfolios] = useState<ApiPortfolio[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const { organization, isLoading: authLoading } = useAuth();
  const totalUnits = properties.reduce((s, p) => s + p.units, 0);
  const totalDevices = properties.reduce((s, p) => s + p.devices, 0);

  const loadPortfolios = useCallback(async () => {
    const organizationId = organization?.id;
    if (!organizationId) return;

    setLoading(true);
    try {
      const data = await listPortfolios(organizationId);
      const perPortfolio = await Promise.all(
        data.map((pf) => listProperties(pf.id, organizationId)),
      );
      setPortfolios(data);
      setProperties(perPortfolio.flat().map(toDisplayProperty));
    } catch (error) {
      console.error("Failed to load portfolios:", error);
    } finally {
      setLoading(false);
    }
  }, [organization?.id]);

  useEffect(() => {
    if (authLoading) return;
    if (!organization?.id) {
      setPortfolios([]);
      setProperties([]);
      setLoading(false);
      return;
    }
    loadPortfolios();
  }, [authLoading, organization?.id, loadPortfolios]);

  async function handleAddPortfolio(data: {
    name: string;
    region: string;
    manager: string;
  }) {
    if (!organization?.id) {
      console.error("Organization not loaded");
      return;
    }

    try {
      await createPortfolio({
        organization_id: organization.id,
        name: data.name,
        description: data.region,
      });

      setShowAddForm(false);
      await loadPortfolios();
    } catch (error) {
      logger.error("Failed to create portfolio:", error);
    }
  }

  const selectedPortfolio =
    portfolios.find((p) => p.id === selectedPortfolioId) ?? null;

  if (selectedPortfolio) {
    return (
      <PortfolioDetailView
        portfolio={selectedPortfolio}
        properties={properties.filter(
          (p) => p.portfolio === selectedPortfolio.id,
        )}
        onBack={() => setSelectedPortfolioId(null)}
        onPortfolioUpdate={loadPortfolios}
        onPropertyCreate={loadPortfolios}
      />
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Portfolios"
        sub={`${portfolios.length} portfolios · ${properties.length} properties · ${totalUnits} units · ${totalDevices} devices`}
        primary={
          <Button
            variant="primary"
            icon={Plus}
            onClick={() => setShowAddForm(true)}
          >
            Add portfolio
          </Button>
        }
        secondary={
          <Button variant="secondary" icon={Download}>
            Export CSV
          </Button>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        {loading ? (
          <div
            className="grid gap-3"
            style={{
              gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
            }}
          >
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                aria-hidden
                className="bg-surface-2 border border-border rounded-panel h-[208px] animate-pulse"
              />
            ))}
          </div>
        ) : portfolios.length === 0 ? (
          <div className="border border-border rounded-panel p-12 text-center">
            <p className="text-[16px] text-text font-serif m-0">
              No portfolios yet
            </p>
            <p className="text-[14px] text-text-2 mt-2 m-0">
              Create your first portfolio to start managing your properties and
              integrations.
            </p>
          </div>
        ) : (
          <PortfolioListView
            portfolios={portfolios}
            properties={properties}
            onPortfolioClick={setSelectedPortfolioId}
          />
        )}
      </div>

      {showAddForm && (
        <AddPortfolioForm
          onClose={() => setShowAddForm(false)}
          onSubmit={handleAddPortfolio}
        />
      )}
    </>
  );
}
