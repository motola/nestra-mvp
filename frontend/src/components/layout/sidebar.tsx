"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Building,
  History,
  Home,
  LayoutGrid,
  MessageSquare,
  Monitor,
  Plug,
  Settings,
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
      <div
        className={cn(
          "w-6 h-6 rounded-[7px] flex items-center justify-center shrink-0",
          active ? "bg-graphite text-[#fbf9f4]" : "bg-surface-2 text-text-3",
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
      {badge && (
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
      )}
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
      <SidebarItem
        href="/overview"
        icon={Home}
        label="Overview"
        active={active("/overview")}
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
      <SidebarItem
        href="/agent"
        icon={MessageSquare}
        label="Agent"
        active={active("/agent")}
      />
      <SidebarItem
        href="/audit"
        icon={History}
        label="Audit log"
        active={active("/audit")}
      />

      <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 px-2.5 pt-4 pb-2 m-0">
        Properties
      </p>
      <SidebarItem
        href="/properties/maple-court"
        icon={Building}
        label="Maple Court"
        badge="1"
        badgeVariant="warn"
        active={active("/properties/maple-court")}
      />
      <SidebarItem
        href="/properties/ash-cottage"
        icon={Building}
        label="Ash Cottage"
        active={active("/properties/ash-cottage")}
      />
      <SidebarItem
        href="/properties/northbrook-mill"
        icon={Building}
        label="Northbrook Mill"
        badge="2"
        active={active("/properties/northbrook-mill")}
      />
      <SidebarItem
        href="/properties/heron-place"
        icon={Building}
        label="Heron Place"
        active={active("/properties/heron-place")}
      />
      <SidebarItem
        href="/properties/seacombe-wharf"
        icon={Building}
        label="Seacombe Wharf"
        active={active("/properties/seacombe-wharf")}
      />
      <div className="px-2.5 py-1.5">
        <span className="text-[12px] text-text-3">+ 7 more</span>
      </div>

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
