"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function TrendTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-1.5">
      <p className="font-mono text-xs text-text-3">{label}</p>
      <p className="font-mono text-sm text-text">{payload[0].value}</p>
    </div>
  );
}

export function TrendChart({
  data,
  height = 200,
  color = "#28241e",
}: {
  data: { label: string; value: number }[];
  height?: number;
  color?: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart
        data={data}
        margin={{ top: 8, right: 6, bottom: 0, left: -18 }}
      >
        <CartesianGrid
          stroke="#e0dbcf"
          strokeDasharray="2 4"
          vertical={false}
        />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 10, fill: "#a39d8e" }}
          axisLine={false}
          tickLine={false}
          interval="preserveStartEnd"
          minTickGap={24}
        />
        <YAxis
          tick={{ fontSize: 10, fill: "#a39d8e" }}
          axisLine={false}
          tickLine={false}
          width={30}
          allowDecimals={false}
        />
        <Tooltip
          content={<TrendTooltip />}
          cursor={{ stroke: "#cdc6b8", strokeWidth: 1 }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          fill={color}
          fillOpacity={0.08}
          animationDuration={700}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
