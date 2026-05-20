import { cn } from "@/lib/utils";
import { Button } from "./Button";

// SVG illustrations for each variant
function NoDevicesSVG() {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="24"
        y="22"
        width="32"
        height="36"
        rx="3"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M36 22V16h8v6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <circle cx="40" cy="40" r="6" stroke="currentColor" strokeWidth="1.5" />
      <line
        x1="36.5"
        y1="36.5"
        x2="43.5"
        y2="43.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="43.5"
        y1="36.5"
        x2="36.5"
        y2="43.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="40"
        y1="58"
        x2="40"
        y2="64"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="34"
        y1="64"
        x2="46"
        y2="64"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function NoAlertsSVG() {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M40 14L56 58H24L40 14Z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
      <line
        x1="40"
        y1="32"
        x2="40"
        y2="44"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="40" cy="51" r="1.5" fill="currentColor" />
      <path
        d="M28 66a12 12 0 0 1 24 0"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M32 72l8-6 8 6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function NoHistorySVG() {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <line
        x1="20"
        y1="40"
        x2="60"
        y2="40"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeDasharray="3 3"
      />
      <circle
        cx="24"
        cy="40"
        r="3.5"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="var(--color-bg)"
      />
      <circle
        cx="40"
        cy="32"
        r="3.5"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="var(--color-bg)"
      />
      <circle
        cx="56"
        cy="48"
        r="3.5"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="var(--color-bg)"
      />
      <line
        x1="24"
        y1="40"
        x2="40"
        y2="32"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="40"
        y1="32"
        x2="56"
        y2="48"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function NoPropertiesSVG() {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M16 40L40 16L64 40"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect
        x="22"
        y="39"
        width="36"
        height="25"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <rect
        x="34"
        y="52"
        width="12"
        height="12"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <rect
        x="27"
        y="45"
        width="8"
        height="7"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.3"
      />
      <rect
        x="45"
        y="45"
        width="8"
        height="7"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.3"
      />
    </svg>
  );
}

function NoInsightsSVG() {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="40" cy="34" r="14" stroke="currentColor" strokeWidth="1.8" />
      <line
        x1="40"
        y1="48"
        x2="40"
        y2="56"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <line
        x1="33"
        y1="56"
        x2="47"
        y2="56"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M34 28c0-3.3 2.7-6 6-6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line
        x1="33"
        y1="22"
        x2="27"
        y2="16"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
      <line
        x1="47"
        y1="22"
        x2="53"
        y2="16"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
      <line
        x1="40"
        y1="20"
        x2="40"
        y2="12"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
    </svg>
  );
}

function GenericSVG({ icon: Icon }: { icon?: React.ElementType }) {
  if (!Icon) return null;
  return (
    <div className="w-20 h-20 flex items-center justify-center">
      <Icon size={40} />
    </div>
  );
}

type EmptyVariant =
  | "no_devices"
  | "no_alerts"
  | "no_history"
  | "no_properties"
  | "no_insights";

const VARIANT_SVG: Record<EmptyVariant, React.ComponentType> = {
  no_devices: NoDevicesSVG,
  no_alerts: NoAlertsSVG,
  no_history: NoHistorySVG,
  no_properties: NoPropertiesSVG,
  no_insights: NoInsightsSVG,
};

export function EmptyState({
  variant,
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: {
  variant?: EmptyVariant;
  icon?: React.ElementType;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}) {
  const VariantSVG = variant ? VARIANT_SVG[variant] : null;

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-16 text-center px-8",
        className,
      )}
    >
      <div className="text-border mb-5">
        {VariantSVG ? <VariantSVG /> : icon ? <GenericSVG icon={icon} /> : null}
      </div>
      <p className="font-display italic text-xl text-text mb-2">{title}</p>
      {description && (
        <p className="font-body font-light text-sm text-text-3 max-w-xs leading-relaxed">
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <Button variant="primary" size="md" className="mt-6" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
