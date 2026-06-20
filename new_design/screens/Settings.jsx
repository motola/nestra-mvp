/* TAB: Settings (org, portfolios, billing, security, API, agent persona, audit log)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateSettings } = React;

function AuditLogBody({ go, rows = AUDIT, scopeLabel }) {
  const resourceTarget = (resource) => {
    if (/^Device/.test(resource)) return { pane: "devices", label: "Open device", icon: "devices" };
    if (/^Integration/.test(resource)) return { pane: "integrations", label: "Open integration", icon: "plug" };
    if (/^Automation/.test(resource) || /cool-down|protection|warm-up|summary/i.test(resource)) return { pane: "automations", label: "Open automation", icon: "bolt" };
    if (/^User/.test(resource) || /Property Manager|Tenant/.test(resource)) return { pane: "team", label: "Open member", icon: "users" };
    if (/^Insight|report/i.test(resource)) return { pane: "overview", label: "Open insight", icon: "sparkles" };
    return null;
  };

  return (
    <div style={{display: "flex", flexDirection: "column", gap: 16}}>
      {/* Resource search — jump to a device, integration or automation directly */}
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 9,
        padding: "8px 12px", display: "flex", alignItems: "center", gap: 10,
      }}>
        <Icon name="search" size={14} color="var(--text-3)"/>
        <span style={{fontSize: 12, color: "var(--text-3)", flex: 1}}>Search the log by resource — e.g. “Living thermostat”, “SmartThings”, “vacant cool-down” — to open it directly</span>
        <span className="t-mono" style={{color: "var(--text-3)", border: "1px solid var(--border)", padding: "1px 6px", borderRadius: 4}}>⌘ K</span>
      </div>

      <div style={{display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap"}}>
        <Tag variant="graphite">All actors</Tag>
        <Tag variant="neutral">Team</Tag>
        <Tag variant="neutral">Agent</Tag>
        <Tag variant="neutral">Automations</Tag>
        <Tag variant="neutral">System</Tag>
        <Tag variant="neutral">Vendor webhooks</Tag>
        <div style={{flex: 1}}/>
        <span className="t-mono" style={{color: "var(--text-3)"}}>{scopeLabel || "showing 10 of 14,827 events · last 90 days"}</span>
      </div>

      <DataTable columns={[
        { k: "time", label: "Time", w: "140px", render: r => <span className="t-mono" style={{color: "var(--text-3)"}}>{r.time}</span>},
        { k: "actor", label: "Actor", w: "160px", render: r => (
          <div style={{display: "flex", alignItems: "center", gap: 8}}>
            <span style={{
              width: 18, height: 18, borderRadius: 4, flexShrink: 0,
              display: "flex", alignItems: "center", justifyContent: "center",
              background: { AGENT: "var(--graphite)", AUTOMATION: "var(--surface-2)", USER: "var(--surface-2)", TENANT: "var(--green-bg)", SYSTEM: "var(--surface-2)", VENDOR: "var(--amber-bg)" }[r.actor.kind],
              color: r.actor.kind === "AGENT" ? "#ffffff" : "var(--text-2)",
            }}>
              <Icon name={{ AGENT: "sparkles", AUTOMATION: "bolt", USER: "user", TENANT: "user", SYSTEM: "settings", VENDOR: "plug" }[r.actor.kind]} size={11}/>
            </span>
            <span style={{fontSize: 12, fontWeight: 500}}>{r.actor.name}</span>
          </div>
        )},
        { k: "action", label: "Action", w: "1fr", render: r => <span style={{fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text)"}}>{r.action}</span>},
        { k: "resource", label: "Resource", w: "1.6fr", render: r => {
          const t = resourceTarget(r.resource);
          if (!t) return <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.resource}</span>;
          return (
            <button
              onClick={(e) => { e.stopPropagation(); go && go(t.pane); }}
              title={t.label}
              style={{
                display: "inline-flex", alignItems: "center", gap: 7, maxWidth: "100%",
                background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 7,
                padding: "4px 9px", cursor: "pointer", fontFamily: "var(--font-sans)",
                transition: "border-color var(--motion-fast)",
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = "var(--border-strong)"}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = "var(--border)"}
            >
              <Icon name={t.icon} size={12} color="var(--text-3)"/>
              <span style={{fontSize: 12, color: "var(--text)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"}}>{r.resource}</span>
              <Icon name="arrow" size={11} color="var(--text-3)"/>
            </button>
          );
        }},
        { k: "meta", label: "Meta · owner snapshot", w: "1.9fr", wrap: true, render: r => <span style={{fontSize: 11, color: "var(--text-3)", lineHeight: 1.5}}>{r.meta}</span>},
      ]} rows={rows}/>
    </div>
  );
}

/* ============================================================
   SETTINGS
   ============================================================ */

function SettingsScreen({ go, initialTab }) {
  const [tab, setTab] = useStateSettings(initialTab || "organization");
  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Settings"
        sub="Organization, billing, security, audit log, and developer settings"
      />

      <div style={{padding: "0 28px", borderBottom: "1px solid var(--border)", background: "var(--surface)"}}>
        <Tabs value={tab} onChange={setTab} tabs={[
          { id: "organization", label: "Organization" },
          { id: "portfolios",   label: "Portfolios",   count: 2 },
          { id: "billing",      label: "Billing" },
          { id: "security",     label: "Security" },
          { id: "audit",        label: "Audit log" },
          { id: "api",          label: "API & webhooks" },
          { id: "agent",        label: "Agent" },
        ]}/>
      </div>

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20, maxWidth: tab === "audit" ? 1200 : 920}}>
        {tab === "organization" && <SettingsOrg/>}
        {tab === "portfolios" && <SettingsPortfolios/>}
        {tab === "billing" && <SettingsBilling/>}
        {tab === "security" && <SettingsSecurity/>}
        {tab === "audit" && (
          <>
            <Card style={{padding: "16px 18px"}}>
              <div style={{display:"flex", alignItems:"center", justifyContent:"space-between", paddingBottom: 10, borderBottom: "1px solid var(--border)"}}>
                <h3 style={{fontSize: 13, fontWeight: 600, margin: 0}}>Recent activity</h3>
                <MonoLabel>Last 6h · live</MonoLabel>
              </div>
              <ActivityList/>
            </Card>
            <SectionHead title="Audit log"
              sub="EVERY ACTION ACROSS THE ORG · JUMP TO ANY RESOURCE IT TOUCHED · 90-DAY RETENTION ON GROWTH"
              right={<><Button variant="secondary" size="sm" icon="filter">Filters</Button><Button variant="primary" size="sm" icon="download">Export CSV</Button></>}/>
            <AuditLogBody go={go}/>
          </>
        )}
        {tab === "api" && <SettingsApi/>}
        {tab === "agent" && <SettingsAgent/>}
      </div>
    </>
  );
}

