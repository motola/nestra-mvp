/* Alphacon AI MVP — shared components. Extends ui_kits/property-dashboard primitives. */
/* global React */
const { useState, useMemo } = React;

/* ============================================================
   Icons — Lucide stroke 1.5
   ============================================================ */
function Icon({ name, size = 16, color = "currentColor" }) {
  const p = {
    home:       <><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></>,
    grid:       <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></>,
    chart:      <><path d="M3 3v18h18"/><polyline points="7 14 11 10 15 13 21 7"/></>,
    devices:    <><rect x="3" y="4" width="18" height="12" rx="2"/><line x1="8" y1="20" x2="16" y2="20"/><line x1="12" y1="16" x2="12" y2="20"/></>,
    plug:       <><path d="M9 2v6M15 2v6M6 8h12v3a6 6 0 0 1-12 0z"/><path d="M12 17v5"/></>,
    users:      <><circle cx="9" cy="7" r="4"/><path d="M3 21v-1a6 6 0 0 1 12 0v1"/><circle cx="17" cy="9" r="3"/><path d="M21 21v-1a4 4 0 0 0-3-3.87"/></>,
    user:       <><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 12 0v1"/></>,
    settings:   <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></>,
    search:     <><circle cx="11" cy="11" r="7"/><line x1="20" y1="20" x2="16.65" y2="16.65"/></>,
    bell:       <><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></>,
    plus:       <><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>,
    arrow:      <><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></>,
    arrowLeft:  <><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></>,
    arrowUp:    <><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></>,
    arrowDown:  <><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></>,
    energy:     <><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></>,
    building:   <><rect x="4" y="3" width="16" height="18" rx="1"/><line x1="9" y1="9" x2="9" y2="9.01"/><line x1="9" y1="13" x2="9" y2="13.01"/><line x1="9" y1="17" x2="9" y2="17.01"/><line x1="15" y1="9" x2="15" y2="9.01"/><line x1="15" y1="13" x2="15" y2="13.01"/><line x1="15" y1="17" x2="15" y2="17.01"/></>,
    alert:      <><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></>,
    check:      <><polyline points="20 6 9 17 4 12"/></>,
    x:          <><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>,
    thermo:     <><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></>,
    bulb:       <><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.5.4 1 1 1 1.6V18h6v-1.7c0-.6.5-1.2 1-1.6A7 7 0 0 0 12 2z"/></>,
    lock:       <><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></>,
    sensor:     <><circle cx="12" cy="12" r="3"/><path d="M3 12a9 9 0 0 1 9-9M21 12a9 9 0 0 1-9 9M12 3a9 9 0 0 1 9 9M12 21a9 9 0 0 1-9-9"/></>,
    drop:       <><path d="M12 2.5s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/></>,
    meter:      <><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></>,
    flow:       <><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></>,
    sparkles:   <><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M5 19l3-3M16 8l3-3"/></>,
    history:    <><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/><path d="M3 12a9 9 0 1 0 3-6.7"/><polyline points="3 4 3 9 8 9"/></>,
    book:       <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></>,
    moon:       <><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></>,
    clock:      <><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></>,
    chat:       <><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></>,
    filter:     <><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></>,
    more:       <><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></>,
    refresh:    <><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></>,
    link:       <><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></>,
    eye:        <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></>,
    download:   <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></>,
    mail:       <><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22 6 12 13 2 6"/></>,
    play:       <><polygon points="5 3 19 12 5 21 5 3"/></>,
    pause:      <><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></>,
    bolt:       <><polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></>,
    calendar:   <><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></>,
    send:       <><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></>,
    chevron:    <><polyline points="9 18 15 12 9 6"/></>,
    spark:      <><path d="M12 3c.5 4.5 4.5 8.5 9 9-4.5.5-8.5 4.5-9 9-.5-4.5-4.5-8.5-9-9 4.5-.5 8.5-4.5 9-9z"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{display:"block"}}>
      {p[name] || null}
    </svg>
  );
}

/* ============================================================
   Tag
   ============================================================ */
