export interface DemoDevice {
  id: string;
  provider: "lifx" | "govee";
  name: string;
  power: boolean;
  brightness: number | null;
  reachable: boolean;
  model: string | null;
}

export interface ActivityEntry {
  id: string;
  message: string;
  time: Date;
}

export function formatRelativeTime(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 10) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  return `${Math.floor(minutes / 60)}h ago`;
}
