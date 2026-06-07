"use client";

import { cn } from "@/lib/cn";

export interface TabItem {
  id: string;
  label: string;
  count?: number;
}

interface TabsProps {
  value: string;
  onChange: (id: string) => void;
  tabs: TabItem[];
}

export function Tabs({ value, onChange, tabs }: TabsProps) {
  return (
    <nav className="flex">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            "relative flex items-center gap-1.5 px-3 py-[11px]",
            "text-[13px] font-medium bg-transparent border-0 cursor-pointer",
            "after:absolute after:bottom-[-1px] after:left-0 after:right-0",
            "after:h-[2px] after:content-['']",
            "transition-colors duration-[120ms]",
            value === tab.id
              ? "text-text after:bg-graphite"
              : "text-text-2 after:bg-transparent hover:text-text",
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className="font-mono text-[10px] text-text-3">
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </nav>
  );
}