function SettingsCard({ title, sub, children, footer }) {
  return (
    <Card style={{padding: 20, display: "flex", flexDirection: "column", gap: 16}}>
      <div>
        <h3 style={{fontSize: 14, fontWeight: 600, margin: 0}}>{title}</h3>
        {sub && <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 4, lineHeight: 1.55}}>{sub}</div>}
      </div>
      {children}
      {footer && <div style={{display: "flex", justifyContent: "flex-end", borderTop: "1px solid var(--border)", paddingTop: 14, marginTop: 4}}>{footer}</div>}
    </Card>
  );
}

function SettingsOrg() {
  return (
    <>
      <SettingsCard title="Organization profile" sub="Visible to teammates. Tenants see only the display name." footer={<Button variant="primary" size="sm">Save changes</Button>}>
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14}}>
          <Field label="Display name"><TextInput value="Chen Property Holdings"/></Field>
          <Field label="Legal name"><TextInput value="Chen Holdings Ltd"/></Field>
          <Field label="URL slug" hint="alphacon.ai/o/chen-holdings"><TextInput value="chen-holdings"/></Field>
          <Field label="Default timezone"><SelectInput value="Europe/London" options={["Europe/London","Europe/Paris","UTC"]}/></Field>
        </div>
      </SettingsCard>

      <SettingsCard title="Defaults" sub="Applied when creating new properties or stays.">
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14}}>
          <Field label="Default property type"><SelectInput value="Mixed-use" options={["Short-term","Long-term","Mixed-use","Commercial"]}/></Field>
          <Field label="Default currency"><SelectInput value="GBP" options={["GBP","EUR","USD"]}/></Field>
          <Field label="Energy provider"><TextInput value="Octopus Energy"/></Field>
          <Field label="Per-kWh rate" hint="Used for estimates only"><TextInput value="0.247"/></Field>
        </div>
      </SettingsCard>

      <SettingsCard title="Danger zone" sub="Permanently delete this organization and all data." footer={<Button variant="destructive" size="sm">Delete organization</Button>}/>
    </>
  );
}