function Tag({ variant = "neutral", children, withDot = false, mono = true }) {
  const s = {
    ok:       { bg: "var(--green-bg)",  fg: "var(--green)",  bd: "transparent" },
    warn:     { bg: "var(--amber-bg)",  fg: "var(--amber)",  bd: "transparent" },
    alert:    { bg: "var(--red-bg)",    fg: "var(--red)",    bd: "transparent" },
    neutral:  { bg: "var(--surface-2)", fg: "var(--text-2)", bd: "var(--border)" },
    graphite: { bg: "var(--graphite)",  fg: "#ffffff",       bd: "transparent" },
  }[variant];
  return (
    <span style={{
      fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)",
      fontSize: 10, letterSpacing: mono ? "0.08em" : 0,
      textTransform: mono ? "uppercase" : "none", fontWeight: 500,
      padding: "3px 9px", borderRadius: 20,
      background: s.bg, color: s.fg, border: `1px solid ${s.bd}`,
      display: "inline-flex", alignItems: "center", gap: 6, whiteSpace: "nowrap",
    }}>
      {withDot && <span style={{width:6, height:6, borderRadius:"50%", background: s.fg}}/>}
      {children}
    </span>
  );
}

/* ============================================================
   Button
   ============================================================ */
function Button({ variant = "secondary", children, icon, iconRight, size = "md", ...rest }) {
  const base = {
    fontFamily: "var(--font-sans)", fontWeight: 500,
    border: "none", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 7,
    transition: "all var(--motion-fast) var(--ease-default)",
    fontSize: size === "sm" ? 12 : 13,
    whiteSpace: "nowrap", lineHeight: 1.2,
  };
  const pad = size === "sm" ? "5px 10px" : "8px 14px";
  const v = {
    primary:     { ...base, background: "var(--blue)", color: "#ffffff", padding: pad, borderRadius: 9 },
    secondary:   { ...base, background: "var(--surface)",  color: "var(--text)", border: "1px solid var(--border)", padding: pad, borderRadius: 9 },
    ghost:       { ...base, background: "transparent", color: "var(--text-2)", padding: pad, borderRadius: 9 },
    destructive: { ...base, background: "var(--surface)", color: "var(--red)", border: "1px solid var(--red-bg)", padding: pad, borderRadius: 9 },
    tagPrim:     { ...base, background: "var(--graphite)", color: "#ffffff", padding: "5px 12px", borderRadius: 20, fontSize: 11 },
    tagSec:      { ...base, background: "var(--surface-2)", color: "var(--text-2)", border: "1px solid var(--border)", padding: "5px 12px", borderRadius: 20, fontSize: 11 },
  };
  return (
    <button style={v[variant]} {...rest}>
      {icon && <Icon name={icon} size={size === "sm" ? 12 : 14}/>}
      {children}
      {iconRight && <Icon name={iconRight} size={size === "sm" ? 12 : 14}/>}
    </button>
  );
}

/* ============================================================
   Card surfaces
   ============================================================ */
function Card({ children, style, hoverable, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: 13, ...style, cursor: onClick ? "pointer" : "default",
      }}
      onMouseEnter={hoverable ? (e) => e.currentTarget.style.borderColor = "var(--border-strong)" : undefined}
      onMouseLeave={hoverable ? (e) => e.currentTarget.style.borderColor = "var(--border)" : undefined}
    >{children}</div>
  );
}

