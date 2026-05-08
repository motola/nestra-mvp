"use client";

import * as RadixTabs from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

export function Tabs({
  defaultValue,
  tabs,
  className,
}: {
  defaultValue: string;
  tabs: { value: string; label: string; content: React.ReactNode }[];
  className?: string;
}) {
  return (
    <RadixTabs.Root defaultValue={defaultValue} className={className}>
      <RadixTabs.List className="flex items-center gap-1 bg-surface-2 rounded-xl p-1 w-fit mb-6">
        {tabs.map((tab) => (
          <RadixTabs.Trigger
            key={tab.value}
            value={tab.value}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-body transition-colors",
              "text-text-2 hover:text-text",
              "data-[state=active]:bg-surface data-[state=active]:text-text data-[state=active]:border data-[state=active]:border-border"
            )}
          >
            {tab.label}
          </RadixTabs.Trigger>
        ))}
      </RadixTabs.List>
      {tabs.map((tab) => (
        <RadixTabs.Content key={tab.value} value={tab.value}>
          {tab.content}
        </RadixTabs.Content>
      ))}
    </RadixTabs.Root>
  );
}
