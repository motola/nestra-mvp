/* Alphacon AI — MVP web app router
   Onboarding overlay → authenticated shell with sidebar nav.
*/
/* global React, ReactDOM, TopNav, Sidebar, Onboarding,
   OverviewScreen, PortfolioScreen, PropertyScreen, DevicesScreen, IntegrationsScreen,
   AutomationsScreen, SettingsScreen, TeamScreen, AgentScreen */
const { useState, useEffect } = React;

const SCREENS = {
  overview:     { label: "Overview",     comp: OverviewScreen },
  portfolio:    { label: "Portfolio",    comp: PortfolioScreen },
  property:     { label: "Maple Court",  comp: PropertyScreen },
  devices:      { label: "Devices",      comp: DevicesScreen },
  integrations: { label: "Integrations", comp: IntegrationsScreen },
  automations:  { label: "Agentic automations", comp: AutomationsScreen },
  agent:        { label: "Agent",        comp: AgentScreen },
  audit:        { label: "Audit log",    comp: (p) => <SettingsScreen {...p} initialTab="audit"/> },
  settings:     { label: "Settings",     comp: SettingsScreen },
  team:         { label: "Team",         comp: TeamScreen },
};

function App() {
  const [onboarding, setOnboarding] = useState(true);
  const [step, setStep] = useState(0);
  const [current, setCurrent] = useState("overview");

  // Persist state across refresh
  useEffect(() => {
    const saved = localStorage.getItem("alphacon-state");
    if (saved) {
      const s = JSON.parse(saved);
      setOnboarding(s.onboarding);
      setStep(s.step || 0);
      setCurrent(s.current || "overview");
    }
  }, []);
  useEffect(() => {
    localStorage.setItem("alphacon-state", JSON.stringify({ onboarding, step, current }));
  }, [onboarding, step, current]);

  const Comp = SCREENS[current]?.comp;
  const go = (id) => setCurrent(id);

  return (
    <div style={{height: "100vh", width: "100vw", display: "flex", flexDirection: "column", overflow: "hidden", background: "var(--bg)"}}>
      <TopNav/>
      <div style={{display: "flex", flex: 1, overflow: "hidden"}}>
        <Sidebar current={current} setCurrent={setCurrent}/>
        <main style={{flex: 1, overflowY: "auto", background: "var(--bg)", position: "relative"}}>
          {Comp && <Comp go={go}/>}
        </main>
      </div>

      {/* Bottom-right helper to revisit onboarding (prototype-only control) */}
      <div style={{
        position: "fixed", bottom: 14, right: 14, zIndex: 50,
        display: "flex", gap: 8, alignItems: "center",
      }}>
        <button onClick={() => { setStep(0); setOnboarding(true); }} style={{
          padding: "8px 14px", borderRadius: 9, cursor: "pointer",
          background: "var(--graphite)", color: "#ffffff",
          border: "none", fontSize: 12, fontWeight: 500, fontFamily: "var(--font-sans)",
          display: "inline-flex", alignItems: "center", gap: 6, whiteSpace: "nowrap",
          boxShadow: "0 8px 24px rgba(16,24,40,0.18)",
        }}>
          <span style={{width: 6, height: 6, borderRadius: "50%", background: "var(--blue-on-dark)"}}/>
          Replay onboarding
        </button>
      </div>

      {onboarding && (
        <Onboarding
          step={step}
          setStep={setStep}
          onFinish={() => { setOnboarding(false); setStep(0); setCurrent("overview"); }}
        />
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