function SectionHead({ title, sub, right }) {
  return (
    <div style={{display:"flex", alignItems:"baseline", justifyContent:"space-between", marginBottom: 12, gap: 16, flexWrap: "wrap"}}>
      <div style={{minWidth: 0}}>
        <h2 style={{fontSize: 18, fontWeight: 600, color: "var(--text)", margin: 0, lineHeight: 1.3}}>{title}</h2>
        {sub && <div className="t-mono" style={{color: "var(--text-3)", marginTop: 4, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis"}}>{sub}</div>}
      </div>
      {right && <div style={{display:"flex", alignItems:"center", gap: 8, flexWrap: "wrap"}}>{right}</div>}
    </div>
  );
}

function MonoLabel({ children, color }) {
  return (
    <span className="t-mono" style={{color: color || "var(--text-3)"}}>{children}</span>
  );
}

/* ============================================================
   Top nav
   ============================================================ */
function TopNav({ org = "Chen Property Holdings", onSearch, user = { initials: "MC", name: "Marcus Chen" } }) {
  return (
    <header style={{
      height: 56, background: "var(--bg)", borderBottom: "1px solid var(--border)",
      display: "flex", alignItems: "center", padding: "0 20px", gap: 20, flexShrink: 0,
    }}>
      <div style={{display:"flex", alignItems:"center", gap: 10, flex: 1, minWidth: 0}}>
        <div style={{
          width: 28, height: 28, borderRadius: 7, background: "var(--graphite)",
          display: "flex", alignItems: "center", justifyContent: "center", position: "relative", flexShrink: 0,
        }}>
          <span style={{fontFamily:"var(--font-serif)", fontSize:19, color:"#ffffff", lineHeight:1}}>A</span>
          <span style={{position:"absolute", top:3, right:3, width:5, height:5, borderRadius:"50%", background:"var(--blue)"}}/>
        </div>
        <span style={{fontFamily:"var(--font-serif)", fontSize: 22, letterSpacing: "-0.01em", color: "var(--text)"}}>Alphacon</span>
      </div>

      <div style={{
        flex: "0 1 460px", maxWidth: 460, minWidth: 0,
        background: "var(--blue-bg)", border: "1px solid var(--blue)", borderRadius: 9,
        padding: "7px 12px", display: "flex", alignItems: "center", gap: 8, cursor: "text",
        whiteSpace: "nowrap", overflow: "hidden",
      }}>
        <Icon name="search" size={14} color="var(--blue)"/>
        <span style={{fontSize: 12, color: "var(--blue-2)", overflow: "hidden", textOverflow: "ellipsis", flex: 1}}>Search properties, devices, stays…</span>
        <span style={{flexShrink: 0, fontFamily:"var(--font-mono)", fontSize:10, color:"var(--blue-2)", border:"1px solid var(--blue)", padding:"1px 5px", borderRadius:4}}>⌘ K</span>
      </div>

      <div style={{display:"flex", alignItems:"center", gap:12, flex: 1, minWidth: 0, justifyContent: "flex-end"}}>
        <button style={{background:"transparent", border:"none", cursor:"pointer", padding: 6, position:"relative"}}>
          <Icon name="bell" size={18} color="var(--text-2)"/>
          <span style={{position:"absolute", top:4, right:4, width:7, height:7, borderRadius:"50%", background:"var(--amber)"}}/>
        </button>
        <div style={{display:"flex", alignItems:"center", gap:8, padding: "3px 8px 3px 3px", borderRadius: 20, border: "1px solid var(--border)", cursor:"pointer"}}>
          <div style={{
            width: 26, height: 26, borderRadius: "50%", background: "var(--graphite)",
            color: "#ffffff", display:"flex", alignItems:"center", justifyContent:"center",
            fontFamily:"var(--font-mono)", fontSize: 10, fontWeight: 500, letterSpacing: 0.5,
          }}>{user.initials}</div>
          <span style={{fontSize: 12, color: "var(--text-2)", paddingRight: 4}}>{user.name.split(" ")[0]}</span>
        </div>
      </div>
    </header>
  );
}

/* ============================================================
   Sidebar
   ============================================================ */
function SidebarItem({ icon, label, active = false, badge, badgeVariant = "alert", onClick }) {
  return (
    <div onClick={onClick} style={{
      display:"flex", alignItems:"center", gap:10,
      padding: "7px 10px", borderRadius: 10,
      background: active ? "var(--side-surface)" : "transparent",
      border: active ? "1px solid var(--side-border)" : "1px solid transparent",
      cursor: "pointer",
    }}
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.background = "var(--side-surface)"; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.background = "transparent"; }}
    >
      <div style={{
        width: 24, height: 24, borderRadius: 7,
        background: active ? "var(--blue)" : "var(--side-surface)",
        display:"flex", alignItems:"center", justifyContent:"center",
        color: active ? "#ffffff" : "var(--side-text-2)", flexShrink: 0,
      }}>
        <Icon name={icon} size={13}/>
      </div>
      <span style={{
        fontSize: 13, color: active ? "var(--side-text)" : "var(--side-text-2)",
        fontWeight: active ? 600 : 400, flex: 1,
      }}>{label}</span>
      {active && <span style={{width: 5, height: 5, borderRadius: "50%", background: "var(--blue)", flexShrink: 0}}/>}
      {badge && (
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: "0.08em",
          padding: "2px 7px", borderRadius: 20, fontWeight: 600,
          background: badgeVariant === "alert" ? "var(--red-bg)" : "var(--amber-bg)",
          color: badgeVariant === "alert" ? "var(--red)" : "var(--amber)",
        }}>{badge}</span>
      )}
    </div>
  );
}

