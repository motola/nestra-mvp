import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AlphaCon — Device Control",
};

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <span className="text-base font-semibold tracking-tight">AlphaCon</span>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500 uppercase tracking-widest">
            Organisation
          </span>
          <span className="text-sm font-medium text-white">
            Acme Properties
          </span>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
