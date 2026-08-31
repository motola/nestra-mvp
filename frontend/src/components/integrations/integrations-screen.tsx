"use client"; // Client: tab switching

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Plus, BookOpen, X } from "lucide-react";
import { cn } from "@/lib/cn";
import { INTEGRATIONS, VENDORS } from "@/lib/fixtures";
import type { Integration, Vendor } from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Tabs } from "@/components/ui/tabs";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";
import { AlertCard } from "@/components/ui/alert-card";
import { VendorLogo } from "@/components/integrations/vendor-logos";
import { useProperty } from "@/lib/property/provider";
import type { PropertyType } from "@/lib/fixtures";
import { BluetoothDiscoveryModal } from "@/components/integrations/bluetooth-discovery-modal";
import { WiFiDiscoveryModal } from "@/components/integrations/wifi-discovery-modal";
import { OAuthTokenModal } from "@/components/integrations/oauth-token-modal";
import { useAuth } from "@/lib/auth/provider";
import { getToken } from "@/lib/auth/session";
import { listPortfolios, listProperties } from "@/lib/api/portfolios";
import type { Property as ApiProperty } from "@/lib/api/portfolios";
import { logger } from "@/lib/logger";

// ─── Connected tab ────────────────────────────────────────────────────────────

function IntegrationCard({ item: i }: { item: Integration }) {
  return (
    <Card hoverable className="p-[18px]">
      <div className="flex items-center gap-3.5">
        <VendorLogo name={i.vendor} size={48} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2.5">
            <span className="font-serif text-[18px] text-text">{i.vendor}</span>
            {i.status === "ACTIVE" ? (
              <Tag variant="ok" withDot>
                active
              </Tag>
            ) : (
              <Tag variant="warn" withDot>
                token expired
              </Tag>
            )}
          </div>
          <MonoLabel className="mt-1 block">property · {i.ownerName}</MonoLabel>
        </div>
        <Button variant={i.needsReauth ? "primary" : "ghost"} size="sm">
          {i.needsReauth ? "Reauthorize" : "Manage"}
        </Button>
      </div>

      <div className="h-px bg-border my-3.5" />

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "devices", value: String(i.devices), mono: true },
          { label: "last sync", value: i.lastSync, mono: false },
          { label: "connected", value: i.connectedAt, mono: true },
        ].map(({ label, value, mono }) => (
          <div key={label}>
            <MonoLabel>{label}</MonoLabel>
            <p
              className={cn(
                "mt-1 m-0",
                mono
                  ? "font-mono text-[18px] font-semibold text-text"
                  : "text-[13px] text-text",
              )}
            >
              {value}
            </p>
          </div>
        ))}
      </div>

      <div className="flex gap-1.5 mt-3.5 flex-wrap">
        {i.scopes.map((s) => (
          <Tag key={s} variant="neutral">
            {s}
          </Tag>
        ))}
      </div>
    </Card>
  );
}

function ConnectedTab({ integrations }: { integrations: Integration[] }) {
  const reauth = integrations.find((i) => i.needsReauth);
  return (
    <>
      {reauth && (
        <AlertCard
          severity="amber"
          title={`${reauth.vendor} token expired`}
          desc={`Your ${reauth.vendor} access token expired. Reconnect to restore — your scopes will carry over.`}
          meta={`Integration · ${reauth.ownerName} · Today 03:14`}
          actions={["Reauthorize", "Open integration"]}
        />
      )}
      <SectionHead
        title="Connected vendors"
        sub={`${integrations.length} INTEGRATIONS`}
      />
      {integrations.length === 0 ? (
        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">
            No connections yet
          </p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            Browse the Catalog to connect your first vendor and start syncing
            devices.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {integrations.map((i) => (
            <IntegrationCard key={i.id} item={i} />
          ))}
        </div>
      )}
    </>
  );
}

// ─── Catalog tab ──────────────────────────────────────────────────────────────

