"use client"; // Client: account menu

import { useState } from "react";
import { Bell, Building, ChevronRight, LogOut, Search } from "lucide-react";
import { useAuth } from "@/lib/auth/provider";
import { useLogout } from "@/lib/api/hooks/use-auth";
import { LogoMark } from "@/components/ui/logo";

export function TopNav() {
  const [open, setOpen] = useState(false);
  const { user, organization } = useAuth();
  const logout = useLogout();

  const handleLogout = () => {
    logout.mutate();
  };

  const initials =
    user?.full_name
      .split(" ")
      .map((p) => p[0])
      .join("")
      .toUpperCase() || "?";

  return (
    <header className="h-14 bg-surface border-b border-border flex items-center px-5 gap-5 shrink-0 z-20">
      {/* Brand mark */}
      <div className="flex items-center gap-2.5 shrink-0">
        <LogoMark />
        <span className="font-serif text-[22px] tracking-[-0.01em] text-text">
          Alphacon
        </span>
      </div>

      {/* Org switcher */}
      <div className="ml-2 px-2.5 py-1 rounded-[9px] flex items-center gap-2 bg-bg border border-border cursor-pointer">
        <Building
          size={13}
          strokeWidth={1.5}
          className="text-text-3 shrink-0"
        />
        <span className="text-[12px] text-text-2 font-medium">
          {organization?.name || "Organization"}
        </span>
        <ChevronRight size={12} strokeWidth={1.5} className="text-text-3" />
      </div>

      {/* Search */}
      <button
        onClick={() => {
          // TODO: Open search modal/command palette
        }}
        className="ml-2 flex-1 max-w-[280px] bg-bg border border-border rounded-[8px] px-2.5 py-1.5 flex items-center gap-2 cursor-text overflow-hidden hover:border-border-strong transition-colors duration-[120ms]"
      >
        <Search size={13} strokeWidth={1.5} className="text-text-3 shrink-0" />
        <span className="text-[12px] text-text-2 truncate flex-1 select-none">
          Search…
        </span>
        <kbd className="shrink-0 font-mono text-[9px] text-text-3 bg-surface-2 border border-border px-1.5 py-0.5 rounded">
          ⌘K
        </kbd>
      </button>

      {/* Bell + account */}
      <div className="ml-auto flex items-center gap-3.5">
        <button className="bg-transparent border-0 cursor-pointer p-1.5 relative hover:text-text transition-colors">
          <Bell size={18} strokeWidth={1.5} className="text-text-2" />
          {/* TODO: Show badge only when there are actual notifications */}
        </button>

        <div className="relative">
          <button
            onClick={() => setOpen(!open)}
            className="flex items-center gap-2 pl-[3px] pr-2 py-[3px] rounded-tag border border-border cursor-pointer hover:border-border-strong transition-colors"
          >
            <div className="w-[26px] h-[26px] rounded-full bg-graphite text-white flex items-center justify-center font-mono text-[10px] font-medium tracking-[0.5px]">
              {initials}
            </div>
            <span className="text-[12px] text-text-2 pr-1">
              {user?.full_name.split(" ")[0] || "Account"}
            </span>
          </button>

          {open && (
            <div className="absolute top-full right-0 mt-1 bg-surface border border-border rounded-card shadow-md py-1 z-50 min-w-[180px]">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-[12px] text-text hover:bg-bg transition-colors border-0 bg-transparent cursor-pointer"
              >
                <LogOut size={14} strokeWidth={1.5} className="text-text-3" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
