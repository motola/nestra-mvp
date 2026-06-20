/* VIEW: Full agent chat surface (opened from Intelligence)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateAgent } = React;

function AgentScreen({ go }) {
  return (
    <>
      <PageHeader
        eyebrow={<span style={{color: "var(--graphite)"}}>● ALPHACON AI · OPERATOR PERSONA · CLAUDE-SONNET-4.6</span>}
        title="Agent"
        sub="Ask anything about your portfolio. I'll use the tools available to me to answer — and I'll always show what I did."
        primary={<Button variant="primary" icon="plus">New conversation</Button>}
        secondary={<Button variant="secondary" icon="history">History</Button>}
      />

      <div style={{padding: "20px 28px 32px", display: "grid", gridTemplateColumns: "260px 1fr 280px", gap: 16, alignItems: "start"}}>
        <Card style={{padding: 14, display: "flex", flexDirection: "column", gap: 10}}>
          <div className="t-mono" style={{color: "var(--text-3)", padding: "4px 6px"}}>Recent</div>
          {[
            { t: "Energy spend this week",       when: "12 min ago", active: true },
            { t: "Northbrook hub restart",       when: "1h ago" },
            { t: "Maple Court vacancy options",  when: "yesterday" },
            { t: "Why is Hue offline?",          when: "yesterday" },
            { t: "March portfolio report",       when: "2 days ago" },
            { t: "Larkspur late check-in",      when: "5 days ago" },
          ].map(c => (
            <div key={c.t} style={{
              padding: "8px 10px", borderRadius: 9, cursor: "pointer",
              background: c.active ? "var(--bg)" : "transparent",
              border: c.active ? "1px solid var(--border)" : "1px solid transparent",
            }}>
              <div style={{fontSize: 13, color: c.active ? "var(--text)" : "var(--text-2)", fontWeight: c.active ? 600 : 400}}>{c.t}</div>
              <div className="t-mono" style={{color: "var(--text-3)", marginTop: 3}}>{c.when}</div>
            </div>
          ))}
        </Card>

        <Card style={{padding: 24, display: "flex", flexDirection: "column", gap: 22, minHeight: 600}}>
          <div style={{display: "flex", alignItems: "center", gap: 10, paddingBottom: 14, borderBottom: "1px solid var(--border)"}}>
            <span style={{width:8, height:8, borderRadius:"50%", background:"var(--green)", boxShadow:"0 0 8px rgba(6,118,71,0.4)"}}/>
            <span style={{fontSize: 13, fontWeight: 600}}>Energy spend this week</span>
            <span className="t-mono" style={{color: "var(--text-3)", marginLeft: "auto"}}>3 messages · 1 tool call</span>
          </div>

          <ConvoTurn role="you" text="What was my total energy spend last week and where did most of it go?"/>

          <ToolRibbon name="get_portfolio_energy" args="{ range: 'last_week', group_by: 'property' }" status="ok" duration="412 ms" rows="12 properties"/>

          <ConvoTurn role="ai">
            Portfolio used <strong>312 kWh</strong> last week — <strong>£77.20 total</strong>, 8% below your weekly average. Three things worth flagging:
            <ul style={{margin: "12px 0 0", paddingLeft: 18, display: "flex", flexDirection: "column", gap: 6, fontSize: 13, lineHeight: 1.6}}>
              <li><strong>Maple Court · £19.40</strong> — driven mostly by Flat 3B running heating while vacant. I turned that off Wednesday morning.</li>
              <li><strong>Northbrook Mill · £16.10</strong> — running normal for occupancy.</li>
              <li><strong>Heron Place · £14.70</strong> — usage spiked Friday evening, likely a gathering in Flat 7. No automation triggered.</li>
            </ul>
            <div style={{marginTop: 14, paddingTop: 14, borderTop: "1px dashed var(--border)", fontSize: 12, color: "var(--text-3)", display: "flex", justifyContent: "space-between"}}>
              <span>Want me to email this as a weekly summary every Monday?</span>
              <span style={{fontFamily: "var(--font-mono)"}}>1,212 in · 218 out · cached 89%</span>
            </div>
          </ConvoTurn>

          <ConvoTurn role="you" text="Yes, set that up — send it to me and Theo every Monday at 08:00."/>

          <ConvoTurn role="ai">
            I can create an automation that runs every Monday 08:00, generates the same energy summary, and emails it to <strong>marcus@chen.holdings</strong> and <strong>theo@chen.holdings</strong>. <strong>Confirm before I save it?</strong>
            <div style={{display: "flex", gap: 8, marginTop: 14}}>
              <Button variant="tagPrim" size="sm">Yes, create it</Button>
              <Button variant="tagSec" size="sm">Add Rina too</Button>
              <Button variant="tagSec" size="sm">No</Button>
            </div>
          </ConvoTurn>

          <div style={{marginTop: "auto"}}>
            <AIBar compact placeholder="Reply…" chips={["audit","sources","tools"]}/>
            <div style={{display: "flex", justifyContent: "space-between", marginTop: 8, fontSize: 11, color: "var(--text-3)"}}>
              <span>Operator persona · sees all property-owned devices across the portfolio</span>
              <span style={{fontFamily: "var(--font-mono)"}}>⏎ to send · ⌘⏎ to send + run</span>
            </div>
          </div>
        </Card>

        <Card style={{padding: 16, display: "flex", flexDirection: "column", gap: 14}}>
          <div className="t-mono" style={{color: "var(--text-3)"}}>This conversation</div>
          <div style={{display: "flex", flexDirection: "column", gap: 10, fontSize: 12}}>
            <Row k="persona" v="Operator"/>
            <Row k="model"   v="Sonnet 4.6"/>
            <Row k="device scope" v="14 property-owned · Maple Court"/>
            <Row k="tools enabled" v="9 of 23"/>
            <Row k="cost so far"  v="£0.034"/>
          </div>

          <div style={{height: 1, background: "var(--border)"}}/>

          <div>
            <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 8}}>Tools used</div>
            <div style={{display: "flex", flexDirection: "column", gap: 6}}>
              {["get_portfolio_energy","list_properties","get_property_devices"].map(t => (
                <div key={t} style={{
                  fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-2)",
                  padding: "5px 9px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6,
                }}>{t}</div>
              ))}
            </div>
          </div>

          <div style={{height: 1, background: "var(--border)"}}/>

          <div>
            <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 8}}>Recent sources</div>
            <div style={{display: "flex", flexDirection: "column", gap: 8}}>
              {[
                { t: "Energy snapshot", s: "today 07:30", k: "system" },
                { t: "Flat 3B vacancy",  s: "Stay s7 · completed 29 Mar", k: "stay" },
                { t: "Heron party hint", s: "Energy spike + motion · Fri 21:14", k: "memory" },
              ].map(s => (
                <div key={s.t} style={{padding: "8px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 9}}>
                  <div style={{fontSize: 12, fontWeight: 500}}>{s.t}</div>
                  <div className="t-mono" style={{color: "var(--text-3)", marginTop: 2}}>{s.k} · {s.s}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}

function Row({ k, v }) {
  return (
    <div style={{display: "flex", justifyContent: "space-between", gap: 12}}>
      <span style={{color: "var(--text-3)", fontFamily: "var(--font-mono)", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em"}}>{k}</span>
      <span style={{color: "var(--text)", textAlign: "right", flex: 1}}>{v}</span>
    </div>
  );
}

function ConvoTurn({ role, text, children }) {
  const isAI = role === "ai";
  return (
    <div style={{display: "flex", gap: 14, alignItems: "flex-start"}}>
      <span className="t-mono" style={{
        color: isAI ? "var(--green)" : "var(--text-3)",
        width: 32, flexShrink: 0, paddingTop: 2,
      }}>{isAI ? "AI" : "You"}</span>
      <div style={{flex: 1, fontSize: 13, lineHeight: 1.65, color: isAI ? "var(--text)" : "var(--text-2)"}}>
        {text}{children}
      </div>
    </div>
  );
}

function ToolRibbon({ name, args, status, duration, rows }) {
  return (
    <div style={{
      padding: "12px 14px", borderRadius: 9,
      background: "var(--bg)", border: "1px solid var(--border)",
      display: "flex", alignItems: "center", gap: 12,
      marginLeft: 46,
    }}>
      <Icon name="bolt" size={14} color="var(--graphite)"/>
      <div style={{flex: 1, minWidth: 0}}>
        <div style={{display: "flex", alignItems: "center", gap: 8}}>
          <span style={{fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 500}}>{name}</span>
          <Tag variant={status === "ok" ? "ok" : "alert"} withDot>{status}</Tag>
        </div>
        <div style={{fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-3)", marginTop: 4, textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap"}}>
          {args}
        </div>
      </div>
      <div style={{textAlign: "right"}}>
        <div className="t-mono" style={{color: "var(--text-3)"}}>{duration} · {rows}</div>
      </div>
    </div>
  );
}

Object.assign(window, { AgentScreen });