const CATALOG_CATS = [
  "All vendors",
  "Thermostats",
  "Lights",
  "Locks",
  "Sensors",
  "Plugs & meters",
  "Hubs & bridges",
];

function VendorCard({
  v,
  onDeviceAdded,
}: {
  v: Vendor;
  onDeviceAdded?: () => void;
}) {
  const { selectedProperty } = useProperty();
  const { organization } = useAuth();
  const [bluetoothModalOpen, setBluetoothModalOpen] = useState(false);
  const [wifiModalOpen, setWifiModalOpen] = useState(false);
  const [oauthTokenModalOpen, setOauthTokenModalOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleConnect = async () => {
    // Check if property is selected first
    if (!selectedProperty?.id) {
      setMessage("Error: Please select a property first");
      return;
    }

    const vendor = v.name.toLowerCase();

    // For OAuth vendors, show the OAuth/Token selection modal
    if (["lifx", "govee", "meross", "shelly"].includes(vendor)) {
      setOauthTokenModalOpen(true);
      return;
    }

    // For Bluetooth discovery
    if (vendor === "bluetooth") {
      setBluetoothModalOpen(true);
      return;
    }

    // For WiFi discovery
    if (vendor === "wifi") {
      setWifiModalOpen(true);
      return;
    }

    logger.warn(`No implementation for ${vendor}`);
  };

  const handleOAuthClick = () => {
    const vendor = v.name.toLowerCase();
    const oauthUrls: Record<string, string> = {
      lifx: `https://api.lifx.com/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_LIFX_CLIENT_ID}&response_type=code&scope=remote_access:all&redirect_uri=${window.location.origin}/auth/lifx/callback`,
      govee: `https://community.govee.com/login?client_id=${process.env.NEXT_PUBLIC_GOVEE_CLIENT_ID}&response_type=code&redirect_uri=${window.location.origin}/auth/govee/callback`,
      meross: `https://iot.meross.com/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_MEROSS_CLIENT_ID}&response_type=code&redirect_uri=${window.location.origin}/auth/meross/callback`,
      shelly: `https://my.shelly.cloud/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_SHELLY_CLIENT_ID}&response_type=code&redirect_uri=${window.location.origin}/auth/shelly/callback`,
    };

    if (oauthUrls[vendor]) {
      window.location.href = oauthUrls[vendor];
    }
  };

  const handleTokenSubmit = async (token: string) => {
    const vendor = v.name.toLowerCase();

    if (!selectedProperty?.id || !organization?.id) {
      setMessage("Error: No property or organization selected");
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const authToken = getToken();

      // For Shelly, create integration then device
      if (vendor === "shelly") {
        // Create integration
        const integrationRes = await fetch(`${apiUrl}/integrations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            organization_id: organization.id,
            provider_id: "shelly",
            connection_identifier: "shelly_cloud",
            display_name: "Shelly Cloud",
            config: { api_token: token },
          }),
        });

        if (!integrationRes.ok)
          throw new Error(
            `Integration creation failed: ${integrationRes.status}`,
          );
        const integration = await integrationRes.json();

        // Create device under integration
        const deviceRes = await fetch(
          `${apiUrl}/integrations/${integration.id}/devices/shelly`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify({
              property_id: selectedProperty.id,
              name: "Shelly Device",
              device_id: "shelly_device",
              ip_address: "0.0.0.0",
            }),
          },
        );

        if (!deviceRes.ok)
          throw new Error(`Device creation failed: ${deviceRes.status}`);
        await deviceRes.json();

        setMessage(`Connected to ${vendor} - Device ready to control`);
        setOauthTokenModalOpen(false);
        setTimeout(() => setMessage(null), 3000);
      } else if (vendor === "govee") {
        // For Govee, create integration
        const integrationRes = await fetch(`${apiUrl}/integrations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            organization_id: organization.id,
            provider_id: "govee",
            connection_identifier: token,
            display_name: "Govee",
            config: { api_key: token },
          }),
        });

        if (!integrationRes.ok)
          throw new Error(
            `Integration creation failed: ${integrationRes.status}`,
          );

        setMessage(`Connected to ${vendor} - Ready to control`);
        setOauthTokenModalOpen(false);
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Connection failed";
      setMessage(`Error: ${errMsg}`);
      logger.error("Device connection error:", err);
    }
  };

  const handleBluetoothDevices = async (
    devices: Array<{
      id: string;
      name: string;
      rssi: number;
      services: string[];
    }>,
  ) => {
    if (!selectedProperty?.id || !organization?.id) {
      setMessage("Error: No property or organization selected");
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const authToken = getToken();

      // Create or get Bluetooth integration
      let integrationId: string;

      // Try to find existing Bluetooth integration
      const listRes = await fetch(
        `${apiUrl}/integrations?organization_id=${organization.id}`,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        },
      );

      if (listRes.ok) {
        const integrations = await listRes.json();
        const btIntegration = integrations.find(
          (i: { provider_id: string }) => i.provider_id === "bluetooth",
        );

        if (btIntegration) {
          integrationId = btIntegration.id;
        } else {
          // Create new Bluetooth integration
          const createRes = await fetch(`${apiUrl}/integrations`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify({
              organization_id: organization.id,
              provider_id: "bluetooth",
              connection_identifier: "local",
              display_name: "Local Bluetooth",
            }),
          });

          if (!createRes.ok)
            throw new Error(`Integration creation failed: ${createRes.status}`);
          const integration = await createRes.json();
          integrationId = integration.id;
        }
      } else {
        throw new Error("Failed to list integrations");
      }

      // Create devices under the integration (handle individual failures)
      const results = await Promise.allSettled(
        devices.map((device) =>
          fetch(`${apiUrl}/integrations/${integrationId}/devices/bluetooth`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${authToken}`,
            },
            body: JSON.stringify({
              property_id: selectedProperty.id,
              name: device.name,
              mac_address: device.id,
            }),
          })
            .then((r) => {
              if (!r.ok) throw new Error(`HTTP ${r.status}`);
              return r.json();
            })
            .then((data) => {
              logger.info("Bluetooth device created:", data);
              return data;
            }),
        ),
      );

      const successCount = results.filter(
        (r) => r.status === "fulfilled",
      ).length;
      const failureCount = results.filter(
        (r) => r.status === "rejected",
      ).length;

      if (successCount === 0) {
        const firstError =
          results.find((r) => r.status === "rejected")?.reason?.message ||
          "Failed to create devices";
        throw new Error(firstError);
      }

      setMessage(
        `Added Bluetooth integration successfully · ${successCount} device(s)${failureCount > 0 ? ` (${failureCount} failed)` : ""}`,
      );
      setBluetoothModalOpen(false);
      onDeviceAdded?.();
      setTimeout(() => setMessage(null), 4000);
    } catch (err) {
      const errMsg =
        err instanceof Error ? err.message : "Failed to create devices";
      setMessage(`Error: ${errMsg}`);
      logger.error("Bluetooth device creation error:", err);
    }
  };

  const handleWifiNetworks = async (
    networks: Array<{
      ssid: string;
      bssid: string;
      signal_strength: number;
      channel: number;
      security: string;
    }>,
  ) => {
    if (!selectedProperty?.id) {
      setMessage("Error: No property selected");
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/wifi/devices/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          organization_id: organization?.id,
          property_id: selectedProperty.id,
          networks,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create devices: HTTP ${response.status}`);
      }

      const devices = await response.json();
      setMessage(`Successfully created ${devices.length} WiFi devices`);
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      const errMsg =
        err instanceof Error ? err.message : "Failed to create devices";
      setMessage(`Error: ${errMsg}`);
      logger.error("WiFi device creation error:", err);
    }
  };

  return (
    <>
      <Card hoverable className="p-[18px] flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <VendorLogo name={v.name} size={36} />
          <div className="flex-1">
            <p className="text-[14px] font-semibold text-text m-0">{v.name}</p>
            <p className="text-[12px] text-text-3 mt-0.5 m-0">{v.cats}</p>
          </div>
          {v.connected && (
            <Tag variant="ok" withDot>
              connected
            </Tag>
          )}
        </div>
        <div className="h-px bg-border" />
        <div className="flex justify-between items-center">
          <MonoLabel>{v.connected ? "manage" : "set up oauth"}</MonoLabel>
          <Button
            variant={v.connected ? "secondary" : "primary"}
            size="sm"
            onClick={v.connected ? undefined : handleConnect}
          >
            {v.connected ? "Manage" : "Connect"}
          </Button>
        </div>
      </Card>

      {message && (
        <div
          className={`fixed bottom-4 left-4 p-4 rounded-lg text-sm font-medium ${
            message.startsWith("Error")
              ? "bg-red-100 text-red-700"
              : "bg-green-100 text-green-700"
          }`}
        >
          {message}
        </div>
      )}

      <OAuthTokenModal
        isOpen={oauthTokenModalOpen}
        vendor={v.name}
        onClose={() => setOauthTokenModalOpen(false)}
        onOAuth={handleOAuthClick}
        onTokenSubmit={handleTokenSubmit}
      />

      <BluetoothDiscoveryModal
        isOpen={bluetoothModalOpen}
        onClose={() => setBluetoothModalOpen(false)}
        onDevicesSelected={handleBluetoothDevices}
      />

      <WiFiDiscoveryModal
        isOpen={wifiModalOpen}
        onClose={() => setWifiModalOpen(false)}
        onNetworksSelected={handleWifiNetworks}
      />
    </>
  );
}

