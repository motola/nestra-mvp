import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Alphacon — Device control",
};

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-bg">
      <header className="bg-graphite px-7 py-4 flex items-center justify-between">
        <span className="font-serif text-[17px] text-white tracking-tight">
          Alphacon
        </span>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
            Organisation
          </span>
          <span className="text-[13px] font-medium text-white">
            Acme Properties
          </span>
        </div>
      </header>

      {/* Tab navigation */}
      <nav className="bg-surface border-b border-border px-7">
        <div className="flex gap-0 max-w-5xl mx-auto">
          <NavTab href="/demo" label="Devices" />
          <NavTab href="/demo/ble" label="Scanner" />
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-7 py-8">{children}</main>
    </div>
  );
}

function NavTab({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="text-[13px] font-medium text-text-2 px-4 py-3 border-b-2 border-transparent hover:text-text hover:border-border-strong transition-colors duration-120"
    >
      {label}
    </Link>
  );
}
