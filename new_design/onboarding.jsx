/* Alphacon AI — onboarding flow
   Five steps: Sign in → Org → Property → Integration → Invite team → Done
*/
/* global React, Icon, Tag, Button, Field, TextInput, SelectInput, Stepper, VendorLogo, VENDORS */
const { useState: useStateO } = React;

function OnboardingShell({ children, step, totalSteps, title, sub, onBack, onContinue, ctaLabel = "Continue", canContinue = true, secondary }) {
  return (
    <div style={{
      position: "fixed", inset: 0, background: "var(--bg)",
      zIndex: 100, overflow: "auto",
      display: "flex", flexDirection: "column",
    }}>
      <header style={{
        height: 64, padding: "0 32px", flexShrink: 0,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        borderBottom: "1px solid var(--border)", background: "var(--surface)",
      }}>
        <div style={{display: "flex", alignItems: "center", gap: 12}}>
          <div style={{
            width: 30, height: 30, borderRadius: 7, background: "var(--graphite)",
            display: "flex", alignItems: "center", justifyContent: "center", position: "relative"
          }}>
            <span style={{fontFamily:"var(--font-serif)", fontSize:20, color:"#ffffff", lineHeight:1}}>A</span>
          </div>
          <span style={{fontFamily:"var(--font-serif)", fontSize: 22, letterSpacing: "-0.01em"}}>Alphacon</span>
          <span style={{fontFamily:"var(--font-mono)", fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text-3)", padding: "3px 8px", border: "1px solid var(--border)", borderRadius: 20, marginLeft: 8, whiteSpace: "nowrap"}}>
            setup · step {step + 1} of {totalSteps}
          </span>
        </div>
        <div style={{fontSize: 12, color: "var(--text-3)"}}>
          Signed in as <span style={{color: "var(--text-2)", fontWeight: 500}}>marcus@chen.holdings</span>
        </div>
      </header>

      <div style={{
        flex: 1, padding: "40px 32px 80px",
        display: "flex", justifyContent: "center", overflowY: "auto",
      }}>
        <div style={{width: "100%", maxWidth: 720, display: "flex", flexDirection: "column", gap: 28}}>
          <Stepper steps={["Account", "Organization", "First property", "Integration", "Done"]} current={step}/>

          <div>
            <h1 style={{fontFamily: "var(--font-serif)", fontSize: 38, lineHeight: 1.1, letterSpacing: "-0.01em", margin: 0}}>{title}</h1>
            {sub && <p style={{fontSize: 14, color: "var(--text-2)", marginTop: 12, lineHeight: 1.55, maxWidth: 560}}>{sub}</p>}
          </div>

          {children}
        </div>
      </div>

      <footer style={{
        flexShrink: 0, padding: "16px 32px", borderTop: "1px solid var(--border)",
        background: "var(--surface)", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12,
      }}>
        <div>
          {onBack && <Button variant="ghost" icon="arrowLeft" onClick={onBack}>Back</Button>}
        </div>
        <div style={{display: "flex", gap: 8}}>
          {secondary}
          {onContinue && (
            <Button variant="primary" onClick={onContinue} iconRight={ctaLabel === "Finish" ? "check" : "arrow"} disabled={!canContinue} style={{opacity: canContinue ? 1 : 0.5}}>
              {ctaLabel}
            </Button>
          )}
        </div>
      </footer>
    </div>
  );
}

/* ============================================================
   Step 0 — Sign in / sign up
   ============================================================ */
function StepAccount({ onContinue }) {
  return (
    <OnboardingShell step={0} totalSteps={5}
      title="Welcome to Alphacon."
      sub="The operator console for property managers. Track occupancy, energy, devices, and stays — with an AI agent that handles the routine work for you."
      onContinue={onContinue}
      ctaLabel="Continue with email"
    >
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14,
        padding: 28, display: "flex", flexDirection: "column", gap: 18, maxWidth: 480,
      }}>
        <div style={{display: "flex", flexDirection: "column", gap: 12}}>
          <Field label="Work email">
            <TextInput value="marcus@chen.holdings" autoFocus/>
          </Field>
          <Field label="Password" hint="At least 12 characters">
            <TextInput value="••••••••••••••"/>
          </Field>
        </div>

        <div style={{display: "flex", alignItems: "center", gap: 12}}>
          <div style={{flex: 1, height: 1, background: "var(--border)"}}/>
          <span className="t-mono" style={{color: "var(--text-3)"}}>or</span>
          <div style={{flex: 1, height: 1, background: "var(--border)"}}/>
        </div>

        <div style={{display: "flex", flexDirection: "column", gap: 8}}>
          <Button variant="secondary" icon="mail">Send a magic link</Button>
          <Button variant="secondary">Continue with Google</Button>
          <Button variant="secondary">Continue with Apple</Button>
        </div>
      </div>

      <p style={{fontSize: 11, color: "var(--text-3)", lineHeight: 1.5, maxWidth: 480}}>
        By continuing you agree to the terms of service and privacy policy. We never share device telemetry or occupant data with third parties.
      </p>
    </OnboardingShell>
  );
}