function CatalogTab({ onDeviceAdded }: { onDeviceAdded?: () => void }) {
  const [cat, setCat] = useState("All vendors");

  const filteredVendors =
    cat === "All vendors"
      ? VENDORS
      : VENDORS.filter((v) => v.cats.toLowerCase().includes(cat.toLowerCase()));

  return (
    <>
      <div className="flex gap-1.5 flex-wrap">
        {CATALOG_CATS.map((c) => (
          <button
            key={c}
            onClick={() => setCat(c)}
            className="border-0 p-0 bg-transparent cursor-pointer"
          >
            <Tag variant={cat === c ? "graphite" : "neutral"}>{c}</Tag>
          </button>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-3">
        {filteredVendors.length > 0 ? (
          filteredVendors.map((v) => (
            <VendorCard key={v.id} v={v} onDeviceAdded={onDeviceAdded} />
          ))
        ) : (
          <div className="col-span-3 border border-border rounded-panel p-12 text-center">
            <p className="text-[16px] text-text font-serif m-0">
              No vendors in this category
            </p>
            <p className="text-[14px] text-text-2 mt-2 m-0">
              Try selecting a different category or view all vendors.
            </p>
          </div>
        )}
      </div>
    </>
  );
}

// ─── Webhooks tab ─────────────────────────────────────────────────────────────

type WebhookRow = {
  vendor: string;
  topic: string;
  events: string;
  last: string;
  status: string;
};

const WEBHOOK_ROWS: WebhookRow[] = [];

const WEBHOOK_COLS: TableColumn<WebhookRow>[] = [
  {
    k: "vendor",
    label: "Vendor",
    w: "1fr",
    render: (r) => <span className="font-medium">{r.vendor}</span>,
  },
  {
    k: "topic",
    label: "Topic",
    w: "1.4fr",
    render: (r) => (
      <span className="font-mono text-[12px] text-text-2">{r.topic}</span>
    ),
  },
  {
    k: "events",
    label: "Events · 24h",
    w: "1fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">{r.events}</span>
    ),
  },
  {
    k: "last",
    label: "Last received",
    w: "1fr",
    render: (r) => <MonoLabel>{r.last}</MonoLabel>,
  },
  {
    k: "status",
    label: "Status",
    w: "0.8fr",
    render: (r) => (
      <Tag variant={r.status === "active" ? "ok" : "alert"} withDot>
        {r.status}
      </Tag>
    ),
  },
  {
    k: "act",
    label: "",
    w: "70px",
    align: "right",
    render: () => (
      <Button variant="ghost" size="sm">
        Rotate
      </Button>
    ),
  },
];

function WebhooksTab() {
  return (
    <>
      <SectionHead
        title="Webhook subscriptions"
        sub="VENDOR → ALPHACON · INCOMING EVENTS"
      />
      {WEBHOOK_ROWS.length === 0 ? (
        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">
            No webhooks configured
          </p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            When you connect vendors, their webhook subscriptions will appear
            here for monitoring.
          </p>
        </div>
      ) : (
        <DataTable columns={WEBHOOK_COLS} rows={WEBHOOK_ROWS} />
      )}
    </>
  );
}

// ─── Errors tab ───────────────────────────────────────────────────────────────

type ErrorRow = {
  time: string;
  vendor: string;
  code: string;
  message: string;
  retriable: boolean;
  userVisible: boolean;
};

const ERROR_ROWS: ErrorRow[] = [];

const ERROR_COLS: TableColumn<ErrorRow>[] = [
  {
    k: "time",
    label: "Time",
    w: "120px",
    render: (r) => <MonoLabel>{r.time}</MonoLabel>,
  },
  { k: "vendor", label: "Vendor", w: "1fr" },
  {
    k: "code",
    label: "Error",
    w: "1fr",
    render: (r) => (
      <span className="font-mono text-[12px] font-medium text-red">
        {r.code}
      </span>
    ),
  },
  {
    k: "message",
    label: "Message",
    w: "2.5fr",
    wrap: true,
    render: (r) => <span className="text-[12px] text-text-2">{r.message}</span>,
  },
  {
    k: "flags",
    label: "Flags",
    w: "1.2fr",
    render: (r) => (
      <div className="flex gap-1">
        {r.retriable && <Tag variant="neutral">retriable</Tag>}
        {r.userVisible && <Tag variant="warn">user-visible</Tag>}
      </div>
    ),
  },
];

function ErrorsTab() {
  return (
    <>
      <SectionHead
        title="Adapter errors"
        sub="LAST 7 DAYS · CLASSIFIED BY ADAPTERROR HIERARCHY"
      />
      {ERROR_ROWS.length === 0 ? (
        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">No errors</p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            All integrations are running smoothly. Errors from the past 7 days
            would appear here.
          </p>
        </div>
      ) : (
        <DataTable columns={ERROR_COLS} rows={ERROR_ROWS} />
      )}
    </>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function IntegrationsScreen() {
  const searchParams = useSearchParams();
  const [tab, setTab] = useState(searchParams?.get("tab") || "connected");
  const { selectedProperty, selectProperty } = useProperty();
  const { organization } = useAuth();
  const [apiProperties, setApiProperties] = useState<ApiProperty[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>(INTEGRATIONS);
  const [loading, setLoading] = useState(false);
  const [showDeviceTypeModal, setShowDeviceTypeModal] = useState(false);
  const [bluetoothModalOpen, setBluetoothModalOpen] = useState(false);
  const [wifiModalOpen, setWifiModalOpen] = useState(false);

  const loadProperties = useCallback(async () => {
    const organizationId = organization?.id;
    if (!organizationId) return;

    setLoading(true);
    try {
      const portfolios = await listPortfolios(organizationId);
      const allProperties = await Promise.all(
        portfolios.map((pf) => listProperties(pf.id, organizationId)),
      );
      setApiProperties(allProperties.flat());

      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(
          `${apiUrl}/integrations?organization_id=${organizationId}`,
          {
            headers: {
              Authorization: `Bearer ${getToken()}`,
            },
          },
        );
        if (response.ok) {
          const data = await response.json();
          setIntegrations(data.length > 0 ? data : INTEGRATIONS);
        }
      } catch (error) {
        logger.warn("Failed to load integrations, using fixtures:", error);
      }
    } catch (error) {
      logger.error("Failed to load properties:", error);
    } finally {
      setLoading(false);
    }
  }, [organization?.id]);

  useEffect(() => {
    loadProperties();
  }, [loadProperties]);

  // Use all integrations if no property selected (for demo), or filter by property
  const propertyIntegrations = selectedProperty
    ? integrations.filter((i) => i.ownerName === selectedProperty.name)
    : integrations;

  const active = propertyIntegrations.filter(
    (i) => i.status === "ACTIVE",
  ).length;
  const needsReauth = propertyIntegrations.filter((i) => i.needsReauth).length;

  return (
    <>
      <PageHeader
        eyebrow={selectedProperty?.name.toUpperCase() || "WORKSPACE"}
        title="Integrations"
        sub={`${propertyIntegrations.length} connections · ${active} active ${needsReauth ? `· ${needsReauth} needs reauth` : ""}`}
        primary={
          <Button variant="primary" icon={Plus}>
            Connect vendor
          </Button>
        }
        secondary={
          <Button variant="secondary" icon={BookOpen}>
            View adapter docs
          </Button>
        }
      />

      <div className="px-7 py-4 bg-surface border-b border-border">
        <label className="flex items-center gap-3">
          <span className="text-sm font-medium text-text">
            Select property:
          </span>
          <select
            value={selectedProperty?.id || ""}
            onChange={(e) => {
              const apiProp = apiProperties.find(
                (p) => p.id === e.target.value,
              );
              if (apiProp) {
                const PROPERTY_TYPES: PropertyType[] = [
                  "MIXED_USE",
                  "SHORT_TERM_RENTAL",
                  "LONG_TERM_RENTAL",
                  "OWNER_OCCUPIED",
                  "COMMERCIAL",
                ];
                const propertyType = PROPERTY_TYPES.includes(
                  apiProp.property_type as PropertyType,
                )
                  ? (apiProp.property_type as PropertyType)
                  : "MIXED_USE";

                selectProperty({
                  id: apiProp.id,
                  portfolio: apiProp.portfolio_id,
                  name: apiProp.name,
                  address: apiProp.address,
                  type: propertyType,
                  tz: apiProp.timezone,
                  units: apiProp.units,
                  occupied: 0,
                  alerts: 0,
                  status: "ok",
                  devices: 0,
                  integrations: 0,
                });
              }
            }}
            className="px-3 py-2 border border-border rounded-lg bg-surface text-text text-sm"
            disabled={loading}
          >
            <option value="">
              {loading ? "Loading..." : "-- Select a property --"}
            </option>
            {apiProperties.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="px-7 border-b border-border bg-surface">
        <Tabs
          value={tab}
          onChange={setTab}
          tabs={[
            {
              id: "connected",
              label: "Connected",
              count: propertyIntegrations.length,
            },
            { id: "catalog", label: "Catalog", count: VENDORS.length },
            { id: "webhooks", label: "Webhooks", count: WEBHOOK_ROWS.length },
            { id: "errors", label: "Errors", count: ERROR_ROWS.length },
          ]}
        />
      </div>

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        {tab === "connected" && (
          <ConnectedTab integrations={propertyIntegrations} />
        )}
        {tab === "catalog" && <CatalogTab onDeviceAdded={loadProperties} />}
        {tab === "webhooks" && <WebhooksTab />}
        {tab === "errors" && <ErrorsTab />}
      </div>

      {showDeviceTypeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-bg rounded-lg shadow-lg w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[16px] font-semibold text-text m-0">
                Connect Device
              </h2>
              <button
                onClick={() => setShowDeviceTypeModal(false)}
                className="p-1 hover:bg-surface rounded-lg border-0 cursor-pointer bg-transparent"
              >
                <X size={20} className="text-text-2" />
              </button>
            </div>
            <p className="text-[13px] text-text-2 mb-4">
              Select the type of device you want to connect
            </p>
            <div className="space-y-2">
              <Button
                variant="secondary"
                className="w-full justify-start"
                onClick={() => {
                  setBluetoothModalOpen(true);
                  setShowDeviceTypeModal(false);
                }}
              >
                Bluetooth Device
              </Button>
              <Button
                variant="secondary"
                className="w-full justify-start"
                onClick={() => {
                  setWifiModalOpen(true);
                  setShowDeviceTypeModal(false);
                }}
              >
                WiFi Network
              </Button>
            </div>
          </div>
        </div>
      )}

      <BluetoothDiscoveryModal
        isOpen={bluetoothModalOpen}
        onClose={() => setBluetoothModalOpen(false)}
        onDevicesSelected={async (devices) => {
          if (!selectedProperty?.id || !organization?.id) {
            logger.error("No property or organization selected");
            return;
          }

          try {
            const apiUrl =
              process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const authToken = getToken();

            let integrationId: string;
            const listRes = await fetch(
              `${apiUrl}/integrations?organization_id=${organization.id}`,
              {
                headers: {
                  Authorization: `Bearer ${authToken}`,
                },
              },
            );

            if (listRes.ok) {
              const integrations = await listRes.json();
              const btIntegration = integrations.find(
                (i: { provider_id: string }) => i.provider_id === "bluetooth",
              );

              if (btIntegration) {
                integrationId = btIntegration.id;
              } else {
                const createRes = await fetch(`${apiUrl}/integrations`, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${authToken}`,
                  },
                  body: JSON.stringify({
                    organization_id: organization.id,
                    provider_id: "bluetooth",
                    connection_identifier: "local",
                    display_name: "Local Bluetooth",
                  }),
                });

                if (!createRes.ok)
                  throw new Error(
                    `Integration creation failed: ${createRes.status}`,
                  );
                const integration = await createRes.json();
                integrationId = integration.id;
              }
            } else {
              throw new Error("Failed to list integrations");
            }

            const results = await Promise.allSettled(
              devices.map((device) =>
                fetch(
                  `${apiUrl}/integrations/${integrationId}/devices/bluetooth`,
                  {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                      Authorization: `Bearer ${authToken}`,
                    },
                    body: JSON.stringify({
                      property_id: selectedProperty.id,
                      name: device.name,
                      mac_address: device.id,
                    }),
                  },
                )
                  .then((r) => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                  })
                  .then((data) => {
                    logger.info("Bluetooth device created:", data);
                    return data;
                  }),
              ),
            );

            const successCount = results.filter(
              (r) => r.status === "fulfilled",
            ).length;
            const failureCount = results.filter(
              (r) => r.status === "rejected",
            ).length;

            if (successCount > 0) {
              logger.info(
                `Successfully created ${successCount} Bluetooth device(s)${failureCount > 0 ? ` (${failureCount} failed)` : ""}`,
              );
            } else {
              throw new Error("Failed to create any Bluetooth devices");
            }
          } catch (err) {
            logger.error("Bluetooth device creation error:", err);
          }
        }}
      />

      <WiFiDiscoveryModal
        isOpen={wifiModalOpen}
        onClose={() => setWifiModalOpen(false)}
        onNetworksSelected={async (networks) => {
          if (!selectedProperty?.id) {
            logger.error("No property selected");
            return;
          }

          try {
            const apiUrl =
              process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const response = await fetch(`${apiUrl}/wifi/devices/create`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify({
                organization_id: organization?.id,
                property_id: selectedProperty.id,
                networks,
              }),
            });

            if (!response.ok) {
              throw new Error(
                `Failed to create devices: HTTP ${response.status}`,
              );
            }

            const devices = await response.json();
            logger.info(`Successfully created ${devices.length} WiFi devices`);
          } catch (err) {
            logger.error("WiFi device creation error:", err);
          }
        }}
      />
    </>
  );
}
