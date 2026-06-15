"use client";

import { cn } from "@/lib/cn";

export interface TableColumn<T> {
  k: string;
  label: string;
  w: string;
  align?: "right" | "left";
  wrap?: boolean;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T extends object> {
  columns: TableColumn<T>[];
  rows: T[];
  onRowClick?: (row: T) => void;
}

export function DataTable<T extends object>({
  columns,
  rows,
  onRowClick,
}: DataTableProps<T>) {
  const colTemplate = columns.map((c) => c.w).join(" ");

  return (
    <div className="bg-surface border border-border rounded-card overflow-hidden">
      <div
        className="grid border-b border-border px-4"
        style={{ gridTemplateColumns: colTemplate }}
      >
        {columns.map((col) => (
          <div
            key={col.k}
            className={cn(
              "py-2.5 font-mono text-[10px] uppercase tracking-[0.08em] text-text-3",
              col.align === "right" && "text-right",
            )}
          >
            {col.label}
          </div>
        ))}
      </div>

      {rows.map((row, i) => (
        <div
          key={i}
          onClick={() => onRowClick?.(row)}
          className={cn(
            "grid px-4 items-center",
            i < rows.length - 1 && "border-b border-border",
            onRowClick &&
              "cursor-pointer hover:bg-surface-2 transition-colors duration-[120ms]",
          )}
          style={{ gridTemplateColumns: colTemplate }}
        >
          {columns.map((col) => (
            <div
              key={col.k}
              className={cn(
                "py-3",
                col.align === "right" && "text-right",
                col.wrap ? "whitespace-normal" : "truncate",
              )}
            >
              {col.render
                ? col.render(row)
                : String((row as Record<string, unknown>)[col.k] ?? "")}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
