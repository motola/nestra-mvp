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
  payload?: { value: number }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-2 text-xs">
      <p className="font-mono text-text-3 mb-0.5">{label}</p>
      <p className="font-mono text-text font-medium">
        {payload[0].value.toFixed(1)} W
      </p>
    </div>
  );
}

export function PowerChart({
  data,
  height = 160,
}: {
  data: { time: string; watts: number }[];
  height?: number;
}) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 4, right: 8, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="powerGradChart" x1="0" y1="0" x2="0" y2="1">
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
            dataKey="time"
            tick={{
              fill: "#a39d8e",
              fontSize: 10,
              fontFamily: "var(--font-dm-mono)",
            }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{
              fill: "#a39d8e",
              fontSize: 10,
              fontFamily: "var(--font-dm-mono)",
            }}
            tickLine={false}
            axisLine={false}
            unit="W"
          />
          <Tooltip content={<ChartTooltip />} />
          <Area
            type="monotone"
            dataKey="watts"
            stroke="#9a5e15"
            strokeWidth={1.5}
            fill="url(#powerGradChart)"
            dot={false}
            activeDot={{ r: 3, fill: "#9a5e15" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
