/* SHARED: device list + device detail drawer (used by Devices tab AND Property detail)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateDevShared } = React;

function DeviceList({ devices, compact, go }) {
  const [filter, setFilter] = useStateDevShared("all");
  const [selected, setSelected] = useStateDevShared(null);
  const iconFor = (cat) => ({
    THERMOSTAT: "thermo", LIGHT: "bulb", LOCK: "lock",
    PLUG: "plug", SENSOR_MOTION: "sensor", SENSOR_LEAK: "drop",
    SENSOR_CONTACT: "sensor", ENERGY_METER: "meter", SWITCH: "plug", HUB: "devices",
  }[cat] || "devices");

  const list = filter === "all" ? devices
    : filter === "offline" ? devices.filter(d => !d.reachable)
    : filter === "alert" ? devices.filter(d => d.alert)
    : devices;

  return (
    <>
      <div style={{display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap"}}>
        {[
          ["all", "All", devices.length],
          ["alert", "Needs attention", devices.filter(d => d.alert).length],
          ["offline", "Unreachable", devices.filter(d => !d.reachable).length],
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
            <span style={{fontFamily: "var(--font-mono)", fontSize: 10}}>{n}</span>
          </button>
        ))}
        <div style={{flex: 1}}/>
        <Button variant="secondary" size="sm" icon="refresh">Re-sync from vendors</Button>
      </div>

      <DataTable columns={[
        { k: "name", label: "Device", w: "1.5fr", render: r => (
          <div style={{display: "flex", alignItems: "center", gap: 10}}>
            <div style={{width: 28, height: 28, borderRadius: 7, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0}}>
              <Icon name={iconFor(r.category)} size={14} color="var(--text-2)"/>
            </div>
            <div style={{minWidth: 0}}>
              <div style={{fontSize: 13, fontWeight: 500, color: r.alert ? "var(--amber)" : "var(--text)"}}>{r.name}</div>
              <div className="t-mono" style={{color: "var(--text-3)", marginTop: 2}}>{r.category.replace(/_/g, " ").toLowerCase()}</div>
            </div>
          </div>
        )},
        { k: "room", label: "Room", w: "1.2fr", render: r => <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.room}</span>},
        { k: "vendor", label: "Vendor", w: "0.8fr", render: r => <span style={{fontSize: 12, color: "var(--text-2)"}}>{r.vendor}</span>},
        { k: "state", label: "State", w: "1fr", render: r => (
          <span style={{fontSize: 13, color: r.reachable ? (r.alert ? "var(--amber)" : "var(--text)") : "var(--text-3)", fontWeight: r.alert ? 500 : 400}}>
            {r.reachable ? r.state : "Unreachable"}
          </span>
        )},
        { k: "lastSeen", label: "Last seen", w: "0.8fr", render: r => <span className="t-mono" style={{color: r.reachable ? "var(--text-3)" : "var(--amber)"}}>{r.lastSeen}</span>},
        { k: "act", label: "", w: compact ? "30px" : "70px", align: "right", render: () => <Icon name="chevron" size={14} color="var(--text-3)"/>},
      ]} rows={list} onRowClick={(r) => setSelected(r)}/>

      {selected && (
        <DeviceDrawer device={selected} iconFor={iconFor} onClose={() => setSelected(null)} go={go}/>
      )}
    </>
  );
}

/* ---- Per-device detail + activity timeline ---- */

