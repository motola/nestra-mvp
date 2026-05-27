import { cn } from "@/lib/cn";

type Severity = "amber" | "red" | "green" | "graphite";

interface AlertCardProps {
  severity?: Severity;
  title: string;
  desc: string;
  meta: string;
  actions?: string[];
  className?: string;
}

const dotColors: Record<Severity, string> = {
  amber: "bg-amber",
  red: "bg-red",
  green: "bg-green",
  graphite: "bg-graphite",
};

export function AlertCard({
  severity = "amber",
  title,
  desc,
  meta,
  actions = [],
  className,
}: AlertCardProps) {
  return (
    <div
      className={cn(
        "bg-surface border border-border rounded-card p-[18px]",
        className,
      )}
    >
      <div className="flex items-start gap-3">
        <span
          className={cn(
            "w-2.5 h-2.5 rounded-full mt-[6px] shrink-0",
            dotColors[severity],
          )}
        />
        <div className="flex-1 min-w-0">
          <p className="text-[14px] font-medium text-text leading-[1.4] m-0">
            {title}
          </p>
          <p className="text-[12px] text-text-2 leading-[1.55] mt-1.5 m-0">
            {desc}
          </p>
          <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mt-2.5 m-0">
            {meta}
          </p>
        </div>
      </div>
      {actions.length > 0 && (
        <div className="flex gap-2 mt-3 pl-[22px] flex-wrap">
          {actions.map((action, i) => (
            <button
              key={action}
              className={cn(
                "font-sans text-[11px] font-medium px-3 py-[5px] rounded-tag cursor-pointer",
                "transition-colors duration-[120ms] [border-width:0] [border-style:solid]",
                i === 0
                  ? "bg-graphite hover:bg-graphite-2 text-[#fbf9f4]"
                  : "bg-surface-2 hover:bg-surface text-text-2 border border-border",
              )}
            >
              {action}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
