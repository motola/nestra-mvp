"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number; name: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-2 text-xs">
      <p className="font-mono text-text-3 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="font-mono text-text font-medium">
          {p.value.toFixed(2)} kWh
        </p>
      ))}
    </div>
  );
}

export function EnergyChart({
  data,
  height = 200,
}: {
  data: { label: string; value: number }[];
  height?: number;
}) {
  const chartData = data.map((d) => ({
    name: d.label,
    "Energy (kWh)": d.value,
  }));
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 4, right: 8, left: -16, bottom: 0 }}
        >
          <defs>
            <linearGradient id="energyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#9a5e15" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#9a5e15" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e0dbcf"
            vertical={false}
          />
          <XAxis
            dataKey="name"
            tick={{
              fill: "#a39d8e",
              fontSize: 10,
              fontFamily: "var(--font-dm-mono)",
            }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{
              fill: "#a39d8e",
              fontSize: 10,
              fontFamily: "var(--font-dm-mono)",
            }}
            tickLine={false}
            axisLine={false}
            unit=" kWh"
          />
          <Tooltip content={<ChartTooltip />} />
          <Area
            type="monotone"
            dataKey="Energy (kWh)"
            stroke="#9a5e15"
            strokeWidth={1.5}
            fill="url(#energyGrad)"
            dot={false}
            activeDot={{ r: 3, fill: "#9a5e15" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
