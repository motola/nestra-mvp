"use client"; // Client: show loading gate while auth hydrates

import { useAuth } from "@/lib/auth/provider";
import { TopNav } from "@/components/layout/top-nav";
import { Sidebar } from "@/components/layout/sidebar";

function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen flex flex-col overflow-hidden bg-bg">
      <TopNav />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-bg">{children}</main>
      </div>
    </div>
  );
}

function LoadingGate({ children }: { children: React.ReactNode }) {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-bg">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 rounded-full border-2 border-border border-t-accent animate-spin" />
          <p className="text-[12px] text-text-3">Loading your workspace…</p>
        </div>
      </div>
    );
  }

  return <DashboardShell>{children}</DashboardShell>;
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <LoadingGate>{children}</LoadingGate>;
}
