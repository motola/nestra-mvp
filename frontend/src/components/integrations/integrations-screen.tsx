"use client";

import {
  Plus,
  Plug,
  CheckCircle,
  AlertCircle,
  Trash2,
  RefreshCw,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyDataState } from "@/components/ui/empty-state";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";

// ─── Type definitions ────────────────────────────────────────────────────────

interface Vendor {
  id: string;
  name: string;
  icon: LucideIcon;
  color: string;
  description: string;
}

interface ConnectedIntegration {
  id: string;
  vendor: Vendor;
  status: "connected" | "needs_auth" | "error";
  lastSync: string;
  deviceCount: number;
  connectedAt: string;
}

// ─── Available vendors ─────────────────────────────────────────────────────────

const AVAILABLE_VENDORS: Vendor[] = [
  {
    id: "google",
    name: "Google Home",
    icon: Plus,
    color: "text-blue-500",
    description: "Connect Google Home devices and get real-time updates",
  },
  {
    id: "microsoft",
    name: "Microsoft",
    icon: Plus,
    color: "text-blue-600",
    description: "Integrate Cortana and Azure IoT devices",
  },
  {
    id: "august",
    name: "August Smart Lock",
    icon: Plug,
    color: "text-amber-600",
    description: "Manage August smart locks and access",
  },
  {
    id: "philips-hue",
    name: "Philips Hue",
    icon: Plus,
    color: "text-amber-400",
    description: "Control Philips Hue lights and color scenes",
  },
  {
    id: "apple",
    name: "Apple HomeKit",
    icon: Plus,
    color: "text-gray-700",
    description: "Sync HomeKit devices and automations",
  },
  {
    id: "amazon",
    name: "Amazon Alexa",
    icon: Plus,
    color: "text-blue-400",
    description: "Connect Alexa devices and smart home skills",
  },
];

// ─── Mock connected integrations ──────────────────────────────────────────────

const MOCK_CONNECTED: ConnectedIntegration[] = [
  {
    id: "int-1",
    vendor: AVAILABLE_VENDORS[0],
    status: "connected",
    lastSync: "2 minutes ago",
    deviceCount: 12,
    connectedAt: "Aug 15, 2026",
  },
  {
    id: "int-2",
    vendor: AVAILABLE_VENDORS[2],
    status: "connected",
    lastSync: "5 minutes ago",
    deviceCount: 3,
    connectedAt: "Aug 10, 2026",
  },
];

// ─── Status badge ─────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const variants: Record<
    string,
    { bg: string; text: string; icon: LucideIcon }
  > = {
    connected: {
      bg: "bg-green-50",
      text: "text-green-700",
      icon: CheckCircle,
    },
    needs_auth: {
      bg: "bg-amber-50",
      text: "text-amber-700",
      icon: AlertCircle,
    },
    error: {
      bg: "bg-red-50",
      text: "text-red-700",
      icon: AlertCircle,
    },
  };

  const variant = variants[status] || variants.error;
  const Icon = variant.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-[6px]",
        variant.bg,
      )}
    >
      <Icon size={14} className={variant.text} strokeWidth={2} />
      <span className={cn("text-[12px] font-medium", variant.text)}>
        {status === "connected"
          ? "Connected"
          : status === "needs_auth"
            ? "Needs Auth"
            : "Error"}
      </span>
    </div>
  );
}

// ─── Connected integration card ──────────────────────────────────────────────

function ConnectedCard({ integration }: { integration: ConnectedIntegration }) {
  return (
    <Card className="p-4 flex items-start justify-between">
      <div className="flex items-start gap-3.5 flex-1">
        <div className="w-10 h-10 rounded-[8px] bg-surface-2 flex items-center justify-center shrink-0">
          <Plug size={18} strokeWidth={1.5} className="text-text-2" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-[14px] font-semibold text-text m-0">
              {integration.vendor.name}
            </p>
            <StatusBadge status={integration.status} />
          </div>
          <p className="text-[12px] text-text-3 m-0 mb-2">
            Connected {integration.connectedAt}
          </p>
          <div className="flex gap-4">
            <div>
              <MonoLabel className="text-text-3">Last sync</MonoLabel>
              <p className="text-[12px] text-text m-0">
                {integration.lastSync}
              </p>
            </div>
            <div>
              <MonoLabel className="text-text-3">Devices</MonoLabel>
              <p className="text-[12px] text-text m-0">
                {integration.deviceCount} synced
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        {integration.status === "needs_auth" ? (
          <Button variant="secondary" size="sm" icon={RefreshCw}>
            Re-auth
          </Button>
        ) : (
          <>
            <Button
              variant="ghost"
              size="sm"
              icon={RefreshCw}
              title="Re-sync now"
            />
            <Button
              variant="ghost"
              size="sm"
              icon={Trash2}
              className="text-red hover:text-red"
              title="Disconnect"
            />
          </>
        )}
      </div>
    </Card>
  );
}

