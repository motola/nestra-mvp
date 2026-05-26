import { type LucideIcon } from "lucide-react";
import { cn } from "@/lib/cn";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "ghost"
  | "destructive"
  | "tagPrim"
  | "tagSec";

export type ButtonSize = "sm" | "md";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: LucideIcon;
  iconRight?: LucideIcon;
  children?: React.ReactNode;
}

const variants: Record<ButtonVariant, string> = {
  primary: "bg-graphite hover:bg-graphite-2 text-[#fbf9f4] rounded-[9px]",
  secondary:
    "bg-surface hover:bg-surface-2 text-text border border-border rounded-[9px]",
  ghost: "bg-transparent hover:bg-surface-2 text-text-2 rounded-[9px]",
  destructive:
    "bg-surface hover:bg-red-bg text-red border border-red-bg rounded-[9px]",
  tagPrim: "bg-graphite hover:bg-graphite-2 text-[#fbf9f4] rounded-tag",
  tagSec:
    "bg-surface-2 hover:bg-surface text-text-2 border border-border rounded-tag",
};

const sizes: Record<ButtonSize, string> = {
  sm: "text-[12px] px-[10px] py-[5px]",
  md: "text-[13px] px-[14px] py-[8px]",
};

const tagSizes: Record<ButtonSize, string> = {
  sm: "text-[11px] px-3 py-[5px]",
  md: "text-[11px] px-3 py-[5px]",
};

export function Button({
  variant = "secondary",
  size = "md",
  icon: Icon,
  iconRight: IconRight,
  className,
  children,
  ...props
}: ButtonProps) {
  const isTag = variant === "tagPrim" || variant === "tagSec";
  const iconSize = size === "sm" ? 12 : 14;

  return (
    <button
      className={cn(
        "inline-flex items-center gap-[7px] whitespace-nowrap font-sans font-medium leading-none",
        "transition-colors duration-[120ms] cursor-pointer [border-width:0] [border-style:solid]",
        isTag ? tagSizes[size] : sizes[size],
        variants[variant],
        className,
      )}
      {...props}
    >
      {Icon && <Icon size={iconSize} strokeWidth={1.5} />}
      {children}
      {IconRight && <IconRight size={iconSize} strokeWidth={1.5} />}
    </button>
  );
}
