/* VIEW: Property detail (opened from Portfolio)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateProperty } = React;

function PropertyScreen({ go }) {
  const [tab, setTab] = useStateProperty("overview");
  const p = PROPERTIES[0]; // Maple Court

  return (
    <>
      <PageHeader
        eyebrow={<><span style={{color: "var(--text-2)"}}>Portfolio →</span> Maple Court</>}
        title="Maple Court"
        sub={<>
          <span style={{fontFamily: "var(--font-mono)", color: "var(--text-2)"}}>leeds_ls1</span>
          {" · "}14 Maple Court, Leeds LS1 4AB · Mixed-use · 6 units · Europe/London
        </>}
        primary={<Button variant="primary" icon="sparkles">Ask agent about this property</Button>}
        secondary={<Button variant="secondary" icon="settings">Property settings</Button>}
      />

      <div style={{padding: "0 28px", borderBottom: "1px solid var(--border)", background: "var(--surface)"}}>
        <Tabs value={tab} onChange={setTab} tabs={[
          { id: "overview",    label: "Overview" },
          { id: "rooms",       label: "Rooms & units", count: ROOMS_MAPLE.length },
          { id: "devices",     label: "Devices",       count: DEVICES_MAPLE.length },
          { id: "automations", label: "Automations",   count: 4 },
          { id: "energy",      label: "Energy" },
          { id: "history",     label: "History" },
        ]}/>
      </div>

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20}}>
        {tab === "overview" && <PropertyOverviewTab/>}
        {tab === "rooms" && <PropertyRoomsTab/>}
        {tab === "devices" && <PropertyDevicesTab go={go}/>}
        {tab === "automations" && <PropertyAutomationsTab/>}
        {tab === "energy" && <PropertyEnergyTab/>}
        {tab === "history" && <PropertyHistoryTab/>}
      </div>
    </>
  );
}

function PropertyOverviewTab() {
  return (
    <>
      <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
        <StatCard label="Occupancy" value="4/6" sub="2 units vacant — Flat 3B + Flat 1A"/>
        <StatCard label="Devices online" value="37" unit="/38" sub={<span style={{color: "var(--amber)"}}>1 sensor unreachable</span>} valueColor="var(--text)"/>
        <StatCard label="Energy · today" value="42" unit="kWh" sub="Avg. £4.20"/>
        <StatCard label="Active alerts" value="1" valueColor="var(--amber)" sub={<span style={{color: "var(--amber)"}}>Vacant heating</span>}/>
      </div>

      <SectionHead title="Live device state" sub="POLLED EVERY 30S"
        right={<Tag variant="ok" withDot>Reporting</Tag>}/>
      <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
        {[
          { name: "Front lock", state: "Locked", icon: "lock", since: "1h ago" },
          { name: "Communal heating", state: "16°C · setback", icon: "thermo", since: "now" },
          { name: "Hallway motion", state: "Unreachable", icon: "sensor", since: "2d ago", warn: true },
          { name: "Energy meter", state: "1.2 kW", icon: "meter", since: "30s ago" },
          { name: "Leak — under sink", state: "Dry", icon: "drop", since: "10m ago" },
          { name: "Communal lights", state: "Off", icon: "bulb", since: "now" },
        ].map(d => (
          <Card key={d.name} style={{padding: 16, display: "flex", flexDirection: "column", gap: 12}}>
            <div style={{display: "flex", alignItems: "center", justifyContent: "space-between"}}>
              <div style={{display: "flex", alignItems: "center", gap: 10}}>
                <div style={{width: 28, height: 28, borderRadius: 7, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center"}}>
                  <Icon name={d.icon} size={14} color="var(--text-2)"/>
                </div>
                <span style={{fontSize: 13, fontWeight: 500}}>{d.name}</span>
              </div>
              <Tag variant={d.warn ? "warn" : "ok"} withDot/>
            </div>
            <div style={{
              fontSize: 18, fontWeight: 500, lineHeight: 1.2,
              color: d.warn ? "var(--amber)" : "var(--text)",
              fontFamily: "var(--font-serif)",
            }}>{d.state}</div>
            <div className="t-mono" style={{color: "var(--text-3)"}}>updated · {d.since}</div>
          </Card>
        ))}
      </div>
    </>
  );
}

function PropertyRoomsTab() {
  return (
    <>
      <SectionHead title="Rooms & units" sub={`${ROOMS_MAPLE.length} ROOMS · 6 UNITS`}
        right={<><Button variant="secondary" size="sm" icon="plus">Add room</Button><Button variant="primary" size="sm" icon="plus">Add unit</Button></>}/>
      <div style={{display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12}}>
        {ROOMS_MAPLE.map(r => (
          <Card key={r.id} style={{padding: 16}}>
            <div style={{display: "flex", justifyContent: "space-between", alignItems: "flex-start"}}>
              <div>
                <div style={{fontFamily: "var(--font-serif)", fontSize: 17, lineHeight: 1.2}}>{r.name}</div>
                <div className="t-mono" style={{color: "var(--text-3)", marginTop: 4}}>{r.type.toLowerCase()}</div>
              </div>
              <Icon name="more" size={16} color="var(--text-3)"/>
            </div>
            <div style={{height: 1, background: "var(--border)", margin: "12px 0"}}/>
            <div style={{display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-2)"}}>
              <span>{r.devices} devices</span>
              <span style={{color: "var(--text-3)"}}>2 capabilities</span>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

function PropertyDevicesTab({ go }) {
  return <DeviceList devices={DEVICES_MAPLE} compact go={go}/>;
}

function PropertyStaysTab() {
  return (
    <>
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 13, padding: 18,
        display: "flex", alignItems: "center", gap: 16,
      }}>
        <div style={{flex: 1}}>
          <h3 style={{margin: 0, fontFamily: "var(--font-serif)", fontSize: 20}}>Sarah Whitmore</h3>
          <div style={{display: "flex", gap: 16, marginTop: 8, fontSize: 12, color: "var(--text-2)"}}>
            <span>Long-term tenant · Flat 3B</span>
            <span style={{color: "var(--text-3)"}}>·</span>
            <span style={{fontFamily: "var(--font-mono)"}}>01 Mar 2026 → 28 Feb 2027</span>
            <span style={{color: "var(--text-3)"}}>·</span>
            <span>11 months remaining</span>
          </div>
        </div>
        <Tag variant="ok" withDot>Active</Tag>
      </div>

      <SectionHead title="Upcoming + recent"/>
      <DataTable columns={[
        { k: "unit",   label: "Unit",     w: "1fr" },
        { k: "tenant", label: "Occupant", w: "1.3fr" },
        { k: "source", label: "Source",   w: "1fr",   render: r => <Tag variant="neutral">{r.source.toLowerCase()}</Tag>},
        { k: "in",     label: "Check-in",  w: "1fr",  render: r => <span style={{fontFamily: "var(--font-mono)", fontSize: 12}}>{r.check_in}</span>},
        { k: "out",    label: "Check-out", w: "1fr",  render: r => <span style={{fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-3)"}}>{r.check_out}</span>},
        { k: "status", label: "Status",    w: "0.8fr",render: r => <Tag variant={r.status === "ACTIVE" ? "ok" : r.status === "UPCOMING" ? "warn" : "neutral"} withDot>{r.status.toLowerCase()}</Tag>},
      ]} rows={STAYS.filter(s => s.property === "Maple Court" || s.tenant === "Holly Marsh")}/>
    </>
  );
}

function PropertyAutomationsTab() {
  return (
    <div style={{
      padding: 40, textAlign: "center",
      background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 13,
    }}>
      <Icon name="bolt" size={28} color="var(--text-3)"/>
      <div style={{fontFamily: "var(--font-serif)", fontSize: 22, marginTop: 14}}>4 automations active for Maple Court</div>
      <div style={{fontSize: 13, color: "var(--text-2)", marginTop: 8, maxWidth: 480, marginInline: "auto"}}>
        Open Automations to view, edit or pause. Pre-arrival warm-up, vacant cool-down, leak shut-off, and daily energy summary are running for this property.
      </div>
      <div style={{marginTop: 18}}>
        <Button variant="primary" icon="bolt">Open automations</Button>
      </div>
    </div>
  );
}

function PropertyEnergyTab() {
  const days = ["M", "T", "W", "T", "F", "S", "S"];
  const values = [42, 39, 51, 47, 44, 38, 33];
  const max = Math.max(...values);
  return (
    <>
      <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
        <StatCard label="This week" value="294" unit="kWh" sub={<span style={{color: "var(--green)"}}>↓ 8% vs last</span>}/>
        <StatCard label="This month" value="1,247" unit="kWh" sub="£124 estimated"/>
        <StatCard label="Per occupied unit" value="73" unit="kWh" sub="Vs 89 portfolio avg"/>
        <StatCard label="Standing carbon" value="312" unit="kg" sub="CO₂e · month"/>
      </div>

      <Card style={{padding: 24}}>
        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24}}>
          <div>
            <h3 style={{fontSize: 14, fontWeight: 600, margin: 0}}>Daily consumption · last 7 days</h3>
            <div className="t-mono" style={{color: "var(--text-3)", marginTop: 4}}>kWh · Maple Court only</div>
          </div>
          <div style={{display: "flex", gap: 8}}>
            <Tag variant="neutral" withDot>Heating</Tag>
            <Tag variant="neutral">Lighting</Tag>
            <Tag variant="neutral">Plugs</Tag>
          </div>
        </div>
        <div style={{display: "flex", alignItems: "flex-end", gap: 18, height: 200, padding: "0 8px"}}>
          {values.map((v, i) => (
            <div key={i} style={{flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 8}}>
              <div className="tnum" style={{fontSize: 11, color: "var(--text-3)", fontFamily: "var(--font-mono)"}}>{v}</div>
              <div style={{
                width: "100%", height: `${(v / max) * 160}px`,
                background: "linear-gradient(180deg, var(--graphite) 0%, var(--graphite-2) 100%)",
                borderRadius: 6,
              }}/>
              <div className="t-mono" style={{color: "var(--text-3)"}}>{days[i]}</div>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}

function PropertyHistoryTab() {
  return (
    <DataTable columns={[
      { k: "time", label: "Time", w: "120px", render: r => <span className="t-mono" style={{color: "var(--text-3)"}}>{r.time}</span>},
      { k: "actor", label: "Actor", w: "150px", render: r => <span style={{fontSize: 13, fontWeight: 500}}>{r.actor}</span>},
      { k: "action", label: "Action", w: "1fr", wrap: true},
      { k: "result", label: "Result", w: "120px", render: r => <Tag variant={r.kind} withDot>{r.kind === "ok" ? "ok" : r.kind}</Tag>},
    ]} rows={[
      { time: "today 11:24", actor: "Agent",  action: "Set Flat 3B Living thermostat to 14°C — vacancy cool-down", kind: "ok" },
      { time: "today 11:20", actor: "Auto",   action: "Triggered vacant cool-down for Flat 3B", kind: "ok" },
      { time: "today 08:42", actor: "Marcus", action: "Approved 'turn off heating' suggestion", kind: "ok" },
      { time: "today 08:14", actor: "Agent",  action: "Published insight: vacant heating waste", kind: "warn" },
      { time: "today 07:30", actor: "System", action: "Daily energy snapshot collected · 42 kWh", kind: "ok" },
      { time: "Y'day 16:30", actor: "Theo A.", action: "Connected Ecobee integration", kind: "ok" },
      { time: "Y'day 09:11", actor: "Marcus", action: "Disabled frost protection automation", kind: "neutral" },
    ]}/>
  );
}

/* ============================================================
   Device list (shared)
   ============================================================ */

Object.assign(window, { PropertyScreen });
