/* TAB: Team (members + roles)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateTeam } = React;

function TeamScreen() {
  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Team"
        sub={`${TEAM.length} members · 4 roles in use · property-scoped access for contractors`}
        primary={<Button variant="primary" icon="plus">Invite member</Button>}
      />

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20}}>
        <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
          <StatCard label="Members" value={TEAM.length} sub="Across 4 roles"/>
          <StatCard label="Pending invites" value="2" sub="Sent in last 7 days"/>
          <StatCard label="Property assignments" value="11" sub="Some scoped + expiring"/>
          <StatCard label="Contractors" value="1" sub={<span style={{color: "var(--amber)"}}>Expires 30 Apr</span>} valueColor="var(--amber)"/>
        </div>

        <DataTable columns={[
          { k: "name", label: "Member", w: "1.5fr", render: r => (
            <div style={{display: "flex", alignItems: "center", gap: 10}}>
              <div style={{
                width: 30, height: 30, borderRadius: "50%", flexShrink: 0,
                background: "var(--graphite)", color: "#ffffff",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 500,
              }}>{r.name.split(" ").map(p => p[0]).join("")}</div>
              <div style={{minWidth: 0}}>
                <div style={{fontSize: 13, fontWeight: 500}}>{r.name}</div>
                <div style={{fontSize: 11, color: "var(--text-3)"}}>{r.email}</div>
              </div>
            </div>
          )},
          { k: "role", label: "Role", w: "1.2fr", render: r => <Tag variant="neutral">{r.role.toLowerCase().replace("_", " ")}</Tag>},
          { k: "scope", label: "Scope", w: "1.8fr", render: r => <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.scope}</span>},
          { k: "last", label: "Last active", w: "1fr", render: r => <span className="t-mono" style={{color: r.last.includes("now") ? "var(--green)" : "var(--text-3)"}}>{r.last}</span>},
          { k: "act", label: "", w: "100px", align: "right", render: () => <Button variant="ghost" size="sm">Manage</Button>},
        ]} rows={TEAM}/>

        <SectionHead title="Role permissions" sub="4 BUILT-IN ROLES · CUSTOM ROLES IN A LATER RELEASE"/>
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12}}>
          {[
            { role: "Owner / Org Admin", desc: "Full access · billing · all portfolios · audit log · agent settings", scope: "Org-wide" },
            { role: "Portfolio Admin",  desc: "Manage their portfolio · invite members · add properties · automations", scope: "One portfolio" },
            { role: "Property Manager", desc: "Manage their property · approve agent actions · view audit",            scope: "Selected properties" },
            { role: "Contractor",       desc: "Big tap targets · time-bound access · device control only",              scope: "One property · expiring" },
          ].map(r => (
            <Card key={r.role} style={{padding: 18}}>
              <div style={{display: "flex", alignItems: "center", justifyContent: "space-between"}}>
                <span style={{fontFamily: "var(--font-serif)", fontSize: 17}}>{r.role}</span>
                <Tag variant="neutral">{r.scope}</Tag>
              </div>
              <div style={{fontSize: 12, color: "var(--text-2)", marginTop: 8, lineHeight: 1.55}}>{r.desc}</div>
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}

/* ============================================================
   AGENT (full chat surface)
   ============================================================ */

Object.assign(window, { TeamScreen });