/* ============================================================
   Step 1 — Organization
   ============================================================ */
function StepOrg({ onBack, onContinue }) {
  const [name, setName] = useStateO("Chen Property Holdings");
  const [tier, setTier] = useStateO("growth");
  const [legal, setLegal] = useStateO("Chen Holdings Ltd");

  const tiers = [
    { id: "starter", name: "Starter",  price: "£0",   sub: "Up to 3 properties",  feats: ["Manual device control","Email support"] },
    { id: "growth",  name: "Growth",   price: "£89",  sub: "Per portfolio · monthly", feats: ["Up to 25 properties","AI agent · Sonnet","Automations","Priority support"], recommended: true },
    { id: "scale",   name: "Scale",    price: "£249", sub: "Per portfolio · monthly", feats: ["Unlimited properties","AI agent · Opus","SSO","Audit log export","Account manager"] },
  ];

  return (
    <OnboardingShell step={1} totalSteps={5}
      title="Set up your organization."
      sub="Your organization is the top-level billing and legal entity. You can add more portfolios and properties later."
      onBack={onBack} onContinue={onContinue}
    >
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14,
        padding: 24, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16,
      }}>
        <Field label="Display name" hint="Shown across the app and on guest-facing communications.">
          <TextInput value={name} onChange={setName} autoFocus/>
        </Field>
        <Field label="Legal name">
          <TextInput value={legal} onChange={setLegal}/>
        </Field>
        <Field label="URL slug" hint="alphacon.ai/o/chen-holdings">
          <TextInput value="chen-holdings"/>
        </Field>
        <Field label="Billing country">
          <SelectInput value="United Kingdom" options={["United Kingdom", "Ireland", "France", "Germany", "Spain", "United States"]}/>
        </Field>
      </div>

      <div>
        <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 10}}>Subscription</div>
        <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
          {tiers.map(t => {
            const active = tier === t.id;
            return (
              <div key={t.id} onClick={() => setTier(t.id)} style={{
                background: active ? "var(--blue-bg)" : "var(--surface)",
                border: `1px solid ${active ? "var(--blue)" : "var(--border)"}`,
                borderRadius: 13, padding: 18, cursor: "pointer",
                boxShadow: active ? "0 0 0 3px var(--blue-bg)" : "none",
                position: "relative",
              }}>
                {t.recommended && (
                  <div style={{position: "absolute", top: -10, right: 12}}>
                    <Tag variant="graphite">Recommended</Tag>
                  </div>
                )}
                <div style={{display: "flex", alignItems: "baseline", justifyContent: "space-between"}}>
                  <span style={{fontSize: 14, fontWeight: 600}}>{t.name}</span>
                  <span style={{
                    width: 16, height: 16, borderRadius: "50%",
                    border: `1.5px solid ${active ? "var(--blue)" : "var(--border-strong)"}`,
                    background: active ? "var(--blue)" : "transparent",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>{active && <Icon name="check" size={10} color="#ffffff"/>}</span>
                </div>
                <div style={{fontFamily: "var(--font-serif)", fontSize: 28, lineHeight: 1.1, marginTop: 8}}>{t.price}</div>
                <div className="t-mono" style={{color: "var(--text-3)", marginTop: 4}}>{t.sub}</div>
                <ul style={{margin: "14px 0 0", padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 6}}>
                  {t.feats.map(f => (
                    <li key={f} style={{fontSize: 12, color: "var(--text-2)", display: "flex", alignItems: "flex-start", gap: 8}}>
                      <Icon name="check" size={12} color="var(--green)"/>{f}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    </OnboardingShell>
  );
}

/* ============================================================
   Step 2 — First property
   ============================================================ */
function StepProperty({ onBack, onContinue }) {
  const [name, setName] = useStateO("Maple Court");
  const [type, setType] = useStateO("MIXED_USE");

  return (
    <OnboardingShell step={2} totalSteps={5}
      title="Add your first property."
      sub="A property is a single physical building. You'll add devices and stays to it next."
      onBack={onBack} onContinue={onContinue}
    >
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14,
        padding: 24, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16,
      }}>
        <Field label="Property name" hint="Internal label — tenants don't see this.">
          <TextInput value={name} onChange={setName} autoFocus/>
        </Field>
        <Field label="Property type">
          <SelectInput value={type} onChange={setType} options={[
            { value: "SHORT_TERM_RENTAL", label: "Short-term rental" },
            { value: "LONG_TERM_RENTAL",  label: "Long-term rental" },
            { value: "MIXED_USE",         label: "Mixed-use building" },
            { value: "OWNER_OCCUPIED",    label: "Owner occupied" },
            { value: "COMMERCIAL",        label: "Commercial" },
          ]}/>
        </Field>
        <Field label="Address line 1">
          <TextInput value="14 Maple Court"/>
        </Field>
        <Field label="Address line 2">
          <TextInput value="Off Headrow"/>
        </Field>
        <Field label="City">
          <TextInput value="Leeds"/>
        </Field>
        <Field label="Postcode">
          <TextInput value="LS1 4AB"/>
        </Field>
        <Field label="Country">
          <SelectInput value="United Kingdom" options={["United Kingdom","Ireland","France"]}/>
        </Field>
        <Field label="Timezone">
          <SelectInput value="Europe/London" options={["Europe/London","Europe/Paris","Europe/Dublin","UTC"]}/>
        </Field>
      </div>

      <div>
        <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 10}}>Units & rooms (optional)</div>
        <div style={{
          background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 13,
          padding: 16, display: "flex", flexDirection: "column", gap: 10,
        }}>
          <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
            <div>
              <div style={{fontSize: 13, fontWeight: 500}}>Add the units inside this property.</div>
              <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 2}}>You can skip this and add them from Devices later.</div>
            </div>
            <Button variant="secondary" icon="plus" size="sm">Add unit</Button>
          </div>

          {["Flat 1A · 1 bed", "Flat 1B · 2 bed", "Flat 2A · studio", "Flat 3B · 2 bed", "Communal · entry + hall"].map((u) => (
            <div key={u} style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              padding: "8px 12px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 9,
            }}>
              <span style={{fontSize: 13}}>{u}</span>
              <Icon name="x" size={14} color="var(--text-3)"/>
            </div>
          ))}
        </div>
      </div>
    </OnboardingShell>
  );
}