function SettingsPortfolios() {
  const rows = [
    { name: "Northern Portfolio", properties: 9, members: 4, region: "North England + Scotland", default: true },
    { name: "Southern Portfolio", properties: 3, members: 2, region: "London + South West", default: false },
  ];
  return (
    <>
      <SectionHead title="Portfolios" sub="LEVEL 2 · GROUPS PROPERTIES UNDER A REGIONAL TEAM"
        right={<Button variant="primary" size="sm" icon="plus">New portfolio</Button>}/>
      <DataTable columns={[
        { k: "name", label: "Portfolio", w: "1.4fr", render: r => (
          <div style={{display: "flex", alignItems: "center", gap: 8}}>
            <span style={{fontFamily: "var(--font-serif)", fontSize: 16}}>{r.name}</span>
            {r.default && <Tag variant="neutral">default</Tag>}
          </div>
        )},
        { k: "region", label: "Region", w: "1.4fr", render: r => <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.region}</span>},
        { k: "properties", label: "Properties", w: "0.8fr", align: "right", render: r => <span className="tnum">{r.properties}</span>},
        { k: "members", label: "Members", w: "0.8fr", align: "right", render: r => <span className="tnum">{r.members}</span>},
        { k: "act", label: "", w: "100px", align: "right", render: () => <Button variant="ghost" size="sm">Manage</Button>},
      ]} rows={rows}/>
    </>
  );
}

function SettingsBilling() {
  return (
    <>
      <Card style={{padding: 22, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20}}>
        <div>
          <MonoLabel>Current plan</MonoLabel>
          <div style={{fontFamily: "var(--font-serif)", fontSize: 28, marginTop: 6}}>Growth</div>
          <div style={{fontSize: 13, color: "var(--text-2)", marginTop: 4}}>£89 per portfolio · monthly · 2 portfolios billed</div>
          <div style={{display: "flex", gap: 8, marginTop: 16}}>
            <Button variant="primary" size="sm">Upgrade to Scale</Button>
            <Button variant="ghost" size="sm">View invoices</Button>
          </div>
        </div>
        <div>
          <MonoLabel>April 2026 · projected</MonoLabel>
          <div style={{fontFamily: "var(--font-serif)", fontSize: 28, marginTop: 6, fontFeatureSettings: "'tnum'"}}>£178.00</div>
          <div style={{fontSize: 13, color: "var(--text-3)", marginTop: 4}}>billed 1 May · ending 4242</div>
          <div style={{display: "flex", gap: 12, marginTop: 16, fontSize: 12, color: "var(--text-2)"}}>
            <span>2 portfolios</span><span>·</span><span>12 properties</span><span>·</span><span>14 seats</span>
          </div>
        </div>
      </Card>

      <SettingsCard title="Agent usage" sub="Pay-as-you-go on top of subscription · billed monthly · view ledger for line items.">
        <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
          <StatCard label="Conversations · April" value="312" sub="Across 4 personas"/>
          <StatCard label="Input tokens" value="1.42M" sub="92% cached"/>
          <StatCard label="Output tokens" value="318K"/>
          <StatCard label="Cost · April" value="£24.12" sub="£12.40 last month"/>
        </div>
      </SettingsCard>
    </>
  );
}

