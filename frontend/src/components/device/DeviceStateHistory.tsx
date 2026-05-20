"use client";

import { useQuery } from "@tanstack/react-query";
import { shellyDeviceApi } from "@/lib/api";
import type { StateHistoryEvent } from "@/lib/types";
import { relativeTime } from "@/lib/utils";

const EVENT_LABELS: Record<string, string> = {
  turned_on: "Turned on",
  turned_off: "Turned off",
  went_offline: "Went offline",
  came_online: "Came online",
  power_spike: "Power spike",
  power_normal: "Power normal",
};

const EVENT_DOT_CLASS: Record<string, string> = {
  turned_on: "bg-green",
  came_online: "bg-green",
  turned_off: "bg-red",
  went_offline: "bg-red",
  power_spike: "bg-amber",
  power_normal: "bg-text-3",
};

export function DeviceStateHistory({ deviceId }: { deviceId: string }) {
  const { data: events = [], isLoading } = useQuery<StateHistoryEvent[]>({
    queryKey: ["device-history", deviceId],
    queryFn: () => shellyDeviceApi.getHistory(deviceId),
    refetchInterval: 30_000,
    retry: false,
  });

  const display = events
    .filter((e) => e.event_type !== "power_reading")
    .slice(0, 20);

  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <p className="font-body font-normal text-sm text-text mb-4">
        State History
      </p>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-surface-2 animate-pulse shrink-0" />
              <div className="h-3 bg-surface-2 rounded animate-pulse flex-1" />
              <div className="h-3 w-16 bg-surface-2 rounded animate-pulse" />
            </div>
          ))}
        </div>
      ) : display.length === 0 ? (
        <p className="font-body font-light text-xs text-text-3">
          No history yet. History builds up as the device is used.
        </p>
      ) : (
        <div className="space-y-3">
          {display.map((event) => (
            <div key={event.id} className="flex items-center gap-3">
              <div
                className={`w-2 h-2 rounded-full shrink-0 ${
                  EVENT_DOT_CLASS[event.event_type] ?? "bg-text-3"
                }`}
              />
              <span className="font-body font-light text-sm text-text-2 flex-1">
                {EVENT_LABELS[event.event_type] ?? event.event_type}
                {event.value && (
                  <span className="font-mono text-text-3 ml-1 text-xs">
                    ({event.value})
                  </span>
                )}
              </span>
              <span className="font-mono text-xs text-text-3 shrink-0">
                {relativeTime(event.recorded_at)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
