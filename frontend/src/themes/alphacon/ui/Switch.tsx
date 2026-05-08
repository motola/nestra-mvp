"use client";

import * as RadixSwitch from "@radix-ui/react-switch";
import { cn } from "@/lib/utils";

export function Switch({
  checked,
  onCheckedChange,
  label,
  description,
  id,
}: {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  id?: string;
}) {
  const switchId = id ?? `switch-${Math.random().toString(36).slice(2)}`;
  return (
    <div className="flex items-center justify-between py-3">
      {(label || description) && (
        <div className="flex-1 mr-4">
          {label && (
            <label htmlFor={switchId} className="font-body font-normal text-sm text-text cursor-pointer">
              {label}
            </label>
          )}
          {description && (
            <p className="font-body font-light text-xs text-text-3 mt-0.5">{description}</p>
          )}
        </div>
      )}
      <RadixSwitch.Root
        id={switchId}
        checked={checked}
        onCheckedChange={onCheckedChange}
        className={cn(
          "relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none flex-shrink-0",
          checked ? "bg-graphite" : "bg-border"
        )}
      >
        <RadixSwitch.Thumb
          className={cn(
            "block h-4 w-4 rounded-full bg-surface transition-transform",
            checked ? "translate-x-[18px]" : "translate-x-0.5"
          )}
        />
      </RadixSwitch.Root>
    </div>
  );
}
