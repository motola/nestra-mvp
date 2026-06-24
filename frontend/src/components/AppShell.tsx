"use client";

// Client: chooses the app chrome based on the route and gates the app behind
// auth. Auth routes render bare (no sidebar / header / agent); every other
// route requires a logged-in user, otherwise we redirect to /login.

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { AgentChat } from "@/components/chat/AgentChat";
import { AIBar } from "@/components/chat/AIBar";
import { useAuth } from "@/contexts/AuthContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
import { CommandPalette, Header, Sidebar } from "@/themes";

const BARE_ROUTES = ["/login", "/signup"];

function FullScreenMessage({ label }: { label: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg">
      <p className="font-mono text-xs uppercase tracking-widest text-text-3">
        {label}
      </p>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading } = useAuth();
  const bare = BARE_ROUTES.some((route) => pathname?.startsWith(route));

  useEffect(() => {
    if (!bare && !loading && !user) {
      router.replace("/login");
    }
  }, [bare, loading, user, router]);

  if (bare) {
    return <>{children}</>;
  }

  if (loading) {
    return <FullScreenMessage label="Loading" />;
  }

  if (!user) {
    return <FullScreenMessage label="Redirecting to login" />;
  }

  return (
    <SidebarProvider>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">
          <Header />
          <main className="flex-1 overflow-y-auto bg-bg">
            <AIBar />
            {children}
          </main>
        </div>
      </div>
      <AgentChat />
      <CommandPalette />
    </SidebarProvider>
  );
}
