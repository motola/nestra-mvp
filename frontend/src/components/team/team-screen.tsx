"use client"; // Client: passes render functions to DataTable

import { Plus } from "lucide-react";
import { TEAM } from "@/lib/fixtures";
import type { TeamMember } from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";

// ─── Initials avatar ──────────────────────────────────────────────────────────

function Avatar({ name }: { name: string }) {
  const initials = name
    .split(" ")
    .map((p) => p[0])
    .join("");
  return (
    <div className="w-[30px] h-[30px] rounded-full bg-graphite text-white flex items-center justify-center font-mono text-[11px] font-medium shrink-0">
      {initials}
    </div>
  );
}

// ─── Table columns ────────────────────────────────────────────────────────────

const COLUMNS: TableColumn<TeamMember>[] = [
  {
    k: "name",
    label: "Member",
    w: "1.5fr",
    render: (r) => (
      <div className="flex items-center gap-2.5">
        <Avatar name={r.name} />
        <div className="min-w-0">
          <p className="text-[13px] font-medium text-text m-0">{r.name}</p>
          <p className="text-[11px] text-text-3 m-0">{r.email}</p>
        </div>
      </div>
    ),
  },
  {
    k: "role",
    label: "Role",
    w: "1.2fr",
    render: (r) => (
      <Tag variant="neutral">{r.role.toLowerCase().replace(/_/g, " ")}</Tag>
    ),
  },
  {
    k: "scope",
    label: "Scope",
    w: "1.8fr",
    render: (r) => <span className="text-[12px] text-text-2">{r.scope}</span>,
  },
  {
    k: "last",
    label: "Last active",
    w: "1fr",
    render: (r) => (
      <MonoLabel className={r.last.includes("now") ? "text-green" : ""}>
        {r.last}
      </MonoLabel>
    ),
  },
  {
    k: "act",
    label: "",
    w: "100px",
    align: "right",
    render: () => (
      <Button variant="ghost" size="sm">
        Manage
      </Button>
    ),
  },
];

// ─── Role permission cards ────────────────────────────────────────────────────

const ROLES = [
  {
    role: "Owner / Org Admin",
    desc: "Full access · billing · all portfolios · audit log · agent settings",
    scope: "Org-wide",
  },
  {
    role: "Portfolio Admin",
    desc: "Manage their portfolio · invite members · add properties · automations",
    scope: "One portfolio",
  },
  {
    role: "Property Manager",
    desc: "Manage their property · approve agent actions · view audit",
    scope: "Selected properties",
  },
  {
    role: "Contractor",
    desc: "Big tap targets · time-bound access · device control only",
    scope: "One property · expiring",
  },
];

// ─── Main export ──────────────────────────────────────────────────────────────

export function TeamScreen() {
  const contractors = TEAM.filter((m) => m.role === "CONTRACTOR").length;

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Team"
        sub={`${TEAM.length} members · 4 roles in use · property-scoped access for contractors`}
        primary={
          <Button variant="primary" icon={Plus}>
            Invite member
          </Button>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        <div className="grid grid-cols-4 gap-3">
          <StatCard label="Members" value={TEAM.length} sub="Across 4 roles" />
          <StatCard
            label="Pending invites"
            value={2}
            sub="Sent in last 7 days"
          />
          <StatCard
            label="Property assignments"
            value={11}
            sub="Some scoped + expiring"
          />
          <StatCard
            label="Contractors"
            value={contractors}
            variant="amber"
            sub={<span className="text-amber">Expires 30 Apr</span>}
          />
        </div>

        <DataTable columns={COLUMNS} rows={TEAM} />

        <SectionHead
          title="Role permissions"
          sub="4 BUILT-IN ROLES · CUSTOM ROLES IN A LATER RELEASE"
        />
        <div className="grid grid-cols-2 gap-3">
          {ROLES.map((r) => (
            <Card key={r.role} className="p-[18px]">
              <div className="flex items-center justify-between">
                <span className="font-serif text-[17px] text-text">
                  {r.role}
                </span>
                <Tag variant="neutral">{r.scope}</Tag>
              </div>
              <p className="text-[12px] text-text-2 mt-2 leading-[1.55] m-0">
                {r.desc}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}
