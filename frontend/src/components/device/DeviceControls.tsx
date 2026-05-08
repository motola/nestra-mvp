"use client";

import { Power } from "lucide-react";
import type { AlphaconDevice } from "@/lib/types";
import { cn } from "@/lib/utils";

export function DeviceControls({ device }: { device: AlphaconDevice }) {
  if (!device.controllable) return null;

  const state = device.state as Record<string, unknown>;
  const isOn = Boolean(state.on);

  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <p className="font-body font-normal text-sm text-text mb-4">Controls</p>
      <div className="flex items-center gap-4">
        <button
          disabled
          title="Control endpoint coming soon"
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-body opacity-50 cursor-not-allowed",
            isOn
              ? "bg-green text-surface"
              : "bg-surface-2 border border-border text-text-2"
          )}
        >
          <Power size={14} />
          {isOn ? "Turn Off" : "Turn On"}
        </button>
        <span className="font-body font-light text-xs text-text-3">Controls active in next release</span>
      </div>
    </div>
  );
}
