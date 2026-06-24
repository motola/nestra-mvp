# AlphaCon AI — Vision Gaps & Product Direction

*Strategic gaps in the product vision (not unbuilt features — holes in the strategy itself), plus directional decisions. Living document. Owned by product.*

---

## Directional decisions

### We are NOT selling energy savings
Energy savings is **not** a positioning or a value proposition for AlphaCon. Smart meters already ship with their own consumption apps; "save on your energy bill" is a commoditised, undifferentiated pitch we cannot win.

**Implication:** remove the energy product surface — the energy dashboard/page, energy charts, energy-savings framing in copy and demo content, and the `ENERGY_METER` device category. Raw power readings from a device (e.g. a smart plug) are incidental device state, never surfaced as an energy-savings feature.

**Where the value is instead:** preventing incidents, predictive maintenance, and guest/operational efficiency — outcomes no smart-meter app delivers.

---

## The gaps

### 1. The moat — "why AI?" is not yet answered
Today the agent is positioned as a *voice remote* (turn off lights, set heat). That's a feature, not a moat — anyone can wrap an LLM over vendor APIs. The defensible asset is the **cross-property data flywheel**: occupancy + device behaviour across many properties enabling failure prediction, anomaly detection, and benchmarking. **Reframe the product as intelligence-first, with control as the actuator.** Detect and prevent problems autonomously; don't just respond to commands.

### 2. Trust & safety — the real adoption blocker
We are asking operators to let an AI control **locks and heating in occupied homes.** That requires, as first-class product pillars (not footnotes):
- Hard boundaries — what the AI will **never** do autonomously.
- **Undo / rollback** of agent and automation actions.
- An **audit-trail UI** the operator actually trusts (viewing, not just writing).
- Confidence thresholds with human-in-the-loop for risky actions (the `<80% → review` rule is a good seed).
- A clear liability / insurance story.

### 3. It talks to devices, not the operator's stack
Property managers live in **booking platforms (Airbnb, Booking.com, Guesty, Hostaway), access/code systems, cleaning & maintenance dispatch, and accounting.** Smart-home control alone is a thin slice of their day, and `Stay` data (which drives automations like "2 hours before check-in") originates in booking platforms. Without these operational integrations, the AI is smart about lightbulbs and blind to the business. **Booking-platform → `Stay` is closer to core than to "deferred."**

### 4. Time-to-value / onboarding is hand-waved
The "5-minute, no-hardware onboarding" promise is the wedge and the most likely thing to break: heterogeneous vendor accounts, mapping **which device is in which room**, partial capability support, OAuth flows that fail. There is no onboarding / device-mapping design yet. B2B SaaS dies in onboarding.

### 5. Guest experience is treated as secondary — but for STR operators it IS the business
For short-term-rental managers, **guest experience = review scores = revenue.** Frictionless check-in/access, wifi, and climate via the Concierge persona could be the actual wedge that sells the platform, yet tenants are modelled as a secondary persona. There is a go-to-market wedge hiding here.

### 6. Cloud-to-cloud is a strategic vulnerability
The Phase-1 bet rides on vendor clouds that are rate-limited, flaky, and prone to deprecating APIs. An AI that can't reach the Nest cloud is *worse* than a dumb local system. **Graceful degradation** ("the device didn't respond — here's what I'll do about it") must be first-class behaviour, not an error toast.

---

## What to prioritise
1. **Reframe around proactive intelligence** — prevents problems, surfaces what matters; the moat and the ROI story.
2. **Make trust a pillar** — boundaries, undo, audit UI; unlocks the "let it control my locks" leap.
3. **Add operational integrations** (booking platforms first) — turns a gadget into a system of record.

The architecture is strong and does not block any of this — these are product/strategy gaps, not technical debt.
