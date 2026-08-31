"use client"; // Client: team management and invites

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Card, SectionHead } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { PageHeader } from "@/components/ui/page-header";
import { InviteMemberForm } from "@/components/team/invite-member-form";
import { logger } from "@/lib/logger";

// ─── Role permission cards ────────────────────────────────────────────────────

const ROLES = [
  {
    role: "Organization Admin",
    desc: "Full access · billing · all portfolios · audit log · agent settings",
    scope: "Org-wide",
  },
  {
    role: "Portfolio Admin",
    desc: "Manage their portfolio · invite members · add properties · automations",
    scope: "One portfolio",
  },
  {
    role: "Portfolio Manager",
    desc: "View portfolio data · manage team members in portfolio",
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
  const [showInviteForm, setShowInviteForm] = useState(false);

  function handleInviteMember(data: { email: string; role: string }) {
    // TODO: Call backend API to send invite
    logger.info("Inviting member:", data);
    setShowInviteForm(false);
  }

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Team"
        sub="Invite members to collaborate on your workspace"
        primary={
          <Button
            variant="primary"
            icon={Plus}
            onClick={() => setShowInviteForm(true)}
          >
            Invite member
          </Button>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        <div className="grid grid-cols-4 gap-3">
          <StatCard label="Members" value="0" sub="You're the only one" />
          <StatCard label="Pending invites" value="0" sub="None yet" />
          <StatCard label="Active roles" value="5" sub="Available for team" />
        </div>

        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">
            No team members yet
          </p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            Click &quot;Invite member&quot; to add collaborators to your
            workspace.
          </p>
        </div>

        <SectionHead
          title="Role permissions"
          sub="5 BUILT-IN ROLES · CUSTOM ROLES IN A LATER RELEASE"
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

      {showInviteForm && (
        <InviteMemberForm
          onClose={() => setShowInviteForm(false)}
          onSubmit={handleInviteMember}
        />
      )}
    </>
  );
}
