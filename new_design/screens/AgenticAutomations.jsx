/* TAB: Agentic automations
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateAutomations } = React;

function AutomationsScreen({ go }) {
  const [filter, setFilter] = useStateAutomations("all");
  const list = filter === "all" ? AUTOMATIONS
    : filter === "agent" ? AUTOMATIONS.filter(a => a.source === "AGENT")
    : filter === "manual" ? AUTOMATIONS.filter(a => a.source === "MANUAL")
    : filter === "paused" ? AUTOMATIONS.filter(a => !a.enabled)
    : AUTOMATIONS;

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Agentic automations"
        sub="Where the agent's automations live. Set up from the Intelligence pane — or build and tweak them by hand. You stay in control of every trigger and action."
        primary={<Button variant="primary" icon="plus">New automation</Button>}
        secondary={<Button variant="secondary" icon="sparkles" onClick={() => go && go("overview")}>Ask the agent to build one</Button>}
      />

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20}}>
        <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
          <StatCard label="Active" value={AUTOMATIONS.filter(a => a.enabled).length} sub={`${AUTOMATIONS.filter(a => !a.enabled).length} paused`}/>
          <StatCard label="Set by agent" value={AUTOMATIONS.filter(a => a.source === "AGENT").length} sub="From Intelligence" valueColor="var(--graphite)"/>
          <StatCard label="Runs · 24h" value="34" sub="2 awaiting approval"/>
          <StatCard label="New suggestions" value="3" sub="Patterns detected this week" valueColor="var(--graphite)"/>
        </div>

        {/* Agent suggestions — proposed, not yet live */}
        <section style={{
          background: "linear-gradient(180deg, var(--surface) 0%, var(--surface-2) 100%)",
          border: "1px solid var(--border)", borderRadius: 14, padding: 18,
        }}>
          <div style={{display: "flex", alignItems: "center", gap: 8, marginBottom: 14}}>
            <Icon name="sparkles" size={15} color="var(--graphite)"/>
            <h2 style={{fontSize: 16, fontWeight: 600, margin: 0}}>The agent wants to set up 3 automations</h2>
            <span className="t-mono" style={{color: "var(--text-3)", marginLeft: "auto"}}>review · tweak · approve</span>
          </div>
          <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
            {[
              { name: "Weekday pre-arrival schedule", trigger: "Mon–Fri · 16:00",       why: "Occupants return at ~16:30 four of five weekdays. Warming earlier cuts the morning spike." },
              { name: "Quiet hours for Ash Cottage",  trigger: "Daily · 23:00 → 07:00", why: "Short-let in a residential street; volume complaints last quarter." },
              { name: "Weekly leak check ping",       trigger: "Sundays · 09:00",       why: "Reduce time-to-detection with a low-cost reminder." },
            ].map(s => (
              <Card key={s.name} style={{padding: 16}}>
                <div className="t-mono" style={{color: "var(--graphite)"}}>Proposed</div>
                <div style={{fontFamily: "var(--font-serif)", fontSize: 17, marginTop: 8}}>{s.name}</div>
                <div className="t-mono" style={{color: "var(--text-3)", marginTop: 6}}>{s.trigger}</div>
                <div style={{fontSize: 12, color: "var(--text-2)", marginTop: 10, lineHeight: 1.55}}>{s.why}</div>
                <div style={{display: "flex", gap: 8, marginTop: 14}}>
                  <Button variant="tagPrim" size="sm">Approve</Button>
                  <Button variant="tagSec" size="sm">Tweak</Button>
                  <Button variant="tagSec" size="sm">Dismiss</Button>
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* Live automations with source filter */}
        <SectionHead title="Live automations" sub="TRIGGER → CONDITIONS → ACTIONS · EDIT ANY BY HAND"
          right={
            <div style={{display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap"}}>
              {[
                ["all", "All", AUTOMATIONS.length],
                ["agent", "Set by agent", AUTOMATIONS.filter(a => a.source === "AGENT").length],
                ["manual", "Manual", AUTOMATIONS.filter(a => a.source === "MANUAL").length],
                ["paused", "Paused", AUTOMATIONS.filter(a => !a.enabled).length],
              ].map(([id, label, n]) => (
                <button key={id} onClick={() => setFilter(id)} style={{
                  background: filter === id ? "var(--graphite)" : "var(--surface)",
                  color: filter === id ? "#ffffff" : "var(--text-2)",
                  border: `1px solid ${filter === id ? "var(--graphite)" : "var(--border)"}`,
                  borderRadius: 9, padding: "5px 11px", cursor: "pointer",
                  fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 500,
                  display: "inline-flex", alignItems: "center", gap: 7,
                }}>
                  {label}
                  <span style={{fontFamily: "var(--font-mono)", fontSize: 10}}>{n}</span>
                </button>
              ))}
            </div>
          }/>
        <AutomationList items={list}/>
      </div>
    </>
  );
}

function AutomationList({ items }) {
  return (
    <div style={{display: "flex", flexDirection: "column", gap: 8}}>
      {items.map(a => (
        <Card key={a.id} hoverable style={{padding: 18}}>
          <div style={{display: "flex", alignItems: "center", gap: 16}}>
            <div style={{
              width: 36, height: 36, borderRadius: 8, flexShrink: 0,
              background: a.enabled ? "var(--graphite)" : "var(--surface-2)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Icon name={a.source === "AGENT" ? "sparkles" : "bolt"} size={16} color={a.enabled ? "#ffffff" : "var(--text-3)"}/>
            </div>

            <div style={{flex: 1, minWidth: 0}}>
              <div style={{display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap"}}>
                <span style={{fontFamily: "var(--font-serif)", fontSize: 18}}>{a.name}</span>
                {a.source === "AGENT"
                  ? <Tag variant="graphite" withDot>Set by agent</Tag>
                  : <Tag variant="neutral">Manual</Tag>}
                {!a.enabled && <Tag variant="neutral">paused</Tag>}
              </div>
              <div style={{display: "flex", gap: 14, marginTop: 8, fontSize: 12, color: "var(--text-2)", flexWrap: "wrap"}}>
                <span><strong style={{color: "var(--text-3)", fontWeight: 500, fontFamily: "var(--font-mono)", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em"}}>trigger</strong>&nbsp; {a.trigger}</span>
                <span><strong style={{color: "var(--text-3)", fontWeight: 500, fontFamily: "var(--font-mono)", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em"}}>actions</strong>&nbsp; {a.actions}</span>
                <span><strong style={{color: "var(--text-3)", fontWeight: 500, fontFamily: "var(--font-mono)", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em"}}>scope</strong>&nbsp; {a.scope}</span>
                <span><strong style={{color: "var(--text-3)", fontWeight: 500, fontFamily: "var(--font-mono)", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em"}}>last run</strong>&nbsp; {a.lastRun}</span>
              </div>
            </div>

            <Button variant="ghost" size="sm" icon="settings">Tweak</Button>

            <div style={{textAlign: "right", flexShrink: 0}}>
              <div className="tnum" style={{fontFamily: "var(--font-mono)", fontSize: 16, fontWeight: 600}}>{a.runs}</div>
              <div className="t-mono" style={{color: "var(--text-3)", marginTop: 2}}>runs · 90d</div>
            </div>

            <div style={{
              width: 44, height: 24, borderRadius: 12, flexShrink: 0, position: "relative",
              background: a.enabled ? "var(--graphite)" : "var(--surface-2)",
              border: a.enabled ? "none" : "1px solid var(--border)",
              cursor: "pointer",
            }}>
              <div style={{
                position: "absolute", top: 2, left: a.enabled ? 22 : 2,
                width: 18, height: 18, borderRadius: "50%", background: "#ffffff",
                transition: "left var(--motion) var(--ease-default)",
                boxShadow: "0 1px 2px rgba(16,24,40,0.2)",
              }}/>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

/* ============================================================
   AUDIT
   ============================================================ */

Object.assign(window, { AutomationsScreen });
