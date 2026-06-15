"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  Monitor,
  Plug,
  Settings,
  Sparkles,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";

interface SidebarItemProps {
  href: string;
  icon: LucideIcon;
  label: string;
  badge?: string;
  badgeVariant?: "alert" | "warn";
  active?: boolean;
}

function SidebarItem({
  href,
  icon: Icon,
  label,
  badge,
  badgeVariant = "alert",
  active,
}: SidebarItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-2.5 px-2.5 py-[7px] rounded-[10px] border no-underline",
        "transition-colors duration-[120ms]",
        active
          ? "bg-bg border-border"
          : "border-transparent hover:bg-surface-2",
      )}
    >
      {/* Icon chip — espresso when active, neutral when not */}
      <div
        className={cn(
          "w-6 h-6 rounded-[7px] flex items-center justify-center shrink-0",
          active ? "bg-accent text-white" : "bg-surface-2 text-text-3",
        )}
      >
        <Icon size={13} strokeWidth={1.5} />
      </div>

      <span
        className={cn(
          "text-[13px] flex-1",
          active ? "text-text font-semibold" : "text-text-2 font-normal",
        )}
      >
        {label}
      </span>

      {/* Count badge takes priority over the trailing dot */}
      {badge ? (
        <span
          className={cn(
            "font-mono text-[9px] uppercase tracking-[0.08em] font-semibold px-[7px] py-[2px] rounded-tag",
            badgeVariant === "alert"
              ? "bg-red-bg text-red"
              : "bg-amber-bg text-amber",
          )}
        >
          {badge}
        </span>
      ) : active ? (
        // 5px accent trailing dot for active items with no badge
        <span className="w-[5px] h-[5px] rounded-full bg-accent shrink-0" />
      ) : null}
    </Link>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const active = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <aside className="w-56 bg-surface border-r border-border px-3 py-4 flex flex-col gap-0.5 shrink-0 overflow-y-auto">
      <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 px-2.5 py-2 m-0">
        Workspace
      </p>

      {/* Nav order per spec: Intelligence · Portfolio · Devices · Integrations · Automations */}
      <SidebarItem
        href="/intelligence"
        icon={Sparkles}
        label="Intelligence"
        active={active("/intelligence")}
      />
      <SidebarItem
        href="/portfolio"
        icon={LayoutGrid}
        label="Portfolio"
        active={active("/portfolio")}
      />
      <SidebarItem
        href="/devices"
        icon={Monitor}
        label="Devices"
        badge="1"
        badgeVariant="alert"
        active={active("/devices")}
      />
      <SidebarItem
        href="/integrations"
        icon={Plug}
        label="Integrations"
        badge="1"
        badgeVariant="warn"
        active={active("/integrations")}
      />
      <SidebarItem
        href="/automations"
        icon={Zap}
        label="Automations"
        active={active("/automations")}
      />

      {/* Team + Settings pinned to bottom */}
      <div className="mt-auto pt-4 flex flex-col gap-0.5">
        <SidebarItem
          href="/team"
          icon={Users}
          label="Team"
          active={active("/team")}
        />
        <SidebarItem
          href="/settings"
          icon={Settings}
          label="Settings"
          active={active("/settings")}
        />
      </div>
    </aside>
  );
}