function Sidebar({ width = 224, current, setCurrent }) {
  const item = (id, icon, label, badge, badgeVariant) =>
    <SidebarItem icon={icon} label={label} active={current === id} onClick={() => setCurrent(id)} badge={badge} badgeVariant={badgeVariant}/>;

  return (
    <aside style={{
      width, background: "var(--side-bg)", borderRight: "1px solid var(--side-border)",
      padding: "16px 12px", display: "flex", flexDirection: "column", gap: 2, flexShrink: 0,
      overflowY: "auto",
    }}>
      <div className="t-mono" style={{color: "var(--side-text-3)", padding: "8px 10px 4px"}}>Workspace</div>
      {item("overview",    "spark",  "Intelligence")}
      {item("portfolio",   "grid",   "Portfolio")}
      {item("devices",     "devices","Devices",      "1", "alert")}
      {item("integrations","plug",   "Integrations", "1", "warn")}
      {item("automations", "sparkles","Agentic automations")}

      <div style={{marginTop: "auto", paddingTop: 16}}>
        {item("team",     "users",    "Team")}
        {item("settings", "settings", "Settings")}
      </div>
    </aside>
  );
}

/* ============================================================
   AI Bar (graphite hero)
   ============================================================ */
function AIBar({ chips = ["energy report", "vacant units", "active alerts", "draft check-in"], placeholder, compact = false, onClick }) {
  return (
    <div onClick={onClick} style={{
      background: "linear-gradient(180deg, #2c2015 0%, #3a2b1c 100%)", border: "1px solid #4a3a28",
      borderRadius: 14,
      padding: compact ? "12px 16px" : "14px 18px",
      display: "flex", alignItems: "center", gap: 12, cursor: onClick ? "pointer" : "text",
    }}>
      <span style={{width:9, height:9, borderRadius:"50%", background:"var(--green)", boxShadow:"0 0 8px rgba(6,118,71,0.6)", flexShrink: 0}}/>
      <input
        readOnly={!!onClick}
        style={{
          flex: 1, background: "transparent", border: "none", outline: "none",
          color: "#e9ddca", fontFamily: "var(--font-sans)", fontStyle: "italic",
          fontSize: compact ? 13 : 14, minWidth: 0, cursor: onClick ? "pointer" : "text",
        }}
        placeholder={placeholder || "Ask anything about your portfolio — what's my total energy spend this week?"}
      />
      {!compact && (
        <div style={{display:"flex", gap:6}}>
          {chips.map((c) => (
            <button key={c} style={{
              fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase",
              padding: "5px 10px", borderRadius: 20, background: "rgba(233,221,202,0.1)", color: "#cdb999",
              fontWeight: 500, whiteSpace: "nowrap", cursor: "pointer", border: "1px solid rgba(233,221,202,0.16)",
            }}>{c}</button>
          ))}
        </div>
      )}
      <button style={{
        width: 30, height: 30, borderRadius: 8, background: "#e9ddca", color: "#2c2015",
        display:"flex", alignItems:"center", justifyContent:"center",
        fontWeight: 700, fontSize: 14, cursor: "pointer", border: "none", flexShrink: 0,
      }}>→</button>
    </div>
  );
}