function SettingsSecurity() {
  return (
    <>
      <SettingsCard title="Authentication" sub="Choose what your team can use to sign in.">
        {[
          { l: "Email + password", on: true, hint: "Min 12 chars · zxcvbn ≥ 3" },
          { l: "Magic link",       on: true, hint: "15-minute single-use links" },
          { l: "Google SSO",       on: true, hint: "*.chen.holdings only" },
          { l: "Apple SSO",        on: false, hint: "Not enabled" },
          { l: "Hardware key (FIDO2)", on: false, hint: "Coming soon" },
        ].map(r => (
          <div key={r.l} style={{display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)"}}>
            <div>
              <div style={{fontSize: 13, fontWeight: 500}}>{r.l}</div>
              <div style={{fontSize: 11, color: "var(--text-3)", marginTop: 2}}>{r.hint}</div>
            </div>
            <Tag variant={r.on ? "ok" : "neutral"} withDot>{r.on ? "on" : "off"}</Tag>
          </div>
        ))}
      </SettingsCard>

      <SettingsCard title="Sessions" sub="Active sessions across browsers + the Alphacon mobile app.">
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12}}>
          {[
            { device: "MacBook · Chrome", where: "Leeds · 78.43.x.x", when: "now", current: true },
            { device: "iPhone · Alphacon app", where: "Leeds · LTE", when: "5h ago" },
            { device: "iPad · Safari", where: "Manchester", when: "3d ago" },
          ].map(s => (
            <div key={s.device} style={{padding: 12, border: "1px solid var(--border)", borderRadius: 9, background: "var(--bg)"}}>
              <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                <span style={{fontSize: 13, fontWeight: 500}}>{s.device}</span>
                {s.current && <Tag variant="ok">current</Tag>}
              </div>
              <div style={{fontSize: 11, color: "var(--text-3)", marginTop: 4}}>{s.where} · {s.when}</div>
            </div>
          ))}
        </div>
      </SettingsCard>
    </>
  );
}

