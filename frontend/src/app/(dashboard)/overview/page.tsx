import { Download, Plus, ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { AIBar } from "@/components/ui/ai-bar";
import { StatCard } from "@/components/ui/stat-card";
import { AlertCard } from "@/components/ui/alert-card";
import { Card, MonoLabel, SectionHead } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { QuickQuestions } from "./quick-questions";
import { PROPERTIES } from "@/lib/fixtures";

const ACTIVITY = [
  {
    time: "08:42",
    who: "Agent",
    what: "Turned off heating in Maple Court Flat 3B",
    kind: "ok",
  },
  {
    time: "08:14",
    who: "Agent",
    what: "Detected vacant heating in Maple Court Flat 3B",
    kind: "warn",
  },
  {
    time: "07:30",
    who: "Marcus",
    what: "Approved March report for team email",
    kind: "neutral",
  },
  {
    time: "06:47",
    who: "System",
    what: "Northbrook Mill hub stopped responding",
    kind: "alert",
  },
  {
    time: "Y'day",
    who: "Agent",
    what: "Drafted check-in message for Larkspur House Flat 1",
    kind: "warn",
  },
] as const;

const dotMap: Record<string, string> = {
  ok: "bg-green",
  warn: "bg-amber",
  alert: "bg-red",
  neutral: "bg-text-3",
};

export default function OverviewPage() {
  const totalUnits = PROPERTIES.reduce((s, p) => s + p.units, 0);
  const totalOcc = PROPERTIES.reduce((s, p) => s + p.occupied, 0);
  const occPct = Math.round((totalOcc / totalUnits) * 100);
  const totalAlerts = PROPERTIES.reduce((s, p) => s + p.alerts, 0);

  return (
    <>
      <PageHeader
        eyebrow="WEDNESDAY · 1 APRIL 2026 · 09:14 BST"
        title="Good morning, Marcus"
        sub={`${PROPERTIES.length} properties · ${totalUnits} units · ${totalOcc} occupied · ${totalAlerts} active alerts overnight`}
        primary={
          <Button variant="primary" icon={Plus}>
            Add property
          </Button>
        }
        secondary={
          <Button variant="secondary" icon={Download}>
            Export portfolio
          </Button>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        <AIBar />

        <QuickQuestions />

        {/* Stat strip */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard
            label="Properties"
            value={PROPERTIES.length}
            sub={`${totalUnits} units total`}
          />
          <StatCard
            label="Occupancy"
            value={occPct}
            unit="%"
            sub={
              <>
                <span className="text-green font-medium">↑ 4%</span> vs last
                month
              </>
            }
          />
          <StatCard
            label="Energy spend"
            value="£1,389"
            sub={
              <>
                <span className="text-green font-medium">↓ 12%</span> below
                budget
              </>
            }
          />
          <StatCard
            label="Active alerts"
            value={totalAlerts}
            variant="amber"
            sub={<span className="text-amber font-medium">1 needs review</span>}
          />
        </div>

        {/* Insights */}
        <section>
          <SectionHead
            title="Insights"
            sub="3 FROM AGENT · LAST 24H · PROACTIVE"
            right={
              <Button variant="ghost" size="sm" iconRight={ArrowRight}>
                Ask the agent
              </Button>
            }
          />
          <div className="grid grid-cols-2 gap-3">
            <AlertCard
              severity="amber"
              title="Vacant unit heating on — Maple Court Flat 3B"
              desc="Unit has been vacant for 4 days. Heating running at 20°C. Estimated waste £12/day. I can turn off and set a pre-arrival schedule automatically."
              meta="Energy · Maple Court · Today 08:14 · 94% confidence"
              actions={["Turn off + schedule", "Review unit", "Dismiss"]}
            />
            <AlertCard
              severity="red"
              title="Two thermostats offline — Northbrook Mill"
              desc="Flat 2A and Flat 4B thermostats stopped reporting at 06:47. Tenants haven't messaged. Likely a hub disconnect; remote restart usually resolves it."
              meta="Devices · Northbrook Mill · Today 06:47 · Review needed"
              actions={["Restart hub", "Open device console"]}
            />
            <AlertCard
              severity="amber"
              title="Late check-in flagged — Larkspur House Flat 1"
              desc="Guest's stay began Monday but the front door hasn't been unlocked. The booking is paid. I drafted a friendly check-in message — review before send."
              meta="Stay · Larkspur House · Yesterday 22:11 · 81% confidence"
              actions={["Review draft", "Call guest"]}
            />
            <AlertCard
              severity="graphite"
              title="March report ready"
              desc="Your monthly portfolio report is ready: £1,389 energy across 12 properties, 87% occupancy, 4 maintenance jobs closed. Tap to read the agent's summary."
              meta="Insights · Portfolio · 1 April 2026 · Generated by agent"
              actions={["Read report", "Email to team"]}
            />
          </div>
        </section>

        {/* Bottom split: conversation preview + recent activity */}
        <div
          className="grid gap-3"
          style={{ gridTemplateColumns: "1.4fr 1fr" }}
        >
          {/* Conversation preview */}
          <Card className="p-[18px]">
            <div className="flex items-center gap-2.5 pb-3 border-b border-border">
              <span
                className="w-2 h-2 rounded-full bg-green shrink-0"
                style={{ boxShadow: "0 0 8px rgba(45,107,45,0.4)" }}
              />
              <span className="text-[13px] font-semibold text-text">
                Alphacon AI
              </span>
              <MonoLabel className="ml-auto">
                claude-sonnet-4.6 · operator
              </MonoLabel>
            </div>
            <div className="flex flex-col gap-3.5 pt-3.5">
              <div className="flex items-start gap-3">
                <MonoLabel className="w-6 shrink-0 pt-[2px]">You</MonoLabel>
                <span className="text-[13px] text-text-2 leading-[1.6]">
                  What was my total energy cost last month across all
                  properties?
                </span>
              </div>
              <div className="flex items-start gap-3">
                <span className="font-mono text-[10px] uppercase tracking-[0.08em] w-6 shrink-0 pt-[2px] text-green">
                  AI
                </span>
                <span className="text-[13px] text-text leading-[1.6]">
                  Portfolio used{" "}
                  <strong className="font-semibold">1,247 kWh</strong> in March
                  — <strong className="font-semibold">£1,389 total</strong>, 12%
                  below your £1,580 budget. Maple Court was the largest spend at
                  £298, driven by the vacant unit running heating.
                </span>
              </div>
            </div>
          </Card>

          {/* Recent activity */}
          <Card className="p-4">
            <div className="flex items-center justify-between pb-2.5 border-b border-border">
              <h3 className="text-[13px] font-semibold text-text m-0">
                Recent activity
              </h3>
              <MonoLabel>Last 6h</MonoLabel>
            </div>
            <ul className="list-none m-0 p-0 flex flex-col">
              {ACTIVITY.map((item, i) => (
                <li
                  key={i}
                  className={`flex items-start gap-2.5 py-2.5 ${
                    i < ACTIVITY.length - 1
                      ? "border-b border-dashed border-border"
                      : ""
                  }`}
                >
                  <MonoLabel className="w-14 shrink-0 pt-[2px]">
                    {item.time}
                  </MonoLabel>
                  <span
                    className={`w-1.5 h-1.5 rounded-full mt-[7px] shrink-0 ${dotMap[item.kind]}`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-[12px] text-text leading-[1.45] m-0">
                      {item.what}
                    </p>
                    <MonoLabel className="mt-0.5">{item.who}</MonoLabel>
                  </div>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </div>
    </>
  );
}
