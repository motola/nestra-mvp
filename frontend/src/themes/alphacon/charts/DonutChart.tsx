"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

function CustomTooltip({ active, payload }: { active?: boolean; payload?: { name: string; value: number }[] }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-2 text-xs">
      <p className="font-mono text-text">{payload[0].name}: <span className="font-medium">{payload[0].value}</span></p>
    </div>
  );
}

export function DonutChart({
  data,
  total,
  label,
  height = 200,
}: {
  data: { name: string; value: number; color: string }[];
  total?: number;
  label?: string;
  height?: number;
}) {
  const size = Math.min(height, 160);
  const displayTotal = total ?? data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="flex flex-col items-center gap-4">
      <div style={{ width: size, height: size }} className="relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={size * 0.32}
              outerRadius={size * 0.48}
              dataKey="value"
              strokeWidth={0}
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="font-mono text-2xl text-text">{displayTotal}</span>
          {label && <span className="font-body font-light text-xs text-text-3">{label}</span>}
        </div>
      </div>
      <div className="flex flex-wrap justify-center gap-3">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: d.color }} />
            <span className="font-body font-light text-xs text-text-2">{d.name}</span>
            <span className="font-mono text-xs text-text-3">({d.value})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