/* ============================================================
   Step 3 — First integration
   ============================================================ */
function StepIntegration({ onBack, onContinue }) {
  const [selected, setSelected] = useStateO(["v_nest", "v_hue"]);
  const toggle = (id) => setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  return (
    <OnboardingShell step={3} totalSteps={5}
      title="Connect your first integration."
      sub="Integrations let Alphacon discover and control devices. We'll set up OAuth for each one — you can add more later."
      onBack={onBack} onContinue={onContinue}
      canContinue={selected.length > 0}
    >
      <div style={{display: "flex", gap: 8, alignItems: "center"}}>
        <Tag variant="neutral">All</Tag>
        <Tag variant="neutral">Thermostats</Tag>
        <Tag variant="neutral">Lights</Tag>
        <Tag variant="neutral">Locks</Tag>
        <Tag variant="neutral">Sensors</Tag>
        <Tag variant="neutral">Plugs & meters</Tag>
        <Tag variant="neutral">Hubs</Tag>
      </div>

      <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12}}>
        {VENDORS.map(v => {
          const active = selected.includes(v.id);
          return (
            <div key={v.id} onClick={() => toggle(v.id)} style={{
              background: active ? "var(--blue-bg)" : "var(--surface)",
              border: `1px solid ${active ? "var(--blue)" : "var(--border)"}`,
              borderRadius: 13, padding: 16, cursor: "pointer",
              display: "flex", alignItems: "center", gap: 12,
            }}>
              <VendorLogo name={v.name}/>
              <div style={{flex: 1, minWidth: 0}}>
                <div style={{display: "flex", alignItems: "center", gap: 8}}>
                  <span style={{fontSize: 14, fontWeight: 600}}>{v.name}</span>
                  {v.popular && <Tag variant="neutral">Popular</Tag>}
                </div>
                <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 3}}>{v.cats}</div>
              </div>
              <span style={{
                width: 22, height: 22, borderRadius: 6,
                background: active ? "var(--blue)" : "var(--surface-2)",
                border: `1px solid ${active ? "var(--blue)" : "var(--border)"}`,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>{active && <Icon name="check" size={12} color="#ffffff"/>}</span>
            </div>
          );
        })}
      </div>

      <div style={{
        background: "var(--amber-bg)", border: "1px solid var(--amber-bg)",
        borderRadius: 13, padding: 14, display: "flex", gap: 12, alignItems: "flex-start",
      }}>
        <Icon name="alert" size={16} color="var(--amber)"/>
        <div>
          <div style={{fontSize: 13, fontWeight: 500, color: "var(--amber)"}}>You'll be redirected to each vendor in turn.</div>
          <div style={{fontSize: 12, color: "var(--amber)", marginTop: 4, opacity: 0.85, lineHeight: 1.5}}>
            We use OAuth — we never see your vendor credentials. Each connection takes about 30 seconds. You can pause and resume from Settings → Integrations.
          </div>
        </div>
      </div>
    </OnboardingShell>
  );
}

