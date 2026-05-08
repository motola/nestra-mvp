"use client";

import Link from "next/link";
import { Droplets, Lock, LockOpen, Shield, Thermometer, Wifi, WifiOff, Zap } from "lucide-react";
import type { AlphaconDevice } from "@/lib/types";
import { cn } from "@/lib/utils";
import { kelvinToRgb, BrightnessBar } from "./ColourPreview";

// Sensor status tints
function getTempTint(temp: number): string {
  if (temp < 16) return "border-l-[#5b8dd9] bg-[rgba(91,141,217,0.04)]";
  if (temp > 22) return "border-l-amber bg-amber-bg/30";
  return "";
}
function getHumidityTint(h: number): string {
  if (h > 70) return "border-l-red bg-red-bg/30";
  if (h > 60) return "border-l-amber bg-amber-bg/30";
  return "";
}
function getTempLabel(temp: number): string {
  if (temp < 16) return "Too cold";
  if (temp > 22) return "Too warm";
  return "Comfortable";
}
function getHumidLabel(h: number): string {
  if (h > 70) return "Too humid";
  if (h > 60) return "Slightly humid";
  if (h < 40) return "Too dry";
  return "Comfortable";
}

// Power colour coding
function powerColor(w: number): string {
  if (w === 0) return "text-text-3";
  if (w <= 100) return "text-green";
  if (w <= 500) return "text-amber";
  return "text-red";
}

function getLightGradient(r: number, g: number, b: number, on: boolean): string {
  if (!on) return "";
  return `radial-gradient(ellipse at 50% 0%, rgba(${r},${g},${b},0.1) 0%, transparent 70%)`;
}

export function DeviceCard({
  device,
  propertyId,
}: {
  device: AlphaconDevice;
  propertyId?: string;
}) {
  const href = propertyId ? `/properties/${propertyId}/devices/${device.id}` : "#";
  const state = device.state as Record<string, unknown>;
  const isOn = Boolean(state.on);
  const isLocked = Boolean(state.locked);
  const hasMotion = "motion" in state;
  const motionActive = Boolean(state.motion);

  // Light colour state
  const colorState = state.color as { r: number; g: number; b: number } | undefined;
  const colorTem = (state.colorTem ?? state.color_temp_kelvin) as number | undefined;
  let lightR = 255, lightG = 210, lightB = 140;
  if (colorState) { lightR = colorState.r; lightG = colorState.g; lightB = colorState.b; }
  else if (colorTem) { [lightR, lightG, lightB] = kelvinToRgb(colorTem); }

  const brightness = typeof state.brightness === "number" ? state.brightness as number : 100;
  const isLight = device.type === "light";
  const gradientStyle = isLight ? { background: getLightGradient(lightR, lightG, lightB, isOn) } : {};
  const borderStyle = isLight && isOn ? { borderColor: `rgba(${lightR},${lightG},${lightB},0.3)` } : {};

  // Sensor tints
  const tempTint = device.temperature != null ? getTempTint(device.temperature) : "";
  const humidTint = device.humidity != null && !tempTint ? getHumidityTint(device.humidity) : "";
  const sensorTint = tempTint || humidTint;

  return (
    <Link href={href}>
      <div
        className={cn(
          "bg-surface border border-border rounded-xl p-4 cursor-pointer",
          "hover:border-border-strong hover:bg-surface-2 hover:-translate-y-0.5 transition-all duration-150",
          sensorTint && `border-l-4 ${sensorTint}`
        )}
        style={{ ...gradientStyle, ...borderStyle, transition: "background 0.3s ease, border-color 0.3s ease" }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="min-w-0">
            <p className="font-body text-sm text-text truncate">{device.name}</p>
            <p className="font-mono text-xs text-text-3 mt-0.5 capitalize">
              {device.vendor !== "demo" ? `${device.vendor} · ` : ""}{device.type}
            </p>
          </div>
          <span className={cn(
            "flex items-center gap-1 font-mono text-xs px-2 py-0.5 rounded-full",
            device.online
              ? "bg-green-bg text-green border border-green/20"
              : "bg-surface-2 text-text-3 border border-border"
          )}>
            {device.online ? <Wifi size={10} /> : <WifiOff size={10} />}
            {device.online ? "Online" : "Offline"}
          </span>
        </div>

        <div className="space-y-1.5 font-mono text-xs text-text-3">
          {device.type === "plug" && device.power_draw != null && (
            <div className="flex items-center gap-1.5">
              <Zap size={11} />
              <span className={powerColor(device.power_draw)}>{device.power_draw} W</span>
              <span className={cn("ml-auto", isOn ? "text-amber" : "text-text-3")}>
                {isOn ? "On" : "Off"}
              </span>
            </div>
          )}
          {isLight && (
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5">
                <span
                  className={cn("w-2.5 h-2.5 rounded-full border border-black/10 flex-shrink-0")}
                  style={isOn ? { backgroundColor: `rgb(${lightR},${lightG},${lightB})` } : { backgroundColor: "#e0dbcf" }}
                />
                <span className={isOn ? "text-text-2" : "text-text-3"}>{isOn ? "On" : "Off"}</span>
                {isOn && (
                  <span className="text-text-3 ml-auto">{Math.round((brightness / 254) * 100)}%</span>
                )}
              </div>
              {isOn && <BrightnessBar brightness={Math.round((brightness / 254) * 100)} r={lightR} g={lightG} b={lightB} />}
            </div>
          )}
          {device.type === "lock" && (
            <div className="flex items-center gap-1.5">
              {isLocked ? <Lock size={11} className="text-green" /> : <LockOpen size={11} className="text-amber" />}
              <span className={isLocked ? "text-green" : "text-amber"}>{isLocked ? "Locked" : "Unlocked"}</span>
            </div>
          )}
          {hasMotion && (
            <div className="flex items-center gap-1.5">
              <Shield size={11} className={motionActive ? "text-amber" : undefined} />
              <span className={motionActive ? "text-amber" : undefined}>
                {motionActive ? "Motion detected" : "No motion"}
              </span>
            </div>
          )}
          {device.leak_detected != null && (
            <div className="flex items-center gap-1.5">
              <Droplets size={11} className={device.leak_detected ? "text-red" : undefined} />
              <span className={device.leak_detected ? "text-red" : undefined}>
                {device.leak_detected ? "Leak detected" : "Dry"}
              </span>
            </div>
          )}
          {device.temperature != null && (
            <div className="flex items-center justify-between gap-1.5">
              <div className="flex items-center gap-1.5">
                <Thermometer size={11} />
                <span>{device.temperature.toFixed(1)} °C</span>
              </div>
              <span className={cn("text-xs", tempTint ? "text-amber" : "text-text-3")}>
                {getTempLabel(device.temperature)}
              </span>
            </div>
          )}
          {device.humidity != null && (
            <div className="flex items-center justify-between gap-1.5">
              <div className="flex items-center gap-1.5">
                <Droplets size={11} />
                <span>{device.humidity.toFixed(0)} %</span>
              </div>
              <span className={cn("text-xs", humidTint ? "text-amber" : "text-text-3")}>
                {getHumidLabel(device.humidity)}
              </span>
            </div>
          )}
        </div>

        <p className="font-mono text-xs text-text-3 mt-3">
          {new Date(device.last_seen).toLocaleTimeString(undefined, {
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </Link>
  );
}
