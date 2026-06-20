/* TAB: Intelligence (the agent home — tabbed chat + espresso composer)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateIntel } = React;

function OverviewScreen({ go }) {
  const totalUnits = PROPERTIES.reduce((s, p) => s + p.units, 0);
  const totalOcc = PROPERTIES.reduce((s, p) => s + p.occupied, 0);
  const occPct = Math.round((totalOcc / totalUnits) * 100);
  const totalAlerts = PROPERTIES.reduce((s, p) => s + p.alerts, 0);
  const totalDevices = PROPERTIES.reduce((s, p) => s + p.devices, 0);

  const SEED_CHATS = [
    { id: "c_energy", title: "Energy spend this week", when: "12 min ago", messages: [
      { role: "you", text: "What was my energy spend this week and where did most of it go?" },
      { role: "ai", text: "Portfolio used 312 kWh last week — £77.20 total, 8% below your weekly average. Maple Court was the largest at £19.40, driven mostly by Flat 3B running heating while vacant. I turned that off Wednesday." },
    ]},
    { id: "c_hub", title: "Northbrook hub restart", when: "1h ago", messages: [
      { role: "you", text: "Why are the Northbrook thermostats offline?" },
      { role: "ai", text: "Flat 2A and 4B stopped reporting at 06:47 — likely a hub disconnect. A remote restart usually clears it. Want me to restart the hub?" },
    ]},
    { id: "c_vacancy", title: "Maple Court vacancy options", when: "yesterday", messages: [
      { role: "you", text: "What are my options for the vacant Flat 3B?" },
      { role: "ai", text: "Three options: drop the thermostat to 14°C (saves ~£12/day), set a pre-arrival warm-up automation, or list it for short-let. I can set any of these up." },
    ]},
  ];

  const [chats, setChats] = useStateIntel(() => [{ id: "new0", title: "New chat", when: "now", messages: [] }, ...SEED_CHATS]);
  const [activeId, setActiveId] = useStateIntel("new0");
  const [draft, setDraft] = useStateIntel("");
  const [showActions, setShowActions] = useStateIntel(false);
  const [showActivity, setShowActivity] = useStateIntel(false);

  const active = chats.find(c => c.id === activeId) || chats[0];

  const newChat = () => {
    const id = "new" + Date.now();
    setChats(cs => [{ id, title: "New chat", when: "now", messages: [] }, ...cs]);
    setActiveId(id);
    setShowActions(false);
  };

  const closeTab = (id, e) => {
    e.stopPropagation();
    setChats(cs => {
      const next = cs.filter(c => c.id !== id);
      const safe = next.length ? next : [{ id: "new0", title: "New chat", when: "now", messages: [] }];
      if (id === activeId) setActiveId(safe[0].id);
      return safe;
    });
  };

  const cannedReply = (text) => {
    const t = text.toLowerCase();
    if (/energy|spend|cost/.test(t)) return "Portfolio is tracking £1,389 this month, 12% below budget. Maple Court is the largest line at £298. Want a breakdown by property?";
    if (/vacant|empty/.test(t)) return "3 units are vacant right now: Maple Court Flat 3B + Flat 1A, and Albany Mews Flat 4. Flat 3B still had heating on — I can switch it off.";
    if (/offline|device|hub/.test(t)) return "2 devices are offline: Northbrook Mill thermostats (Flat 2A, 4B) since 06:47. A remote hub restart usually clears it — shall I?";
    if (/add (a )?property/.test(t)) return "Opening the new-property form. I'll pre-fill the timezone and currency from your org defaults.";
    if (/report/.test(t)) return "I've drafted the weekly energy summary for marcus@ and theo@. Review it and I'll schedule it for every Monday 08:00.";
    return "On it. I'll gather the data and show exactly what I checked — and I'll ask before anything that changes device state.";
  };

  const send = (text) => {
    const msg = (text != null ? text : draft).trim();
    if (!msg) return;
    setChats(cs => cs.map(c => c.id === activeId ? {
      ...c,
      title: c.messages.length === 0 ? (msg.length > 36 ? msg.slice(0, 36) + "…" : msg) : c.title,
      when: "now",
      messages: [...c.messages, { role: "you", text: msg }, { role: "ai", text: cannedReply(msg) }],
    } : c));
    setDraft("");
    setShowActions(false);
  };

  return (
    <div style={{display: "flex", flexDirection: "column", minHeight: "100%"}}>
      {/* Header */}
      <div style={{padding: "12px 28px 0", background: "var(--surface)", borderBottom: "1px solid var(--border)"}}>
        {/* Conversation tabs (left) + actions (right) on one row */}
        <div style={{display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 16}}>
          <div style={{display: "flex", gap: 4, overflowX: "auto", flex: 1, minWidth: 0}}>
            {chats.map(c => {
              const on = c.id === activeId;
              return (
                <button key={c.id} onClick={() => setActiveId(c.id)} style={{
                  display: "inline-flex", alignItems: "center", gap: 8, flexShrink: 0,
                  maxWidth: 230, padding: "8px 12px", cursor: "pointer",
                  background: on ? "var(--bg)" : "transparent",
                  border: "1px solid " + (on ? "var(--border)" : "transparent"),
                  borderBottom: on ? "1px solid var(--bg)" : "1px solid transparent",
                  borderRadius: "9px 9px 0 0", marginBottom: -1,
                  fontFamily: "var(--font-sans)",
                }}>
                  <Icon name={c.messages.length ? "chat" : "sparkles"} size={13} color={on ? "var(--blue)" : "var(--text-3)"}/>
                  <span style={{fontSize: 12, fontWeight: on ? 600 : 400, color: on ? "var(--text)" : "var(--text-2)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis"}}>{c.title}</span>
                  <span onClick={(e) => closeTab(c.id, e)} title="Close" style={{display: "inline-flex", color: "var(--text-3)", borderRadius: 4, padding: 1}}>
                    <Icon name="x" size={12}/>
                  </span>
                </button>
              );
            })}
          </div>
          <div style={{display: "flex", gap: 8, alignItems: "center", flexShrink: 0, paddingBottom: 8}}>
            <IconButton icon="history" label="Recent activity" onClick={() => setShowActivity(true)}/>
            <Button variant="secondary" icon="book" onClick={() => go("audit")}>History</Button>
            <Button variant="primary" icon="plus" onClick={newChat}>New chat</Button>
          </div>
        </div>
      </div>

      {/* Canvas — empty greeting state or the active transcript */}
      {active.messages.length === 0 ? (
        <div style={{
          flex: 1, minHeight: 0,
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          padding: "40px 28px", textAlign: "center", gap: 16,
        }}>
          <div style={{width: 52, height: 52, borderRadius: 13, background: "var(--blue)", display: "flex", alignItems: "center", justifyContent: "center"}}>
            <Icon name="sparkles" size={24} color="#ffffff"/>
          </div>
          <div style={{maxWidth: 520}}>
            <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 10}}>HELLO MARCUS</div>
            <h2 style={{fontFamily: "var(--font-serif)", fontSize: 40, fontWeight: 400, lineHeight: 1.12, margin: 0, letterSpacing: "-0.01em"}}>
              What would you like to do?
            </h2>
            <p style={{fontSize: 13, color: "var(--text-2)", marginTop: 10, lineHeight: 1.6}}>
              {PROPERTIES.length} properties · {totalUnits} units · {totalOcc} occupied · {totalAlerts} active alerts overnight. Ask about your portfolio or run an action — I'll show what I did and ask before anything that changes device state.
            </p>
          </div>
        </div>
      ) : (
        <div style={{flex: 1, minHeight: 0, overflowY: "auto", padding: "24px 28px 8px"}}>
          <div style={{maxWidth: 760, margin: "0 auto", display: "flex", flexDirection: "column", gap: 20}}>
            {active.messages.map((m, i) => (
              <div key={i} style={{display: "flex", gap: 14, alignItems: "flex-start"}}>
                <span className="t-mono" style={{color: m.role === "ai" ? "var(--green)" : "var(--text-3)", width: 28, flexShrink: 0, paddingTop: 2}}>{m.role === "ai" ? "AI" : "You"}</span>
                <div style={{flex: 1, fontSize: 14, lineHeight: 1.65, color: m.role === "ai" ? "var(--text)" : "var(--text-2)"}}>{m.text}</div>
              </div>
            ))}
            <div style={{display: "flex", justifyContent: "center", paddingTop: 4}}>
              <Button variant="ghost" size="sm" iconRight="arrow" onClick={() => go("agent")}>Open in full agent view</Button>
            </div>
          </div>
        </div>
      )}

      {/* Composer — anchored to the bottom of the pane */}
      <div style={{
        position: "sticky", bottom: 0, zIndex: 5,
        padding: "14px 28px 24px",
        background: "linear-gradient(180deg, rgba(247,248,250,0) 0%, var(--bg) 36%)",
      }}>
        {showActions && <QuickActionsTray go={go} onPick={(label) => send(label)} onClose={() => setShowActions(false)}/>}
        <div style={{display: "flex", gap: 10, alignItems: "flex-end"}}>
          <button onClick={() => setShowActions(v => !v)} title="Quick actions" style={{
            flexShrink: 0, height: 50, padding: "0 16px", borderRadius: 14, cursor: "pointer",
            whiteSpace: "nowrap",
            background: showActions ? "var(--graphite)" : "var(--surface)",
            color: showActions ? "#ffffff" : "var(--text)",
            border: `1px solid ${showActions ? "var(--graphite)" : "var(--border)"}`,
            display: "inline-flex", alignItems: "center", gap: 8, fontFamily: "var(--font-sans)", fontSize: 13, fontWeight: 500,
            transition: "all var(--motion-fast)",
          }}>
            <Icon name="bolt" size={16} color={showActions ? "#ffffff" : "var(--graphite)"}/>
            Quick actions
            <Icon name={showActions ? "x" : "chevron"} size={13} color={showActions ? "#ffffff" : "var(--text-3)"}/>
          </button>
          <div style={{
            flex: 1, minWidth: 0,
            background: "var(--blue)",
            border: "1px solid var(--blue-2)",
            borderRadius: 14, padding: "12px 14px", display: "flex", alignItems: "center", gap: 12,
          }}>
            <span style={{width: 9, height: 9, borderRadius: "50%", background: "var(--green)", boxShadow: "0 0 8px rgba(6,118,71,0.6)", flexShrink: 0}}/>
            <input
              value={draft}
              className="agent-composer-input"
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") send(); }}
              placeholder="Ask anything, or run an action — “add a property”, “draft the weekly energy report”…"
              style={{flex: 1, background: "transparent", border: "none", outline: "none", boxShadow: "none", padding: 0, margin: 0, color: "#ffffff", fontFamily: "var(--font-sans)", fontSize: 14, minWidth: 0}}
            />
            <style>{`.agent-composer-input::placeholder{color:#ffffff;opacity:1;}`}</style>
            <button onClick={() => send()} title="Send" style={{
              width: 30, height: 30, borderRadius: 8, background: "#fbf3e4", color: "#5e3c1a",
              display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 14, cursor: "pointer", border: "none", flexShrink: 0,
            }}>→</button>
          </div>
        </div>
        <div style={{display: "flex", justifyContent: "space-between", marginTop: 8, paddingInline: 2}}>
          <span style={{fontSize: 11, color: "var(--text-3)"}}>Operator persona · asks before any action that changes device state</span>
          <span className="t-mono" style={{color: "var(--text-3)"}}>⌘ K to focus · ⏎ to send</span>
        </div>
      </div>

      {showActivity && <ActivityDrawer go={go} onClose={() => setShowActivity(false)}/>}
    </div>
  );
}