/* ============================================================
   Step 4 — Done
   ============================================================ */
function StepDone({ onBack, onContinue }) {
  return (
    <OnboardingShell step={4} totalSteps={5}
      title="You're ready."
      sub="Here's what's set up so far. The agent will surface signals as soon as it sees enough device state — usually within a few minutes."
      onBack={onBack} onContinue={onContinue}
      ctaLabel="Open Alphacon"
    >
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14,
        padding: 24, display: "flex", flexDirection: "column", gap: 14,
      }}>
        {[
          { l: "Organization", v: "Chen Property Holdings · Growth plan", done: true },
          { l: "Portfolio",    v: "Northern Portfolio · 1 property", done: true },
          { l: "Property",     v: "Maple Court · leeds_ls1 · 5 units", done: true },
          { l: "Integrations", v: "Nest, Hue · connected · 23 devices discovered", done: true },
          { l: "Team",         v: "Just you — invite teammates from Settings", done: false },
        ].map(r => (
          <div key={r.l} style={{display: "flex", alignItems: "center", gap: 14}}>
            <span style={{
              width: 22, height: 22, borderRadius: "50%", flexShrink: 0,
              background: r.done ? "var(--green-bg)" : "var(--surface-2)",
              color: r.done ? "var(--green)" : "var(--text-3)",
              display: "flex", alignItems: "center", justifyContent: "center",
              border: r.done ? "none" : "1px solid var(--border)",
            }}>
              {r.done ? <Icon name="check" size={12}/> : <Icon name="plus" size={12}/>}
            </span>
            <div style={{flex: 1}}>
              <div style={{fontSize: 13, fontWeight: 500}}>{r.l}</div>
              <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 2}}>{r.v}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{
        background: "linear-gradient(180deg, var(--graphite) 0%, var(--graphite-2) 100%)",
        borderRadius: 14, padding: 24, color: "#ffffff",
      }}>
        <div className="t-mono" style={{color: "var(--text-3)", marginBottom: 10}}>From the agent</div>
        <div style={{fontSize: 15, lineHeight: 1.5, fontFamily: "var(--font-serif)"}}>
          "Hi Marcus — I'll watch Maple Court for the first 24 hours and learn the rhythms. I'll surface anything that needs your attention in the Overview pane. If you want me to take action automatically, set up an automation when you have a minute."
        </div>
        <div className="t-mono" style={{color: "var(--text-3)", marginTop: 12}}>
          claude-sonnet-4.6 · operator persona
        </div>
      </div>

      <div style={{display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12}}>
        {[
          { t: "Invite your team", s: "Add operators and contractors with scoped access." },
          { t: "Create an automation", s: "Pre-arrival warm-up, leak shut-off, daily summaries." },
          { t: "Read the brief",  s: "What the agent can do, and what it'll ask before doing." },
        ].map(c => (
          <div key={c.t} style={{
            background: "var(--surface)", border: "1px solid var(--border)",
            borderRadius: 13, padding: 16, cursor: "pointer",
          }}>
            <div style={{fontSize: 13, fontWeight: 500}}>{c.t}</div>
            <div style={{fontSize: 12, color: "var(--text-3)", marginTop: 6, lineHeight: 1.5}}>{c.s}</div>
            <div style={{marginTop: 10, fontSize: 12, color: "var(--text-2)", display: "flex", alignItems: "center", gap: 6}}>
              Open <Icon name="arrow" size={12}/>
            </div>
          </div>
        ))}
      </div>
    </OnboardingShell>
  );
}

/* ============================================================
   Onboarding router
   ============================================================ */
function Onboarding({ step, setStep, onFinish }) {
  const back = () => setStep(Math.max(0, step - 1));
  const next = () => setStep(step + 1);
  if (step === 0) return <StepAccount onContinue={next}/>;
  if (step === 1) return <StepOrg onBack={back} onContinue={next}/>;
  if (step === 2) return <StepProperty onBack={back} onContinue={next}/>;
  if (step === 3) return <StepIntegration onBack={back} onContinue={next}/>;
  if (step === 4) return <StepDone onBack={back} onContinue={onFinish}/>;
  return null;
}

Object.assign(window, { Onboarding });
