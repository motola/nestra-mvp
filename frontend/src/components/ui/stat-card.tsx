import { cn } from "@/lib/cn";

type StatVariant = "default" | "amber" | "red" | "green";

interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  sub?: React.ReactNode;
  variant?: StatVariant;
}

const valueColors: Record<StatVariant, string> = {
  default: "text-text",
  amber: "text-amber",
  red: "text-red",
  green: "text-green",
};

export function StatCard({
  label,
  value,
  unit,
  sub,
  variant = "default",
}: StatCardProps) {
  return (
    <div className="bg-surface border border-border rounded-card p-[18px]">
      <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mb-3 m-0">
        {label}
      </p>
      <p
        className={cn(
          "text-[30px] font-semibold leading-none tracking-[-0.01em] m-0",
          "[font-variant-numeric:tabular-nums]",
          valueColors[variant],
        )}
      >
        {value}
        {unit && (
          <span className="text-[18px] text-text-3 font-medium ml-[2px]">
            {unit}
          </span>
        )}
      </p>
      <div className="h-px bg-border my-3" />
      <div className="text-[12px] text-text-3">{sub}</div>
    </div>
  );
}