/* ============================================================
   Stat Card
   ============================================================ */
function StatCard({ label, value, unit, sub, valueColor }) {
  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 13, padding: 18 }}>
      <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 12}}>{label}</div>
      <div style={{
        fontSize: 30, fontWeight: 600, lineHeight: 1, letterSpacing: "-0.01em",
        color: valueColor || "var(--text)", fontFeatureSettings: "'tnum'",
      }}>
        {value}{unit && <span style={{fontSize:18, color:"var(--text-3)", fontWeight:500, marginLeft: 2}}>{unit}</span>}
      </div>
      <div style={{height:1, background:"var(--border)", margin:"12px 0"}}/>
      <div style={{fontSize:12, color:"var(--text-3)"}}>{sub}</div>
    </div>
  );
}

/* ============================================================
   Alert Card
   ============================================================ */
function AlertCard({ severity = "amber", title, desc, meta, actions = [] }) {
  const dot = { amber: "var(--amber)", red: "var(--red)", green: "var(--green)", graphite: "var(--graphite)" }[severity];
  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 13, padding: 18 }}>
      <div style={{display:"flex", alignItems:"flex-start", gap: 12}}>
        <span style={{width:10, height:10, borderRadius:"50%", background: dot, marginTop: 6, flexShrink: 0}}/>
        <div style={{flex:1, minWidth: 0}}>
          <div style={{fontSize:14, fontWeight:500, lineHeight:1.4, color:"var(--text)"}}>{title}</div>
          <div style={{fontSize:12, color:"var(--text-2)", lineHeight: 1.55, marginTop: 6}}>{desc}</div>
          <div className="t-mono" style={{color: "var(--text-3)", marginTop: 10}}>{meta}</div>
        </div>
      </div>
      {actions.length > 0 && (
        <div style={{display:"flex", gap: 8, marginTop: 12, paddingLeft: 22, flexWrap:"wrap"}}>
          {actions.map((a, i) => (
            <Button key={i} variant={i === 0 ? "tagPrim" : "tagSec"}>{a}</Button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Property Card
   ============================================================ */
function PropertyCard({ name, address, status, units, occupied, alerts = 0, onClick }) {
  const sc = { ok: "var(--green)", warn: "var(--amber)", alert: "var(--red)" }[status];
  return (
    <div onClick={onClick} style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: 13, padding: 16, cursor: onClick ? "pointer" : "default",
      transition: "border-color var(--motion-fast) var(--ease-default)",
    }}
      onMouseEnter={(e) => e.currentTarget.style.borderColor = "var(--border-strong)"}
      onMouseLeave={(e) => e.currentTarget.style.borderColor = "var(--border)"}
    >
      <div style={{display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap: 10}}>
        <div style={{minWidth: 0}}>
          <div style={{fontFamily:"var(--font-serif)", fontSize:17, lineHeight:1.2, color:"var(--text)"}}>{name}</div>
          <div style={{fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-3)", marginTop: 3}}>{address}</div>
        </div>
        <span style={{width:10, height:10, borderRadius:"50%", background: sc, marginTop: 4, flexShrink: 0}}/>
      </div>
      <div style={{display:"flex", flexWrap:"wrap", gap:6, marginTop: 12}}>
        {alerts > 0 && <Tag variant={status === "alert" ? "alert" : "warn"}>{alerts} alert{alerts>1?"s":""}</Tag>}
        {alerts === 0 && status === "ok" && <Tag variant="ok">All clear</Tag>}
        <Tag variant="neutral">{units} units</Tag>
        <Tag variant="neutral">{occupied}/{units} occupied</Tag>
      </div>
    </div>
  );
}

/* ============================================================
   Page header — used at the top of every pane
   ============================================================ */
function PageHeader({ title, sub, primary, secondary, eyebrow }) {
  return (
    <div style={{
      padding: "20px 28px", display: "flex", alignItems: "flex-end", justifyContent: "space-between",
      gap: 16, borderBottom: "1px solid var(--border)", background: "var(--surface)", flexWrap: "wrap",
    }}>
      <div style={{minWidth: 0}}>
        {eyebrow && <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 6}}>{eyebrow}</div>}
        <h1 style={{fontFamily:"var(--font-serif)", fontSize: 26, lineHeight: 1.15, letterSpacing:"-0.01em", color:"var(--text)", margin: 0}}>
          {title}
        </h1>
        {sub && <div style={{fontSize:12, color:"var(--text-3)", marginTop: 4}}>{sub}</div>}
      </div>
      <div style={{display:"flex", gap: 8}}>
        {secondary}
        {primary}
      </div>
    </div>
  );
}

/* ============================================================
   Tabs
   ============================================================ */
function Tabs({ tabs, value, onChange }) {
  return (
    <div style={{display: "flex", gap: 4, borderBottom: "1px solid var(--border)"}}>
      {tabs.map(t => {
        const active = value === t.id;
        return (
          <button key={t.id} onClick={() => onChange(t.id)} style={{
            background: "transparent", border: "none", cursor: "pointer",
            padding: "10px 4px", marginRight: 18,
            fontFamily: "var(--font-sans)", fontSize: 13,
            color: active ? "var(--text)" : "var(--text-3)", fontWeight: active ? 600 : 500,
            borderBottom: `2px solid ${active ? "var(--blue)" : "transparent"}`,
            display: "inline-flex", alignItems: "center", gap: 8,
          }}>
            {t.label}
            {t.count != null && <Tag variant="neutral">{t.count}</Tag>}
          </button>
        );
      })}
    </div>
  );
}

/* ============================================================
   Owner badge (polymorphic)
   ============================================================ */
function OwnerBadge({ ownerType, ownerName }) {
  if (ownerType === "TENANT" || ownerType === "tenant") {
    const first = (ownerName || "").split(" ")[0];
    return <Tag variant="graphite" withDot>Tenant{first ? ` · ${first}` : ""}</Tag>;
  }
  return <Tag variant="neutral">Property</Tag>;
}

/* ============================================================
   Data table (rows with header)
   ============================================================ */
function DataTable({ columns, rows, onRowClick, footer }) {
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: 13, overflow: "hidden",
    }}>
      <div style={{
        display: "grid", gridTemplateColumns: columns.map(c => c.w || "1fr").join(" "),
        padding: "10px 16px", borderBottom: "1px solid var(--border)", background: "var(--surface-2)",
        gap: 12,
      }}>
        {columns.map(c => (
          <div key={c.k} className="t-mono" style={{color: "var(--text-3)", textAlign: c.align || "left"}}>{c.label}</div>
        ))}
      </div>
      <div>
        {rows.map((r, i) => (
          <div key={i}
            onClick={onRowClick ? () => onRowClick(r) : undefined}
            style={{
              display: "grid", gridTemplateColumns: columns.map(c => c.w || "1fr").join(" "),
              padding: "12px 16px", borderBottom: i < rows.length - 1 ? "1px solid var(--border)" : "none",
              gap: 12, alignItems: "center",
              cursor: onRowClick ? "pointer" : "default",
              transition: "background var(--motion-fast)",
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "var(--bg)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}
          >
            {columns.map(c => (
              <div key={c.k} style={{textAlign: c.align || "left", fontSize: 13, color: "var(--text)", minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: c.wrap ? "normal" : "nowrap"}}>
                {c.render ? c.render(r) : r[c.k]}
              </div>
            ))}
          </div>
        ))}
      </div>
      {footer && <div style={{padding: "10px 16px", borderTop: "1px solid var(--border)", background: "var(--surface-2)"}}>{footer}</div>}
    </div>
  );
}

/* ============================================================
   Field / form input
   ============================================================ */
function Field({ label, hint, children, error }) {
  return (
    <div style={{display: "flex", flexDirection: "column", gap: 6}}>
      <label style={{fontSize: 12, color: "var(--text-2)", fontWeight: 500}}>{label}</label>
      {children}
      {hint && !error && <div style={{fontSize: 11, color: "var(--text-3)"}}>{hint}</div>}
      {error && <div style={{fontSize: 11, color: "var(--red)"}}>{error}</div>}
    </div>
  );
}

function TextInput({ value, onChange, placeholder, autoFocus }) {
  return (
    <input
      value={value || ""} onChange={(e) => onChange && onChange(e.target.value)}
      placeholder={placeholder} autoFocus={autoFocus}
      style={{
        fontFamily: "var(--font-sans)", fontSize: 13, color: "var(--text)",
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: 9, padding: "9px 12px", outline: "none",
        transition: "border-color var(--motion-fast)",
      }}
      onFocus={(e) => e.target.style.borderColor = "var(--graphite)"}
      onBlur={(e) => e.target.style.borderColor = "var(--border)"}
    />
  );
}

function SelectInput({ value, onChange, options }) {
  return (
    <select
      value={value} onChange={(e) => onChange && onChange(e.target.value)}
      style={{
        fontFamily: "var(--font-sans)", fontSize: 13, color: "var(--text)",
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: 9, padding: "9px 12px", outline: "none", appearance: "menulist",
      }}
    >
      {options.map(o => (
        typeof o === "string"
          ? <option key={o} value={o}>{o}</option>
          : <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  );
}

/* ============================================================
   Vendor logo placeholder (mono initials)
   ============================================================ */
function VendorLogo({ name, size = 36 }) {
  const initials = name.split(/[\s]/).map(w => w[0]).slice(0, 2).join("").toUpperCase();
  const hue = (name.charCodeAt(0) * 17) % 360;
  return (
    <div style={{
      width: size, height: size, borderRadius: 8, flexShrink: 0,
      background: "var(--surface-2)", border: "1px solid var(--border)",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "var(--font-mono)", fontSize: size * 0.32, fontWeight: 600,
      color: "var(--graphite)", letterSpacing: "0.04em",
      backgroundImage: `linear-gradient(135deg, oklch(0.94 0.015 ${hue}) 0%, oklch(0.97 0.01 ${hue}) 100%)`,
    }}>
      {initials}
    </div>
  );
}

/* ============================================================
   Stepper (used in onboarding)
   ============================================================ */
function Stepper({ steps, current }) {
  return (
    <div style={{display: "flex", alignItems: "center", gap: 8}}>
      {steps.map((s, i) => {
        const done = i < current, active = i === current;
        return (
          <React.Fragment key={s}>
            <div style={{display: "flex", alignItems: "center", gap: 8}}>
              <div style={{
                width: 22, height: 22, borderRadius: "50%", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                background: done ? "var(--graphite)" : (active ? "var(--surface)" : "var(--surface-2)"),
                color: done ? "#ffffff" : "var(--text-2)",
                fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 600,
                border: `1px solid ${active ? "var(--graphite)" : "var(--border)"}`,
              }}>
                {done ? <Icon name="check" size={11}/> : (i + 1)}
              </div>
              <span style={{
                fontSize: 12, color: active ? "var(--text)" : "var(--text-3)",
                fontWeight: active ? 600 : 400, whiteSpace: "nowrap",
              }}>{s}</span>
            </div>
            {i < steps.length - 1 && <div style={{width: 28, height: 1, background: "var(--border)"}}/>}
          </React.Fragment>
        );
      })}
    </div>
  );
}

/* ============================================================
   Export
   ============================================================ */
Object.assign(window, {
  Icon, Tag, Button, Card, SectionHead, MonoLabel,
  TopNav, Sidebar, SidebarItem, AIBar,
  StatCard, AlertCard, PropertyCard,
  PageHeader, Tabs, OwnerBadge, DataTable,
  Field, TextInput, SelectInput, VendorLogo, Stepper,
});
