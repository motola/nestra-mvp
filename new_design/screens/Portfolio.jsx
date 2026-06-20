/* TAB: Portfolio (portfolios + all-properties)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStatePortfolio } = React;

function PortfolioScreen({ go }) {
  const [tab, setTab] = useStatePortfolio("portfolios");
  const [view, setView] = useStatePortfolio("grid");
  const [filter, setFilter] = useStatePortfolio("all");
  const filtered = filter === "all" ? PROPERTIES : PROPERTIES.filter(p => p.status === filter);

  const columns = [
    { k: "name", label: "Property", w: "1.4fr", render: r => (
      <div>
        <div style={{fontFamily: "var(--font-serif)", fontSize: 16}}>{r.name}</div>
        <div style={{fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-3)", marginTop: 2}}>{r.address}</div>
      </div>
    )},
    { k: "type", label: "Type", w: "0.9fr", render: r => <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.type.replace(/_/g, " ").toLowerCase()}</span>},
    { k: "units", label: "Units", w: "0.5fr", align: "right", render: r => <span className="tnum">{r.units}</span>},
    { k: "occupied", label: "Occupied", w: "0.7fr", align: "right", render: r => <span className="tnum">{r.occupied}/{r.units}</span>},
    { k: "devices", label: "Devices", w: "0.6fr", align: "right", render: r => <span className="tnum">{r.devices}</span>},
    { k: "integrations", label: "Integrations", w: "0.7fr", align: "right", render: r => <span className="tnum">{r.integrations}</span>},
    { k: "status", label: "Status", w: "0.8fr", render: r => (
      r.alerts > 0
        ? <Tag variant={r.status === "alert" ? "alert" : "warn"} withDot>{r.alerts} alert{r.alerts>1?"s":""}</Tag>
        : <Tag variant="ok" withDot>All clear</Tag>
    )},
    { k: "actions", label: "", w: "30px", align: "right", render: () => <Icon name="chevron" size={14} color="var(--text-3)"/>},
  ];

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Portfolios"
        sub={`${PORTFOLIOS.length} portfolios · ${PROPERTIES.length} properties across 4 cities · 68 units · 401 devices`}
        primary={<Button variant="primary" icon="plus">Add property</Button>}
        secondary={<Button variant="secondary" icon="download">Export CSV</Button>}
      />

      <div style={{padding: "0 28px", borderBottom: "1px solid var(--border)", background: "var(--surface)"}}>
        <Tabs value={tab} onChange={setTab} tabs={[
          { id: "portfolios", label: "Portfolios", count: PORTFOLIOS.length },
          { id: "all",        label: "All properties", count: PROPERTIES.length },
        ]}/>
      </div>

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20}}>
        {tab === "portfolios" ? (
          <div style={{display: "flex", flexDirection: "column", gap: 16}}>
            {PORTFOLIOS.map(pf => {
              const props = PROPERTIES.filter(p => p.portfolio === pf.id);
              const units = props.reduce((s, p) => s + p.units, 0);
              const occ = props.reduce((s, p) => s + p.occupied, 0);
              const alerts = props.reduce((s, p) => s + p.alerts, 0);
              return (
                <section key={pf.id} style={{
                  background: "var(--surface-2)", border: "1px solid var(--border)",
                  borderRadius: 14, padding: 18,
                }}>
                  {/* Portfolio header */}
                  <div style={{display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, flexWrap: "wrap", marginBottom: 14}}>
                    <div style={{display: "flex", alignItems: "center", gap: 12, minWidth: 0}}>
                      <div style={{width: 32, height: 32, borderRadius: 8, background: "var(--graphite)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0}}>
                        <Icon name="grid" size={15} color="#ffffff"/>
                      </div>
                      <div style={{minWidth: 0}}>
                        <div style={{fontFamily: "var(--font-serif)", fontSize: 19, lineHeight: 1.15}}>{pf.name}</div>
                        <div className="t-mono" style={{color: "var(--text-3)", marginTop: 2}}>{pf.region} · {pf.manager}</div>
                      </div>
                    </div>
                    <div style={{display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap"}}>
                      <Tag variant="neutral">{props.length} properties</Tag>
                      <Tag variant="neutral">{units} units</Tag>
                      <Tag variant="neutral">{occ}/{units} occupied</Tag>
                      {alerts > 0
                        ? <Tag variant="warn" withDot>{alerts} alert{alerts > 1 ? "s" : ""}</Tag>
                        : <Tag variant="ok" withDot>All clear</Tag>}
                      <Button variant="ghost" size="sm" iconRight="arrow">Manage</Button>
                    </div>
                  </div>

                  {/* Enclosed, wrapping property cards */}
                  <div style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(230px, 1fr))",
                    gap: 12,
                  }}>
                    {props.map(p => <PropertyCard key={p.id} {...p} onClick={() => go("property")}/>)}
                  </div>
                </section>
              );
            })}
          </div>
        ) : (
          <>
            <div style={{display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12}}>
              <div style={{display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap"}}>
                {[
                  ["all", "All", PROPERTIES.length],
                  ["ok", "Clear", PROPERTIES.filter(p => p.status === "ok").length],
                  ["warn", "Attention", PROPERTIES.filter(p => p.status === "warn").length],
                  ["alert", "Critical", PROPERTIES.filter(p => p.status === "alert").length],
                ].map(([id, label, n]) => (
                  <button key={id} onClick={() => setFilter(id)} style={{
                    background: filter === id ? "var(--graphite)" : "var(--surface)",
                    color: filter === id ? "#ffffff" : "var(--text-2)",
                    border: `1px solid ${filter === id ? "var(--graphite)" : "var(--border)"}`,
                    borderRadius: 9, padding: "6px 12px", cursor: "pointer",
                    fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 500,
                    display: "inline-flex", alignItems: "center", gap: 8,
                  }}>
                    {label}
                    <span className="tnum" style={{opacity: filter === id ? 0.8 : 1, fontFamily: "var(--font-mono)", fontSize: 10}}>{n}</span>
                  </button>
                ))}
              </div>
              <div style={{display: "flex", gap: 6, padding: 3, background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 9}}>
                {["grid", "list"].map(v => (
                  <button key={v} onClick={() => setView(v)} style={{
                    background: view === v ? "var(--bg)" : "transparent",
                    border: "1px solid " + (view === v ? "var(--border)" : "transparent"),
                    color: view === v ? "var(--text)" : "var(--text-3)",
                    borderRadius: 7, padding: "4px 10px", cursor: "pointer", fontFamily: "var(--font-sans)", fontSize: 12,
                    textTransform: "capitalize",
                  }}>{v}</button>
                ))}
              </div>
            </div>

            {view === "grid" ? (
              <div style={{display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(230px, 1fr))", gap: 12}}>
                {filtered.map(p => <PropertyCard key={p.id} {...p} onClick={() => go("property")}/>)}
              </div>
            ) : (
              <DataTable columns={columns} rows={filtered} onRowClick={() => go("property")}/>
            )}
          </>
        )}
      </div>
    </>
  );
}

/* ============================================================
   PROPERTY DETAIL
   ============================================================ */

Object.assign(window, { PortfolioScreen });
