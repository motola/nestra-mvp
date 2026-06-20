/* TAB: Devices (global fleet)
   Alphacon AI — parchment + espresso. Reference design (recreate in your stack).
   Depends on shared primitives in components.jsx (Icon, Button, Tag, Card, PageHeader, Tabs, DataTable, StatCard, AlertCard, PropertyCard, OwnerBadge, MonoLabel, SectionHead) and data.js globals. */
/* global React, Icon, Tag, Button, Card, SectionHead, MonoLabel, AIBar, StatCard, AlertCard, PropertyCard, PageHeader, Tabs, OwnerBadge, DataTable, Field, TextInput, SelectInput, DeviceList, PORTFOLIOS, PROPERTIES, ROOMS_MAPLE, DEVICES_MAPLE, INTEGRATIONS, AUTOMATIONS, AUDIT, TEAM, VENDORS */
const { useState: useStateDevices } = React;

function DevicesScreen({ go }) {
  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Devices"
        sub="401 devices across 12 properties · synced from connected vendor integrations"
        primary={<Button variant="primary" icon="plus">Pair device</Button>}
        secondary={<Button variant="secondary" icon="refresh">Re-sync</Button>}
      />

      <div style={{padding: "20px 28px 32px", display: "flex", flexDirection: "column", gap: 20}}>
        <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
          <StatCard label="Total devices" value="401" sub="Across 12 properties"/>
          <StatCard label="Online" value="400" sub="Reporting normally"/>
          <StatCard label="Categories" value="8" sub="Thermostats, lights, locks, sensors…"/>
          <StatCard label="Unreachable" value="1" valueColor="var(--amber)" sub={<span style={{color: "var(--amber)"}}>Hallway motion · Maple Court</span>}/>
        </div>

        <SectionHead title="All devices" sub="MAPLE COURT — SHOWING 14 OF 401 · FILTER BY PROPERTY ABOVE"
          right={<Button variant="ghost" size="sm" icon="filter">Filters</Button>}/>
        <DeviceList devices={DEVICES_MAPLE} go={go}/>

        <Card style={{padding: 18, display: "flex", alignItems: "flex-start", gap: 14}}>
          <div style={{width: 36, height: 36, borderRadius: 8, background: "var(--graphite)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0}}>
            <Icon name="refresh" size={16} color="#ffffff"/>
          </div>
          <div style={{flex: 1}}>
            <div style={{fontSize: 13, fontWeight: 600, color: "var(--text)"}}>Devices stay in sync with your vendors</div>
            <div style={{fontSize: 12, color: "var(--text-2)", marginTop: 4, lineHeight: 1.6, maxWidth: 720}}>
              Every device is discovered through a connected integration and owned by the property. State updates arrive over vendor webhooks; if a device looks stale, re-sync pulls the latest from the vendor cloud.
            </div>
            <div style={{display: "flex", gap: 8, marginTop: 12}}>
              <Button variant="tagSec" size="sm">Manage integrations</Button>
              <Button variant="tagSec" size="sm">View sync log</Button>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}

/* ============================================================
   INTEGRATIONS
   ============================================================ */

Object.assign(window, { DevicesScreen });
