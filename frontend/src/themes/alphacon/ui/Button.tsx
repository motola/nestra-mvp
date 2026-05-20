"use client";

import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

const VARIANTS: Record<ButtonVariant, string> = {
  primary: "bg-graphite hover:bg-graphite-2 text-surface",
  secondary:
    "bg-surface-2 border border-border hover:border-border-strong text-text-2 hover:text-text",
  ghost: "text-text-3 hover:text-text hover:bg-surface-2",
  danger: "bg-red-bg text-red border border-red/20 hover:border-red/40",
};

export function Button({
  children,
  variant = "primary",
  size = "md",
  className,
  ...props
}: {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: "sm" | "md" | "lg";
  className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-5 py-2.5 text-sm",
    lg: "px-6 py-3 text-base",
  };
  return (
    <button
      className={cn(
        "inline-flex items-center gap-2 font-body font-normal rounded-lg transition-all active:scale-[0.97] disabled:opacity-50",
        VARIANTS[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