// ─── Vendor grid ────────────────────────────────────────────────────────────────

function VendorGrid({
  vendors,
  connectedIds,
  onConnect,
}: {
  vendors: Vendor[];
  connectedIds: string[];
  onConnect: (vendor: Vendor) => void;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {vendors.map((vendor) => {
        const isConnected = connectedIds.includes(vendor.id);
        return (
          <Card
            key={vendor.id}
            className={cn(
              "p-4 cursor-pointer transition-all",
              isConnected ? "opacity-60" : "hover:bg-surface-2",
            )}
          >
            <div className="flex items-start gap-3 mb-3">
              <div className="w-8 h-8 rounded-[6px] bg-surface-2 flex items-center justify-center shrink-0">
                <Plug size={16} strokeWidth={1.5} className="text-text-2" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[13px] font-semibold text-text m-0">
                  {vendor.name}
                </p>
              </div>
              {isConnected && (
                <CheckCircle
                  size={16}
                  className="text-green shrink-0"
                  fill="currentColor"
                />
              )}
            </div>
            <p className="text-[12px] text-text-2 mb-3 m-0 leading-[1.4]">
              {vendor.description}
            </p>
            <Button
              variant="secondary"
              size="sm"
              className="w-full"
              disabled={isConnected}
              onClick={() => onConnect(vendor)}
            >
              {isConnected ? "Connected" : "Connect"}
            </Button>
          </Card>
        );
      })}
    </div>
  );
}

// ─── Main export ─────────────────────────────────────────────────────────────

export function IntegrationsScreen() {
  const connected = MOCK_CONNECTED;

  const connectedIds = connected.map((c) => c.vendor.id);
  const unconnectedVendors = AVAILABLE_VENDORS.filter(
    (v) => !connectedIds.includes(v.id),
  );

  const handleConnect = (vendor: Vendor) => {
    console.log("Connecting to:", vendor.name);
    // TODO: Initiate OAuth flow
  };

  const showEmpty = connected.length === 0;

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Integrations"
        sub={`${connected.length} connection${connected.length !== 1 ? "s" : ""}`}
        primary={
          <Button variant="primary" icon={Plus}>
            Connect vendor
          </Button>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-8">
        {showEmpty ? (
          <EmptyDataState
            title="No integrations connected"
            description="Connect your first smart home vendor to start syncing devices."
          />
        ) : (
          <>
            {/* Connected integrations */}
            <div>
              <SectionHead
                title="Connected integrations"
                sub={`${connected.length} ACTIVE CONNECTION${connected.length !== 1 ? "S" : ""}`}
              />
              <div className="space-y-3 mt-4">
                {connected.map((integration) => (
                  <ConnectedCard
                    key={integration.id}
                    integration={integration}
                  />
                ))}
              </div>
            </div>
          </>
        )}

        {/* Available vendors */}
        <div>
          <SectionHead
            title={showEmpty ? "Available vendors" : "Add more integrations"}
            sub={`${unconnectedVendors.length} VENDOR${unconnectedVendors.length !== 1 ? "S" : ""} AVAILABLE`}
          />
          <div className="mt-4">
            <VendorGrid
              vendors={unconnectedVendors}
              connectedIds={connectedIds}
              onConnect={handleConnect}
            />
          </div>
        </div>

        {/* Info card */}
        <Card className="p-[18px] flex items-start gap-3.5 bg-blue-50 border-blue-200">
          <div className="w-9 h-9 rounded-[8px] bg-blue-100 flex items-center justify-center shrink-0">
            <Plug size={16} strokeWidth={1.5} color="#2563eb" />
          </div>
          <div className="flex-1">
            <p className="text-[13px] font-semibold text-blue-900 m-0">
              OAuth-secured integrations
            </p>
            <p className="text-[12px] text-blue-800 mt-1 leading-[1.6] m-0 max-w-[720px]">
              All integrations use OAuth 2.0 for secure authentication. Your
              credentials are encrypted and never stored in plain text. Each
              vendor integration can be revoked independently at any time.
            </p>
          </div>
        </Card>
      </div>
    </>
  );
}