/* ---- Recent-activity icon button (sits beside History) ---- */

function IconButton({ icon, label, onClick }) {
  return (
    <button onClick={onClick} title={label} aria-label={label} style={{
      width: 36, height: 36, borderRadius: 9, cursor: "pointer",
      background: "var(--surface)", border: "1px solid var(--border)",
      display: "inline-flex", alignItems: "center", justifyContent: "center", color: "var(--text-2)",
      transition: "border-color var(--motion-fast)",
    }}
      onMouseEnter={(e) => e.currentTarget.style.borderColor = "var(--border-strong)"}
      onMouseLeave={(e) => e.currentTarget.style.borderColor = "var(--border)"}
    >
      <Icon name={icon} size={16}/>
    </button>
  );
}

/* ---- Quick actions tray — the lookups we surfaced earlier, on tap ---- */

function QuickActionsTray({ go, onClose, onPick }) {
  const actions = [
    { id: "energy",   icon: "energy", label: "Energy spend this week",  answer: "£77.20 across 12 properties — 8% below your weekly average. Maple Court is the largest at £19.40." },
    { id: "vacant",   icon: "building", label: "Vacant units right now", answer: "3 vacant: Maple Court Flat 3B + Flat 1A, and Albany Mews Flat 4. Flat 3B still had heating on." },
    { id: "offline",  icon: "devices", label: "Devices offline",         answer: "2 offline: Northbrook Mill thermostats (Flat 2A, 4B) since 06:47, and 1 unreachable sensor at Maple Court." },
    { id: "approve",  icon: "check",  label: "Waiting for my approval",  answer: "2 items: turn off vacant heating at Maple Court, and the drafted weekly energy report." },
    { id: "attention",icon: "alert",  label: "Properties needing attention", answer: "2 right now: Maple Court (vacant heating) and Northbrook Mill (2 thermostats offline)." },
    { id: "digest",   icon: "history",label: "Overnight digest",         answer: "Quiet night. Agent cooled 1 vacant unit, a hub dropped at Northbrook, and 1 report is awaiting review." },
    { id: "report",   icon: "mail",   label: "Run weekly energy report", answer: "Drafting the Monday summary for marcus@ and theo@…" },
    { id: "add",      icon: "plus",   label: "Add a property",           answer: "Opening the new-property form…" },
  ];
  const [picked, setPicked] = useStateIntel(null);

  return (
    <div style={{
      marginBottom: 12, background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: 14, padding: 14, boxShadow: "var(--shadow-md)",
    }}>
      <div style={{display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12}}>
        <div style={{display: "flex", alignItems: "center", gap: 8}}>
          <Icon name="bolt" size={14} color="var(--graphite)"/>
          <span style={{fontSize: 13, fontWeight: 600}}>Quick actions</span>
          <MonoLabel>cached · one tap · no reasoning spend</MonoLabel>
        </div>
        <button onClick={onClose} style={{background: "transparent", border: "none", cursor: "pointer", color: "var(--text-3)", padding: 2}}>
          <Icon name="x" size={16}/>
        </button>
      </div>

      <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8}}>
        {actions.map(a => {
          const on = picked === a.id;
          return (
            <button key={a.id} onClick={() => setPicked(on ? null : a.id)} style={{
              display: "flex", alignItems: "center", gap: 8, textAlign: "left",
              padding: "10px 12px", borderRadius: 10, cursor: "pointer",
              background: on ? "var(--bg)" : "var(--surface)",
              border: `1px solid ${on ? "var(--border-strong)" : "var(--border)"}`,
              fontFamily: "var(--font-sans)", transition: "all var(--motion-fast)",
            }}
              onMouseEnter={(e) => { if (!on) e.currentTarget.style.borderColor = "var(--border-strong)"; }}
              onMouseLeave={(e) => { if (!on) e.currentTarget.style.borderColor = "var(--border)"; }}
            >
              <span style={{width: 26, height: 26, borderRadius: 7, flexShrink: 0, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-2)"}}>
                <Icon name={a.icon} size={13}/>
              </span>
              <span style={{fontSize: 12, fontWeight: 500, color: "var(--text)", lineHeight: 1.3}}>{a.label}</span>
            </button>
          );
        })}
      </div>

      {picked && (
        <div style={{marginTop: 12, padding: "12px 14px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 10, display: "flex", flexDirection: "column", gap: 8}}>
          <div style={{fontSize: 13, color: "var(--text)", lineHeight: 1.6}}>{actions.find(a => a.id === picked).answer}</div>
          <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
            <MonoLabel>instant · 0 reasoning tokens</MonoLabel>
            <span onClick={() => { const a = actions.find(x => x.id === picked); onPick ? onPick(a.label) : go("agent"); }} style={{fontSize: 11, color: "var(--blue)", fontWeight: 500, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4}}>
              Ask in chat <Icon name="arrow" size={11}/>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---- Recent activity slide-over (opened from the icon beside History) ---- */

function ActivityDrawer({ go, onClose }) {
  return (
    <div style={{position: "fixed", inset: 0, zIndex: 60, display: "flex", justifyContent: "flex-end"}}>
      <div onClick={onClose} style={{position: "absolute", inset: 0, background: "rgba(16,24,40,0.28)"}}/>
      <div style={{
        position: "relative", width: 380, maxWidth: "92vw", height: "100%",
        background: "var(--surface)", borderLeft: "1px solid var(--border)",
        boxShadow: "var(--shadow-lg)", display: "flex", flexDirection: "column",
      }}>
        <div style={{padding: "18px 20px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between"}}>
          <div>
            <h3 style={{fontSize: 14, fontWeight: 600, margin: 0}}>Recent activity</h3>
            <MonoLabel>Last 6h · live</MonoLabel>
          </div>
          <button onClick={onClose} style={{background: "transparent", border: "none", cursor: "pointer", color: "var(--text-3)", padding: 4}}>
            <Icon name="x" size={18}/>
          </button>
        </div>
        <div style={{flex: 1, overflowY: "auto", padding: "8px 20px 20px"}}>
          <ActivityList/>
        </div>
        <div style={{padding: "14px 20px", borderTop: "1px solid var(--border)"}}>
          <Button variant="secondary" icon="book" onClick={() => { onClose(); go("audit"); }} style={{width: "100%", justifyContent: "center"}}>
            Open full audit log
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ---- Pending approvals (retired — kept for reference) ---- */

function ConversationPreview() {
  return (
    <Card style={{padding: "16px 18px"}}>
      <div style={{display:"flex", alignItems:"center", gap:10, paddingBottom:12, borderBottom:"1px solid var(--border)"}}>
        <span style={{width:8, height:8, borderRadius:"50%", background:"var(--green)", boxShadow:"0 0 8px rgba(6,118,71,0.4)"}}/>
        <span style={{fontSize:13, fontWeight:600, color:"var(--text)"}}>Alphacon AI</span>
        <span className="t-mono" style={{color: "var(--text-3)", marginLeft: "auto"}}>claude-sonnet-4.6 · operator</span>
      </div>
      <div style={{display:"flex", flexDirection:"column", gap:14, paddingTop:14}}>
        <div style={{display:"flex", alignItems:"flex-start", gap:12}}>
          <span className="t-mono" style={{color: "var(--text-3)", width:24, flexShrink:0, paddingTop:2}}>You</span>
          <span style={{fontSize:13, lineHeight:1.6, color:"var(--text-2)"}}>What was my total energy cost last month across all properties?</span>
        </div>
        <div style={{display:"flex", alignItems:"flex-start", gap:12}}>
          <span className="t-mono" style={{color: "var(--green)", width:24, flexShrink:0, paddingTop:2}}>AI</span>
          <span style={{fontSize:13, lineHeight:1.6, color:"var(--text)"}}>
            Portfolio used <strong style={{fontWeight:600}}>1,247 kWh</strong> in March — <strong style={{fontWeight:600}}>£1,389 total</strong>, 12% below your £1,580 budget. Maple Court was the largest spend at £298, driven by the vacant unit running heating.
          </span>
        </div>
      </div>
    </Card>
  );
}

function ActivityList() {
  const items = [
    { time: "08:42", who: "Agent",  what: "Turned off heating in Maple Court Flat 3B", kind: "ok" },
    { time: "08:14", who: "Agent",  what: "Detected vacant heating in Maple Court Flat 3B", kind: "warn" },
    { time: "07:30", who: "Marcus", what: "Approved March report for team email", kind: "neutral" },
    { time: "06:47", who: "System", what: "Northbrook Mill hub stopped responding", kind: "alert" },
    { time: "Y'day", who: "Agent",  what: "Drafted check-in message for Larkspur House Flat 1", kind: "warn" },
  ];
  return (
    <ul style={{listStyle: "none", margin: 0, padding: 0, display:"flex", flexDirection:"column"}}>
      {items.map((it, i) => (
        <li key={i} style={{
          display:"flex", alignItems:"flex-start", gap: 10, padding: "10px 0",
          borderBottom: i < items.length - 1 ? "1px dashed var(--border)" : "none",
        }}>
          <span className="t-mono" style={{color: "var(--text-3)", width: 56, flexShrink: 0, paddingTop: 2}}>{it.time}</span>
          <span style={{
            width: 6, height: 6, borderRadius: "50%", marginTop: 7, flexShrink: 0,
            background: { ok:"var(--green)", warn:"var(--amber)", alert:"var(--red)", neutral:"var(--text-3)" }[it.kind],
          }}/>
          <div style={{flex: 1, minWidth: 0}}>
            <div style={{fontSize: 12, color: "var(--text)", lineHeight: 1.45}}>{it.what}</div>
            <div className="t-mono" style={{color: "var(--text-3)", marginTop: 2}}>{it.who}</div>
          </div>
        </li>
      ))}
    </ul>
  );
}

/* ============================================================
   PORTFOLIO
   ============================================================ */

Object.assign(window, { OverviewScreen, ActivityList });
