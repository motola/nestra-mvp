/* TAB: Integrations (vendor connections)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateIntegrations } = React;

function IntegrationsScreen() {
  const [tab, setTab] = useStateIntegrations("connected");
  const property = INTEGRATIONS.filter(i => i.ownerType === "PROPERTY");

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Integrations"
        sub={`${INTEGRATIONS.length} connections · ${INTEGRATIONS.filter(i => i.status === "ACTIVE").length} active · 1 needs reauth`}
        primary={<Button variant="primary" icon="plus">Connect vendor</Button>}
        secondary={<Button variant="secondary" icon="book">View adapter docs</Button>}
      />

      <div style={{padding: "0 28px", borderBottom: "1px solid var(--border)", background: "var(--surface)"}}>
        <Tabs value={tab} onChange={setTab} tabs={[
          { id: "connected", label: "Connected",  count: INTEGRATIONS.length },
          { id: "catalog",   label: "Catalog",    count: 10 },
          { id: "webhooks",  label: "Webhooks",   count: 18 },
          { id: "errors",    label: "Errors",     count: 1 },
        ]}/>
      </div>

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20}}>
        {tab === "connected" && <>
          {INTEGRATIONS.find(i => i.needsReauth) && (
            <AlertCard severity="amber"
              title="SmartThings token expired"
              desc="Your portfolio's SmartThings access token expired 6 hours ago. 12 devices are not receiving state updates. Reconnect to restore — your scopes will carry over."
              meta="Integration · Northern Portfolio · Today 03:14"
              actions={["Reauthorize", "Open integration"]}/>
          )}

          <SectionHead title="Connected vendors" sub={`${property.length} INTEGRATIONS · OWNED BY THE PORTFOLIO`}/>
          <IntegrationGrid items={property}/>
        </>}

        {tab === "catalog" && <CatalogTab/>}
        {tab === "webhooks" && <WebhooksTab/>}
        {tab === "errors" && <ErrorsTab/>}
      </div>
    </>
  );
}

function IntegrationGrid({ items }) {
  return (
    <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12}}>
      {items.map(i => (
        <Card key={i.id} hoverable style={{padding: 18}}>
          <div style={{display: "flex", alignItems: "center", gap: 14}}>
            <VendorLogo name={i.vendor} size={48}/>
            <div style={{flex: 1, minWidth: 0}}>
              <div style={{display: "flex", alignItems: "center", gap: 10}}>
                <span style={{fontFamily: "var(--font-serif)", fontSize: 18}}>{i.vendor}</span>
                {i.status === "ACTIVE"
                  ? <Tag variant="ok" withDot>active</Tag>
                  : <Tag variant="warn" withDot>token expired</Tag>}
              </div>
              <div className="t-mono" style={{color: "var(--text-3)", marginTop: 4}}>
                {`property · ${i.ownerName}`}
              </div>
            </div>
            <Button variant={i.needsReauth ? "primary" : "ghost"} size="sm">
              {i.needsReauth ? "Reauthorize" : "Manage"}
            </Button>
          </div>

          <div style={{height: 1, background: "var(--border)", margin: "14px 0"}}/>

          <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
            <div>
              <div className="t-mono" style={{color: "var(--text-3)"}}>devices</div>
              <div style={{fontSize: 18, fontWeight: 600, fontFamily: "var(--font-mono)", marginTop: 4}}>{i.devices}</div>
            </div>
            <div>
              <div className="t-mono" style={{color: "var(--text-3)"}}>last sync</div>
              <div style={{fontSize: 13, marginTop: 4}}>{i.lastSync}</div>
            </div>
            <div>
              <div className="t-mono" style={{color: "var(--text-3)"}}>connected</div>
              <div style={{fontSize: 13, marginTop: 4, fontFamily: "var(--font-mono)"}}>{i.connectedAt}</div>
            </div>
          </div>

          <div style={{display: "flex", gap: 6, marginTop: 14, flexWrap: "wrap"}}>
            {i.scopes.map(s => <Tag key={s} variant="neutral">{s}</Tag>)}
          </div>
        </Card>
      ))}
    </div>
  );
}

function CatalogTab() {
  return (
    <>
      <div style={{display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap"}}>
        <Tag variant="graphite">All vendors</Tag>
        <Tag variant="neutral">Thermostats</Tag>
        <Tag variant="neutral">Lights</Tag>
        <Tag variant="neutral">Locks</Tag>
        <Tag variant="neutral">Sensors</Tag>
        <Tag variant="neutral">Plugs &amp; meters</Tag>
        <Tag variant="neutral">Hubs &amp; bridges</Tag>
      </div>
      <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
        {VENDORS.map(v => (
          <Card key={v.id} hoverable style={{padding: 18, display: "flex", flexDirection: "column", gap: 12}}>
            <div style={{display: "flex", alignItems: "center", gap: 12}}>
              <VendorLogo name={v.name}/>
              <div style={{flex: 1}}>
                <div style={{fontSize: 14, fontWeight: 600}}>{v.name}</div>
                <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 2}}>{v.cats}</div>
              </div>
              {v.connected && <Tag variant="ok" withDot>connected</Tag>}
            </div>
            <div style={{height: 1, background: "var(--border)"}}/>
            <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
              <span className="t-mono" style={{color: "var(--text-3)"}}>{v.connected ? "manage" : "set up oauth"}</span>
              <Button variant={v.connected ? "secondary" : "primary"} size="sm">{v.connected ? "Manage" : "Connect"}</Button>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

function WebhooksTab() {
  const rows = [
    { vendor: "Nest",        topic: "device.state",      events: "1,847", last: "2 min ago",   status: "active" },
    { vendor: "Hue",         topic: "lights.changed",    events: "4,329", last: "30 sec ago",  status: "active" },
    { vendor: "August",      topic: "lock.state",        events: "412",   last: "1 min ago",   status: "active" },
    { vendor: "Shelly",      topic: "energy.usage",      events: "8,201", last: "1 min ago",   status: "active" },
    { vendor: "SmartThings", topic: "hub.events",        events: "230",   last: "6 h ago",     status: "error" },
    { vendor: "Ecobee",      topic: "thermostat.state",  events: "942",   last: "5 min ago",   status: "active" },
  ];
  return (
    <>
      <SectionHead title="Webhook subscriptions" sub="VENDOR → ALPHACON · INCOMING EVENTS"/>
      <DataTable columns={[
        { k: "vendor", label: "Vendor", w: "1fr", render: r => <span style={{fontWeight: 500}}>{r.vendor}</span>},
        { k: "topic", label: "Topic", w: "1.4fr", render: r => <span style={{fontFamily: "var(--font-mono)", fontSize: 12}}>{r.topic}</span>},
        { k: "events", label: "Events · 24h", w: "1fr", align: "right", render: r => <span className="tnum">{r.events}</span>},
        { k: "last", label: "Last received", w: "1fr", render: r => <span className="t-mono" style={{color: "var(--text-3)"}}>{r.last}</span>},
        { k: "status", label: "Status", w: "0.8fr", render: r => <Tag variant={r.status === "active" ? "ok" : "alert"} withDot>{r.status}</Tag>},
        { k: "act", label: "", w: "70px", align: "right", render: () => <Button variant="ghost" size="sm">Rotate</Button>},
      ]} rows={rows}/>
    </>
  );
}

function ErrorsTab() {
  const rows = [
    { time: "today 03:14", vendor: "SmartThings", code: "AuthExpired",   message: "Refresh token returned 401 invalid_grant", retriable: true, user: true },
    { time: "Y'day 18:32", vendor: "Nest",        code: "RateLimited",   message: "Backoff for 47s · /thermostat/cmd", retriable: true, user: false },
    { time: "Y'day 11:09", vendor: "Hue",         code: "DeviceOffline", message: "Bridge unreachable for 3 min · Maple Court", retriable: false, user: true },
    { time: "29 Mar",      vendor: "August",      code: "CommandRejected", message: "Lock not in manual mode · Larkspur House", retriable: false, user: true },
  ];
  return (
    <>
      <SectionHead title="Adapter errors" sub="LAST 7 DAYS · CLASSIFIED BY ADAPTERROR HIERARCHY"/>
      <DataTable columns={[
        { k: "time", label: "Time", w: "120px", render: r => <span className="t-mono" style={{color: "var(--text-3)"}}>{r.time}</span>},
        { k: "vendor", label: "Vendor", w: "1fr"},
        { k: "code", label: "Error", w: "1fr", render: r => <span style={{fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 500, color: "var(--red)"}}>{r.code}</span>},
        { k: "message", label: "Message", w: "2.5fr", wrap: true, render: r => <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.message}</span>},
        { k: "flags", label: "Flags", w: "1.2fr", render: r => (
          <div style={{display: "flex", gap: 4}}>
            {r.retriable && <Tag variant="neutral">retriable</Tag>}
            {r.user && <Tag variant="warn">user-visible</Tag>}
          </div>
        )},
      ]} rows={rows}/>
    </>
  );
}

/* ============================================================
   STAYS
   ============================================================ */

Object.assign(window, { IntegrationsScreen });
