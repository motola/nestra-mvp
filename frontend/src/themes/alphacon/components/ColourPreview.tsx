"use client";

// Colour temperature (Kelvin) → approximate RGB for preview
export function kelvinToRgb(kelvin: number): [number, number, number] {
  const t = Math.max(1000, Math.min(12000, kelvin));
  if (t <= 4000) {
    const factor = (t - 1000) / 3000;
    return [
      255,
      Math.round(100 + factor * 128),
      Math.round(40 + factor * 103),
    ];
  }
  if (t <= 6500) {
    const factor = (t - 4000) / 2500;
    return [255, Math.round(228 + factor * 21), Math.round(143 + factor * 110)];
  }
  return [255, 249, 253];
}

// Colour preview swatch
export function ColourPreview({
  r,
  g,
  b,
  brightness = 100,
  size = 40,
}: {
  r: number;
  g: number;
  b: number;
  brightness?: number;
  size?: number;
}) {
  const dimmed = brightness / 100;
  const style = {
    width: size,
    height: size,
    borderRadius: 8,
    backgroundColor: `rgb(${Math.round(r * dimmed)},${Math.round(g * dimmed)},${Math.round(b * dimmed)})`,
    border: "1px solid rgba(0,0,0,0.1)",
    transition: "background-color 0.3s ease",
  };
  return <div style={style} />;
}

// Brightness bar
export function BrightnessBar({
  brightness,
  r = 255,
  g = 210,
  b = 140,
}: {
  brightness: number;
  r?: number;
  g?: number;
  b?: number;
}) {
  return (
    <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-300"
        style={{
          width: `${brightness}%`,
          backgroundColor: `rgb(${r},${g},${b})`,
        }}
      />
    </div>
  );
}