function deviceActivity(d) {
  const cat = d.category;
  const base = [];
  if (!d.reachable) {
    base.push({ time: "2d ago", kind: "VENDOR", who: d.vendor, text: `Stopped reporting — last heartbeat received, then silence`, tone: "alert" });
    base.push({ time: "2d ago", kind: "SYSTEM", who: "System", text: "Marked unreachable after 3 missed polls", tone: "warn" });
  }
  if (d.alert && d.reachable) {
    base.push({ time: "today 08:14", kind: "AGENT", who: "Agent", text: "Flagged: running while unit is vacant — published an insight", tone: "warn" });
  }
  const byCat = {
    THERMOSTAT: [
      { time: "today 11:24", kind: "AGENT", who: "Agent", text: "Set point lowered to 14°C — vacancy cool-down", tone: "ok" },
      { time: "today 08:42", kind: "USER", who: "Marcus Chen", text: "Approved agent suggestion to lower heating", tone: "ok" },
      { time: "yesterday 18:30", kind: "AUTOMATION", who: "Pre-arrival warm-up", text: "Raised to 20°C ahead of expected occupancy", tone: "ok" },
      { time: "yesterday 06:00", kind: "SYSTEM", who: "System", text: "Mode changed heat → auto on schedule", tone: "neutral" },
    ],
    LIGHT: [
      { time: "today 07:02", kind: "AUTOMATION", who: "Morning scene", text: "Brightness set to 60%, warm white", tone: "ok" },
      { time: "yesterday 23:10", kind: "AUTOMATION", who: "Bedtime", text: "Turned off", tone: "neutral" },
      { time: "yesterday 19:44", kind: "USER", who: "Marcus Chen", text: "Turned on from device console", tone: "ok" },
    ],
    LOCK: [
      { time: "today 09:01", kind: "USER", who: "Olu Adebayo", text: "Unlocked remotely for a contractor visit", tone: "ok" },
      { time: "today 09:36", kind: "SYSTEM", who: "System", text: "Auto-relocked after 35 min", tone: "neutral" },
      { time: "yesterday 14:20", kind: "VENDOR", who: d.vendor, text: "Battery level reported: 72%", tone: "neutral" },
    ],
    PLUG: [
      { time: "today 11:30", kind: "VENDOR", who: d.vendor, text: `Power draw reported: ${d.state}`, tone: "neutral" },
      { time: "today 02:00", kind: "AUTOMATION", who: "Vacant cool-down", text: "Switched off non-essential load", tone: "ok" },
    ],
    ENERGY_METER: [
      { time: "30s ago", kind: "VENDOR", who: d.vendor, text: `Live reading: ${d.state}`, tone: "neutral" },
      { time: "today 07:30", kind: "SYSTEM", who: "System", text: "Daily energy snapshot collected", tone: "ok" },
    ],
    SENSOR_MOTION: [
      { time: "3m ago", kind: "VENDOR", who: d.vendor, text: "Motion cleared", tone: "neutral" },
      { time: "yesterday 21:14", kind: "VENDOR", who: d.vendor, text: "Motion detected", tone: "neutral" },
    ],
    SENSOR_LEAK: [
      { time: "10m ago", kind: "VENDOR", who: d.vendor, text: "Reading: dry", tone: "ok" },
      { time: "1 Apr 03:00", kind: "SYSTEM", who: "System", text: "Self-test passed", tone: "ok" },
    ],
    SENSOR_CONTACT: [
      { time: "1h ago", kind: "VENDOR", who: d.vendor, text: "Reading: closed", tone: "neutral" },
      { time: "yesterday 16:02", kind: "VENDOR", who: d.vendor, text: "Opened, then closed after 4 min", tone: "neutral" },
    ],
  };
  const tail = [
    { time: d.connectedAt || "20 Jan 2026", kind: "SYSTEM", who: "System", text: `Paired via ${d.vendor} integration · owner: property`, tone: "neutral" },
  ];
  return [...base, ...(byCat[cat] || [{ time: "today", kind: "VENDOR", who: d.vendor, text: `State: ${d.state}`, tone: "neutral" }]), ...tail];
}

