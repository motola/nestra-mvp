"use client";

import { use, useState } from "react";
import {
  ArrowLeft,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useAlerts } from "@/hooks/useAlerts";
import { useProperty } from "@/hooks/useProperty";
import { DeviceCard, PageWrapper, SkeletonCard, AlertCard, PropertyIllustration } from "@/themes";
import { propertiesApi, provisioningApi, roomsApi } from "@/lib/api";
import { RoomManagement } from "@/components/property/RoomManagement";
import type { AlphaconDevice, Room, SavedDevice } from "@/lib/types";
import { cn } from "@/lib/utils";

// ── Stat card ─────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-surface/60 border border-white/20 rounded-xl p-3 backdrop-blur-sm">
      <p className="font-body font-normal text-xs uppercase tracking-widest text-white/60 mb-1">{label}</p>
      <p className="font-mono text-xl text-white">{value}</p>
      {sub && <p className="font-mono text-xs text-white/50 mt-0.5">{sub}</p>}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function PropertyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: property } = useProperty(id);
  const [activeTab, setActiveTab] = useState("overview");

  const { data: rooms = [] } = useQuery<Room[]>({
    queryKey: ["rooms", id],
    queryFn: () => roomsApi.list(id),
  });

  const { data: alphaDevices = [], isLoading: alphaLoading } = useQuery<AlphaconDevice[]>({
    queryKey: ["property-devices", id],
    queryFn: () => propertiesApi.devices(id),
    enabled: Boolean(property?.is_demo),
  });

  const { data: savedDevices = [], isLoading: savedLoading } = useQuery<SavedDevice[]>({
    queryKey: ["saved-devices", id],
    queryFn: () => provisioningApi.listDevices(id),
    enabled: !property?.is_demo,
  });

  const { data: alerts = [] } = useAlerts();

  const isDemo = Boolean(property?.is_demo);
  const isLoading = isDemo ? alphaLoading : savedLoading;

  const roomMap: Record<string, Room> = {};
  rooms.forEach((r) => {
    roomMap[r.id] = r;
    roomMap[String(r.id)] = r;
  });
  const getRoomForDevice = (roomId: string | null | undefined): Room | null => {
    if (!roomId) return null;
    return roomMap[roomId] ?? roomMap[String(roomId)] ?? null;
  };

  const propertyAlerts = alerts.filter((a) => !a.dismissed && a.property_id === id);
  const hasCritical = propertyAlerts.some((a) => a.severity === "critical");

  const onlineCount = alphaDevices.filter((d) => d.online).length;
  const totalPower = alphaDevices.reduce((s, d) => s + (d.power_draw ?? 0), 0);

  const demoByRoom = alphaDevices.reduce<Record<string, AlphaconDevice[]>>((acc, d) => {
    const room = getRoomForDevice(d.room_id);
    const key = room ? room.id : "__unassigned__";
    (acc[key] ??= []).push(d);
    return acc;
  }, {});

  const demoRoomsWithDevices = rooms.filter((r) => (demoByRoom[r.id] ?? []).length > 0);
  const demoUnassigned = demoByRoom["__unassigned__"] ?? [];

  const savedByRoom = savedDevices.reduce<Record<string, SavedDevice[]>>((acc, d) => {
    const room = getRoomForDevice(d.room_id);
    const key = room ? room.id : "__unassigned__";
    (acc[key] ??= []).push(d);
    return acc;
  }, {});

  const totalDeviceCount = isDemo ? alphaDevices.length : savedDevices.length;

  const TABS = [
    { value: "overview", label: "Overview" },
    { value: "devices", label: "Devices", count: totalDeviceCount },
    { value: "alerts", label: "Alerts", count: propertyAlerts.length },
  ];

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Hero banner */}
        <div className="bg-graphite text-surface px-6 md:px-8 pt-6 pb-0">
          <Link
            href="/portfolio"
            className="flex items-center gap-1.5 text-sm text-white/50 hover:text-white/80 mb-5 transition-colors w-fit"
          >
            <ArrowLeft size={14} />
            Portfolio
          </Link>

          <div className="flex items-end justify-between gap-6 pb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <span className="text-white/40">
                  <PropertyIllustration name={property?.name ?? ""} />
                </span>
                <h2 className="font-display italic text-3xl text-white">{property?.name ?? "Property"}</h2>
              </div>
              <p className="font-body font-light text-sm text-white/50 ml-[92px]">{property?.address}</p>
            </div>

            {/* Quick stats */}
            {isDemo && !isLoading && alphaDevices.length > 0 && (
              <div className="hidden sm:grid grid-cols-4 gap-2 flex-shrink-0">
                <StatCard label="Devices" value={alphaDevices.length} />
                <StatCard label="Rooms" value={rooms.length} />
                <StatCard label="Online" value={onlineCount} sub={`of ${alphaDevices.length}`} />
                <StatCard
                  label="Live Power"
                  value={totalPower >= 1000 ? `${(totalPower / 1000).toFixed(1)} kW` : `${Math.round(totalPower)} W`}
                />
              </div>
            )}
          </div>

          {/* Tab bar - part of the hero */}
          <div className="flex items-center gap-0 -mb-px">
            {TABS.map((tab) => (
              <button
                key={tab.value}
                onClick={() => setActiveTab(tab.value)}
                className={cn(
                  "flex items-center gap-2 px-4 py-3 text-sm font-body border-b-2 transition-colors",
                  activeTab === tab.value
                    ? "border-white text-white"
                    : "border-transparent text-white/50 hover:text-white/70"
                )}
              >
                {tab.label}
                {tab.count != null && tab.count > 0 && (
                  <span className={cn(
                    "font-mono text-xs px-1.5 py-0.5 rounded-full",
                    activeTab === tab.value
                      ? "bg-white/20 text-white"
                      : "bg-white/10 text-white/50"
                  )}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Tab content */}
        <div className="p-6 md:p-8 max-w-7xl mx-auto">

          {/* Critical alert banner */}
          {hasCritical && (
            <div className="mb-6 bg-red-bg border border-red/20 rounded-xl p-4 flex items-center gap-3">
              <XCircle size={16} className="text-red flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="font-body font-normal text-sm text-text">Critical alerts active</p>
                <p className="font-body font-light text-xs text-text-3 mt-0.5">
                  {propertyAlerts.filter((a) => a.severity === "critical").length} critical issue
                  {propertyAlerts.filter((a) => a.severity === "critical").length !== 1 ? "s" : ""} require attention
                </p>
              </div>
              <Link
                href="/alerts"
                className="font-body font-light text-xs text-red hover:underline flex-shrink-0"
              >
                View alerts →
              </Link>
            </div>
          )}

          {/* Mobile stats (demo only) */}
          {isDemo && !isLoading && alphaDevices.length > 0 && (
            <div className="sm:hidden grid grid-cols-2 gap-3 mb-6">
              <div className="bg-surface border border-border rounded-xl p-3">
                <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-1">Devices</p>
                <p className="font-mono text-xl text-text">{alphaDevices.length}</p>
              </div>
              <div className="bg-surface border border-border rounded-xl p-3">
                <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-1">Online</p>
                <p className="font-mono text-xl text-text">{onlineCount}</p>
                <p className="font-mono text-xs text-text-3">of {alphaDevices.length}</p>
              </div>
            </div>
          )}

          {/* OVERVIEW TAB */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {rooms.length > 0 && (
                <div>
                  <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-3">Rooms</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {rooms.map((room) => {
                      const roomDevices = isDemo
                        ? (demoByRoom[room.id] ?? [])
                        : (savedByRoom[room.id] ?? []);
                      const roomOnline = isDemo
                        ? roomDevices.filter((d) => (d as AlphaconDevice).online).length
                        : 0;
                      return (
                        <div
                          key={room.id}
                          className="bg-surface border border-border rounded-xl p-4 hover:border-border-strong transition-colors"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <p className="font-body font-normal text-sm text-text">{room.name}</p>
                            {room.floor != null && (
                              <span className="font-mono text-xs text-text-3">Floor {room.floor}</span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 font-mono text-xs text-text-3">
                            <span>{roomDevices.length} device{roomDevices.length !== 1 ? "s" : ""}</span>
                            {isDemo && roomDevices.length > 0 && (
                              <span className="text-green">{roomOnline} online</span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {propertyAlerts.length === 0 && rooms.length === 0 && (
                <div className="py-12 text-center">
                  <p className="font-body font-light text-sm text-text-3">
                    No rooms configured for this property yet.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* DEVICES TAB */}
          {activeTab === "devices" && (
            <>
              {isLoading && (
                <div className="space-y-6">
                  {[1, 2].map((i) => (
                    <div key={i}>
                      <div className="h-3 w-24 bg-surface-2 rounded mb-3 animate-pulse" />
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {[1, 2].map((j) => <SkeletonCard key={j} />)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!isLoading && isDemo && (
                <>
                  {alphaDevices.length === 0 && (
                    <p className="font-body font-light text-sm text-text-3 py-12 text-center">
                      No devices linked to this property yet.
                    </p>
                  )}
                  <div className="space-y-8">
                    {demoRoomsWithDevices.map((room) => (
                      <div key={room.id}>
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
                            {room.name}
                            {room.floor != null && (
                              <span className="ml-2 normal-case font-light">· Floor {room.floor}</span>
                            )}
                          </h3>
                          <div className="flex-1 border-t border-border" />
                          <span className="font-mono text-xs text-text-3">
                            {(demoByRoom[room.id] ?? []).length}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {(demoByRoom[room.id] ?? []).map((d) => (
                            <DeviceCard key={d.id} device={d} propertyId={id} />
                          ))}
                        </div>
                      </div>
                    ))}

                    {demoUnassigned.length > 0 && (
                      <div>
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
                            Unassigned
                          </h3>
                          <div className="flex-1 border-t border-border" />
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {demoUnassigned.map((d) => (
                            <DeviceCard key={d.id} device={d} propertyId={id} />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}

              {!isLoading && !isDemo && (
                <RoomManagement
                  propertyId={id}
                  propertyName={property?.name ?? ""}
                  rooms={rooms}
                  savedDevices={savedDevices}
                />
              )}
            </>
          )}

          {/* ALERTS TAB */}
          {activeTab === "alerts" && (
            <div className="space-y-2">
              {propertyAlerts.length === 0 ? (
                <div className="py-16 text-center">
                  <p className="font-display italic text-xl text-text mb-2">No active alerts</p>
                  <p className="font-body font-light text-sm text-text-3">This property is running normally.</p>
                </div>
              ) : (
                propertyAlerts.map((alert, i) => (
                  <AlertCard key={alert.id} alert={alert} index={i} />
                ))
              )}
            </div>
          )}
        </div>
      </motion.div>
    </PageWrapper>
  );
}
