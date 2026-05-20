import type { Metadata } from "next";
import { DM_Sans, DM_Mono, Instrument_Serif } from "next/font/google";
import { Toaster } from "react-hot-toast";
import "./globals.css";
import { Providers } from "./providers";
import { SidebarProvider } from "@/contexts/SidebarContext";
import { Sidebar, Header, CommandPalette } from "@/themes";
import { AgentChat } from "@/components/chat/AgentChat";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  weight: ["300", "400", "500"],
  display: "swap",
});

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  variable: "--font-instrument-serif",
  weight: "400",
  style: ["normal", "italic"],
  display: "swap",
});

const dmMono = DM_Mono({
  subsets: ["latin"],
  variable: "--font-dm-mono",
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Nestra",
  description: "Smart property intelligence for property managers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${dmSans.variable} ${instrumentSerif.variable} ${dmMono.variable}`}
    >
      <body className="bg-bg text-text font-body antialiased h-full">
        <Providers>
          <SidebarProvider>
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              <div className="flex-1 flex flex-col overflow-hidden min-w-0">
                <Header />
                <main className="flex-1 overflow-y-auto bg-bg">{children}</main>
              </div>
            </div>
            <AgentChat />
            <CommandPalette />
          </SidebarProvider>
        </Providers>
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#fbf9f4",
              border: "1px solid #e0dbcf",
              color: "#1a1814",
              fontFamily: "var(--font-dm-sans)",
              fontSize: "14px",
              borderRadius: "12px",
              padding: "12px 16px",
            },
          }}
        />
      </body>
    </html>
  );
}
