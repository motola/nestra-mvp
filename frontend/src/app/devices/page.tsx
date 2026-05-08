"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { motion } from "framer-motion";
import { devicesApi } from "@/lib/api";
import type { AlphaconDevice, DeviceType, VendorName } from "@/lib/types";
import { PageWrapper, DeviceCard, SkeletonCard, EmptyState } from "@/themes";
import { cn } from "@/lib/utils";

const TYPE_FILTERS: { label: string; value: DeviceType | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Lights", value: "light" },
  { label: "Plugs", value: "plug" },
  { label: "Sensors", value: "sensor" },
  { label: "Locks", value: "lock" },
];

const VENDOR_FILTERS: { label: string; value: VendorName | "all" }[] = [
  { label: "All Vendors", value: "all" },
  { label: "Govee", value: "govee" },
  { label: "Shelly", value: "shelly" },
  { label: "LIFX", value: "lifx" },
  { label: "Demo", value: "demo" },
];

function StatPill({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-4">
      <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-1">{label}</p>
      <p className="font-mono text-2xl text-text">{value}</p>
      {sub && <p className="font-mono text-xs text-text-3 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function DevicesPage() {
  const { data: devices = [], isLoading } = useQuery<AlphaconDevice[]>({
    queryKey: ["devices"],
    queryFn: devicesApi.list,
  });

  const [typeFilter, setTypeFilter] = useState<DeviceType | "all">("all");
  const [vendorFilter, setVendorFilter] = useState<VendorName | "all">("all");
  const [search, setSearch] = useState("");
  const [onlineOnly, setOnlineOnly] = useState(false);

  const filtered = useMemo(() => {
    return devices.filter((d) => {
      if (typeFilter !== "all" && d.type !== typeFilter) return false;
      if (vendorFilter !== "all" && d.vendor !== vendorFilter) return false;
      if (onlineOnly && !d.online) return false;
      if (search) {
        const q = search.toLowerCase();
        return d.name.toLowerCase().includes(q) || d.type.includes(q) || d.vendor.includes(q);
      }
      return true;
    });
  }, [devices, typeFilter, vendorFilter, search, onlineOnly]);

  const onlineCount = devices.filter((d) => d.online).length;
  const offlineCount = devices.length - onlineCount;
  const totalPowerW = devices.reduce((s, d) => s + (d.power_draw ?? 0), 0);
  const powerLabel = totalPowerW >= 1000
    ? `${(totalPowerW / 1000).toFixed(1)} kW`
    : `${Math.round(totalPowerW)} W`;

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 md:p-8 max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-6">
          <h1 className="font-display italic text-2xl text-text">Devices</h1>
          <p className="font-body font-light text-sm text-text-3 mt-1">
            {isLoading ? "Loading…" : `${onlineCount} of ${devices.length} online`}
          </p>
        </div>

        {/* Stats row */}
        {!isLoading && devices.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <StatPill label="Total" value={devices.length} />
            <StatPill label="Online" value={onlineCount} />
            <StatPill label="Offline" value={offlineCount} />
            <StatPill label="Live Power" value={powerLabel} />
          </div>
        )}

        {/* Search + filters */}
        <div className="space-y-3 mb-6">
          <div className="flex items-center gap-2 bg-surface border border-border rounded-lg px-3 py-2">
            <Search size={13} className="text-text-3 flex-shrink-0" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search devices…"
              className="flex-1 bg-transparent font-body text-sm text-text placeholder:text-text-3 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {TYPE_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setTypeFilter(f.value)}
                className={cn(
                  "px-3 py-1 rounded-full text-xs font-body font-light transition-colors",
                  typeFilter === f.value
                    ? "bg-graphite text-surface"
                    : "bg-surface border border-border text-text-3 hover:text-text hover:border-border-strong"
                )}
              >
                {f.label}
              </button>
            ))}
            <div className="w-px h-4 bg-border mx-1" />
            {VENDOR_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setVendorFilter(f.value)}
                className={cn(
                  "px-3 py-1 rounded-full text-xs font-body font-light transition-colors",
                  vendorFilter === f.value
                    ? "bg-graphite text-surface"
                    : "bg-surface border border-border text-text-3 hover:text-text hover:border-border-strong"
                )}
              >
                {f.label}
              </button>
            ))}
            <div className="w-px h-4 bg-border mx-1" />
            <button
              onClick={() => setOnlineOnly((v) => !v)}
              className={cn(
                "px-3 py-1 rounded-full text-xs font-body font-light transition-colors",
                onlineOnly
                  ? "bg-green text-surface"
                  : "bg-surface border border-border text-text-3 hover:text-text hover:border-border-strong"
              )}
            >
              Online only
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16">
            <EmptyState
              variant="no_devices"
              title="No devices found"
              description={search ? `No devices match "${search}"` : "Try adjusting your filters."}
            />
          </div>
        ) : (
          <>
            <p className="font-mono text-xs text-text-3 mb-4">{filtered.length} device{filtered.length !== 1 ? "s" : ""}</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map((device, i) => (
                <motion.div
                  key={device.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.04 }}
                >
                  <DeviceCard device={device} />
                </motion.div>
              ))}
            </div>
          </>
        )}
      </motion.div>
    </PageWrapper>
  );
}
