"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart2,
  Bell,
  Brain,
  Building2,
  Cable,
  Cpu,
  Home,
  LayoutGrid,
  Settings,
  Users,
  Wrench,
  X,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/contexts/SidebarContext";
import { useAlerts } from "@/hooks/useAlerts";

const NAV_SECTIONS = [
  {
    label: "Overview",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: Home },
      { href: "/portfolio", label: "Portfolio", icon: LayoutGrid },
    ],
  },
  {
    label: "Operations",
    items: [
      { href: "/alerts", label: "Alerts", icon: Bell },
      { href: "/intelligence", label: "Intelligence", icon: Brain },
      { href: "/devices", label: "Devices", icon: Cpu },
    ],
  },
  {
    label: "Property Management",
    items: [
      { href: "/portfolio", label: "Properties", icon: Building2 },
      { href: "/tenants", label: "Tenants", icon: Users },
      { href: "/maintenance", label: "Maintenance", icon: Wrench },
    ],
  },
  {
    label: "Analytics",
    items: [
      { href: "/reports", label: "Reports", icon: BarChart2 },
      { href: "/energy", label: "Energy", icon: Zap },
    ],
  },
  {
    label: "Settings",
    items: [
      { href: "/integrations", label: "Integrations", icon: Cable },
      { href: "/settings", label: "Account", icon: Settings },
    ],
  },
];

const DOT_PATTERN = `url("data:image/svg+xml,%3Csvg width='20' height='20' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='1' cy='1' r='0.6' fill='%23e0dbcf' opacity='0.5'/%3E%3C/svg%3E")`;

function NavItem({
  href,
  label,
  icon: Icon,
  badge,
}: {
  href: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}) {
  const pathname = usePathname();
  const active = pathname === href || (href !== "/portfolio" && pathname.startsWith(href + "/"));

  return (
    <motion.div whileHover={{ x: active ? 0 : 2 }} transition={{ duration: 0.12 }}>
      <Link
        href={href}
        className={cn(
          "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors relative",
          active
            ? "border-l-2 border-l-graphite text-text font-normal bg-surface-2 rounded-l-none -ml-3 pl-[14px]"
            : "text-text-2 font-light hover:text-text hover:bg-surface-2"
        )}
      >
        <Icon size={14} />
        <span className="font-body">{label}</span>
        {badge != null && badge > 0 && (
          <span className="ml-auto bg-red rounded-full w-4 h-4 text-surface text-[9px] font-mono flex items-center justify-center flex-shrink-0">
            {badge > 9 ? "9+" : badge}
          </span>
        )}
      </Link>
    </motion.div>
  );
}

function SidebarContent() {
  const { data: alerts = [] } = useAlerts();
  const activeAlerts = alerts.filter((a) => !a.dismissed).length;

  return (
    <div className="flex flex-col h-full" style={{ backgroundImage: DOT_PATTERN }}>
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          {/* N monogram */}
          <div
            className="w-7 h-7 rounded-lg bg-graphite flex items-center justify-center flex-shrink-0"
          >
            <span className="font-display italic text-surface text-sm leading-none">N</span>
          </div>
          <div>
            <p className="font-display italic text-base text-text leading-tight tracking-tight">Nestra</p>
            <p className="font-body font-light text-[9px] text-text-3 uppercase tracking-widest leading-tight">
              Property Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <p className="font-mono text-[9px] text-text-3 uppercase tracking-widest px-3 mb-1.5">
              {section.label}
            </p>
            <div className="space-y-0.5">
              {section.items.map((item) => (
                <NavItem
                  key={item.href + item.label}
                  {...item}
                  badge={item.href === "/alerts" ? activeAlerts : undefined}
                />
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Bottom user area */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-graphite flex items-center justify-center text-surface text-xs font-display italic flex-shrink-0">
            A
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-body font-normal text-xs text-text truncate">Alphacon Demo</p>
            <span className="font-mono text-[10px] text-text-3">Free plan</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function Sidebar() {
  const { isOpen, close } = useSidebar();

  return (
    <>
      {/* Desktop */}
      <aside className="hidden md:flex w-[220px] flex-shrink-0 bg-surface border-r border-border flex-col h-full">
        <SidebarContent />
      </aside>

      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-graphite/40 z-40 md:hidden"
              onClick={close}
            />
            <motion.aside
              initial={{ x: -240 }}
              animate={{ x: 0 }}
              exit={{ x: -240 }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 bottom-0 w-[220px] bg-surface border-r border-border z-50 md:hidden flex flex-col"
            >
              <button
                onClick={close}
                className="absolute top-4 right-4 text-text-3 hover:text-text"
              >
                <X size={18} />
              </button>
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