function DeviceDrawer({ device: d, iconFor, onClose, go }) {
  const kindColor = (k) => ({ AGENT: "var(--graphite)", AUTOMATION: "var(--text-2)", USER: "var(--text-2)", SYSTEM: "var(--text-3)", VENDOR: "var(--amber)" }[k] || "var(--text-3)");
  const toneDot = (t) => ({ ok: "var(--green)", warn: "var(--amber)", alert: "var(--red)", neutral: "var(--text-3)" }[t]);
  const events = deviceActivity(d);

  return (
    <div style={{position: "fixed", inset: 0, zIndex: 60, display: "flex", justifyContent: "flex-end"}}>
      <div onClick={onClose} style={{position: "absolute", inset: 0, background: "rgba(16,24,40,0.28)"}}/>
      <div style={{
        position: "relative", width: 440, maxWidth: "92vw", height: "100%",
        background: "var(--surface)", borderLeft: "1px solid var(--border)",
        boxShadow: "var(--shadow-lg)", display: "flex", flexDirection: "column",
        animation: "none",
      }}>
        {/* header */}
        <div style={{padding: "18px 20px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "flex-start", gap: 12}}>
          <div style={{width: 38, height: 38, borderRadius: 8, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0}}>
            <Icon name={iconFor(d.category)} size={18} color="var(--text-2)"/>
          </div>
          <div style={{flex: 1, minWidth: 0}}>
            <div style={{fontFamily: "var(--font-serif)", fontSize: 19, lineHeight: 1.2, color: d.alert ? "var(--amber)" : "var(--text)"}}>{d.name}</div>
            <div className="t-mono" style={{color: "var(--text-3)", marginTop: 3}}>{d.category.replace(/_/g, " ").toLowerCase()} · {d.room}</div>
          </div>
          <button onClick={onClose} style={{background: "transparent", border: "none", cursor: "pointer", padding: 4, color: "var(--text-3)"}}>
            <Icon name="x" size={18}/>
          </button>
        </div>

        <div style={{flex: 1, overflowY: "auto", padding: "18px 20px", display: "flex", flexDirection: "column", gap: 20}}>
          {/* live state */}
          <div style={{background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 13, padding: 16}}>
            <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
              <span className="t-mono" style={{color: "var(--text-3)"}}>current state</span>
              <Tag variant={d.reachable ? (d.alert ? "warn" : "ok") : "alert"} withDot>{d.reachable ? "online" : "unreachable"}</Tag>
            </div>
            <div style={{fontFamily: "var(--font-serif)", fontSize: 24, marginTop: 8, color: d.alert ? "var(--amber)" : "var(--text)"}}>
              {d.reachable ? d.state : "No signal"}
            </div>
            <div className="t-mono" style={{color: "var(--text-3)", marginTop: 6}}>last seen · {d.lastSeen}</div>
          </div>

          {/* meta */}
          <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12}}>
            <Meta k="Vendor" v={d.vendor}/>
            <Meta k="Owner" v="Property"/>
            <Meta k="Room" v={d.room}/>
            <Meta k="Device ID" v={d.id} mono/>
          </div>
          <div>
            <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 8}}>capabilities</div>
            <div style={{display: "flex", gap: 6, flexWrap: "wrap"}}>
              {(d.capabilities || []).map(c => <Tag key={c} variant="neutral">{c.replace(/_/g, " ").toLowerCase()}</Tag>)}
            </div>
          </div>

          {/* quick controls */}
          <div style={{display: "flex", gap: 8, flexWrap: "wrap"}}>
            <Button variant="secondary" size="sm" icon="refresh">Re-sync</Button>
            <Button variant="secondary" size="sm" icon="sparkles">Ask agent</Button>
            {!d.reachable && <Button variant="primary" size="sm" icon="refresh">Restart via hub</Button>}
          </div>

          {/* activity */}
          <div>
            <div style={{display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12}}>
              <h3 style={{fontSize: 13, fontWeight: 600, margin: 0}}>Activity</h3>
              <button onClick={() => { onClose(); go && go("audit"); }} style={{
                background: "transparent", border: "none", cursor: "pointer", padding: 0,
                fontSize: 11, color: "var(--blue)", fontWeight: 500, display: "inline-flex", alignItems: "center", gap: 4,
              }}>
                Full audit log <Icon name="arrow" size={11}/>
              </button>
            </div>
            <ul style={{listStyle: "none", margin: 0, padding: 0}}>
              {events.map((e, i) => (
                <li key={i} style={{display: "flex", gap: 12, paddingBottom: i < events.length - 1 ? 16 : 0, position: "relative"}}>
                  {/* timeline rail */}
                  <div style={{display: "flex", flexDirection: "column", alignItems: "center", flexShrink: 0}}>
                    <span style={{width: 9, height: 9, borderRadius: "50%", background: toneDot(e.tone), marginTop: 4, flexShrink: 0}}/>
                    {i < events.length - 1 && <span style={{width: 1, flex: 1, background: "var(--border)", marginTop: 4}}/>}
                  </div>
                  <div style={{flex: 1, minWidth: 0, paddingBottom: 2}}>
                    <div style={{fontSize: 13, color: "var(--text)", lineHeight: 1.45}}>{e.text}</div>
                    <div style={{display: "flex", alignItems: "center", gap: 6, marginTop: 4}}>
                      <span className="t-mono" style={{color: kindColor(e.kind)}}>{e.kind.toLowerCase()}</span>
                      <span style={{color: "var(--text-3)", fontSize: 11}}>· {e.who} ·</span>
                      <span className="t-mono" style={{color: "var(--text-3)"}}>{e.time}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function Meta({ k, v, mono }) {
  return (
    <div style={{background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 9, padding: "10px 12px"}}>
      <div className="t-mono" style={{color: "var(--text-3)"}}>{k}</div>
      <div style={{fontSize: 13, marginTop: 4, fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)", color: "var(--text)"}}>{v}</div>
    </div>
  );
}

Object.assign(window, { DeviceList });
