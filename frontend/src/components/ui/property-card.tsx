import { Card } from "./card";
import { Tag } from "./tag";
import { cn } from "@/lib/cn";
import type { Property } from "@/lib/fixtures";

const statusDot: Record<string, string> = {
  ok: "bg-green",
  warn: "bg-amber",
  alert: "bg-red",
};

interface PropertyCardProps extends Property {
  onClick?: () => void;
}

export function PropertyCard({
  name,
  address,
  type,
  units,
  occupied,
  alerts,
  status,
  devices,
  onClick,
}: PropertyCardProps) {
  return (
    <Card hoverable onClick={onClick} className="p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="font-serif text-[16px] leading-[1.2] text-text truncate">
            {name}
          </div>
          <div className="font-mono text-[11px] uppercase tracking-[0.08em] text-text-3 mt-0.5">
            {address}
          </div>
        </div>
        <span
          className={cn(
            "w-2 h-2 rounded-full shrink-0 mt-[5px]",
            statusDot[status],
          )}
        />
      </div>

      <div className="h-px bg-border" />

      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-0.5">
          <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
            Units
          </span>
          <span className="text-[13px] font-medium text-text [font-variant-numeric:tabular-nums]">
            {occupied}/{units}
          </span>
        </div>
        <div className="flex flex-col gap-0.5 items-end">
          <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
            Devices
          </span>
          <span className="text-[13px] font-medium text-text [font-variant-numeric:tabular-nums]">
            {devices}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-1.5 flex-wrap">
        <Tag variant="neutral">{type.replace(/_/g, " ").toLowerCase()}</Tag>
        {alerts > 0 ? (
          <Tag variant={status === "alert" ? "alert" : "warn"} withDot>
            {alerts} alert{alerts > 1 ? "s" : ""}
          </Tag>
        ) : (
          <Tag variant="ok" withDot>
            All clear
          </Tag>
        )}
      </div>
    </Card>
  );
}