function SettingsApi() {
  return (
    <>
      <SettingsCard title="Webhooks · outbound" sub="Subscribe your services to events from Alphacon. Coming in 1.5.">
        <div style={{padding: 18, border: "1px dashed var(--border)", borderRadius: 9, textAlign: "center", color: "var(--text-3)", fontSize: 12}}>
          Outbound webhooks not available on the Growth plan. Available on Scale and above.
        </div>
      </SettingsCard>

      <SettingsCard title="API keys" sub="Server-to-server access for your own dashboards or imports." footer={<Button variant="primary" size="sm" icon="plus">Generate key</Button>}>
        <DataTable columns={[
          { k: "name", label: "Name", w: "1fr"},
          { k: "preview", label: "Preview", w: "1fr", render: r => <span style={{fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-3)"}}>{r.preview}</span>},
          { k: "scope", label: "Scope", w: "1fr"},
          { k: "last", label: "Last used", w: "1fr", render: r => <span className="t-mono" style={{color: "var(--text-3)"}}>{r.last}</span>},
          { k: "act", label: "", w: "80px", align: "right", render: () => <Button variant="ghost" size="sm">Revoke</Button>},
        ]} rows={[
          { name: "Reporting pipeline", preview: "ac_live_••••8j2k", scope: "read:portfolio", last: "today 07:30" },
          { name: "Internal CRM sync",  preview: "ac_live_••••f3m1", scope: "read:stays",   last: "yesterday" },
        ]}/>
      </SettingsCard>
    </>
  );
}

function SettingsAgent() {
  return (
    <>
      <SettingsCard title="Routing" sub="The agent picks a model tier based on the question's complexity. You can lock the floor.">
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
          {[
            { tier: "HAIKU",  label: "Haiku 4.5",  use: "Status lookups · single tool",  cost: "£0.001 / msg", on: true },
            { tier: "SONNET", label: "Sonnet 4.6", use: "Reasoning · multi-step plans",  cost: "£0.012 / msg", on: true, recommended: true },
            { tier: "OPUS",   label: "Opus 4.5",   use: "Complex analytics · escalated", cost: "£0.090 / msg", on: false },
          ].map(m => (
            <div key={m.tier} style={{
              padding: 16, borderRadius: 13,
              background: m.recommended ? "var(--bg)" : "var(--surface)",
              border: `1px solid ${m.recommended ? "var(--graphite)" : "var(--border)"}`,
            }}>
              <div style={{display: "flex", alignItems: "center", justifyContent: "space-between"}}>
                <MonoLabel>{m.tier}</MonoLabel>
                <Tag variant={m.on ? "ok" : "neutral"} withDot>{m.on ? "on" : "off"}</Tag>
              </div>
              <div style={{fontFamily: "var(--font-serif)", fontSize: 18, marginTop: 8}}>{m.label}</div>
              <div style={{fontSize: 12, color: "var(--text-2)", marginTop: 6, lineHeight: 1.5}}>{m.use}</div>
              <div className="t-mono" style={{color: "var(--text-3)", marginTop: 10}}>{m.cost}</div>
            </div>
          ))}
        </div>
      </SettingsCard>

      <SettingsCard title="Personas" sub="The operator persona powers the console. Guest-facing personas arrive with the tenant app.">
        {[
          { p: "Operator",         desc: "Professional · expects precision and minimal hedging. Sees all property-owned devices and data.", default: true },
        ].map(p => (
          <div key={p.p} style={{display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid var(--border)"}}>
            <div>
              <div style={{fontSize: 13, fontWeight: 500}}>{p.p}</div>
              <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 4}}>{p.desc}</div>
            </div>
            <Button variant="ghost" size="sm">Edit prompt</Button>
          </div>
        ))}
        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", opacity: 0.55}}>
          <div>
            <div style={{fontSize: 13, fontWeight: 500}}>Concierge · Home Assistant</div>
            <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 4}}>Guest and resident personas — ship with the tenant app in a later release.</div>
          </div>
          <Tag variant="neutral">coming soon</Tag>
        </div>
      </SettingsCard>

      <SettingsCard title="Confirmations" sub="Which actions require a human OK before the agent runs them.">
        {[
          { l: "Unlock a door",                always: true,  desc: "Always require approval — physical security." },
          { l: "Change thermostat",            always: false, desc: "Approve when delta > 4°C or unit is occupied." },
          { l: "Send a guest message",        always: true,  desc: "Always preview drafts." },
          { l: "Cancel or refund a stay",      always: true,  desc: "Always require approval." },
          { l: "Acknowledge an automation run",always: false, desc: "Approve only when an action failed." },
        ].map(c => (
          <div key={c.l} style={{display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid var(--border)"}}>
            <div style={{maxWidth: 480}}>
              <div style={{fontSize: 13, fontWeight: 500}}>{c.l}</div>
              <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 4}}>{c.desc}</div>
            </div>
            <Tag variant={c.always ? "graphite" : "neutral"}>{c.always ? "always confirm" : "rule-based"}</Tag>
          </div>
        ))}
      </SettingsCard>
    </>
  );
}

/* ============================================================
   TEAM
   ============================================================ */

Object.assign(window, { SettingsScreen, AuditLogBody });
