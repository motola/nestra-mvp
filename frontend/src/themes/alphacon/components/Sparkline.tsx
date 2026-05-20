// Pure SVG deterministic sparkline seeded from a string

function seeded(seed: string, count = 12): number[] {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const vals: number[] = [];
  for (let i = 0; i < count; i++) {
    h = (h * 1664525 + 1013904223) >>> 0;
    vals.push((h % 600) + 100);
  }
  return vals;
}

export function Sparkline({
  seed,
  width = 80,
  height = 28,
  className,
}: {
  seed: string;
  width?: number;
  height?: number;
  className?: string;
}) {
  const vals = seeded(seed);
  const min = Math.min(...vals),
    max = Math.max(...vals);
  const norm = (v: number) => height - ((v - min) / (max - min || 1)) * height;
  const pts = vals
    .map((v, i) => `${(i / (vals.length - 1)) * width},${norm(v)}`)
    .join(" ");
  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      fill="none"
      className={className}
    >
      <polyline
        points={pts}
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export { seeded as seededSparklineValues };
