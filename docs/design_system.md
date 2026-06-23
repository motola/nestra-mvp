# AlphaCon AI — Design System Reference

*The full design system. Calibrated to the parchment direction (Prototype C). Every component, token, state, and pattern. Read alongside `prompts/claude_design.md` when designing new screens; read alongside `frontend/SKILL.md` when implementing them.*

---

## How to use this document

**For designers (using Claude Design in Claude.ai):**
- The lightweight version is in `prompts/claude_design.md` — paste that as the first message of a Claude.ai design session
- Consult this document for detailed component anatomy, states, and patterns when designing new screens
- Update this document when new patterns emerge — `prompts/claude_design.md` is derived from it

**For engineers (using Claude Code or working directly):**
- The Tailwind config snippet in section 2 drops into `frontend/tailwind.config.ts` — that's the implementation source of truth for tokens
- shadcn/ui primitive mappings tell you which primitives compose each AlphaCon pattern
- Every component's state matrix tells you what loading/empty/error/hover variants you must implement

**For reviewers:**
- The "Don't list" at the end captures explicit anti-patterns. If a design or PR introduces one of these, push back.

---

## Table of contents

1. [Brand principles](#1-brand-principles)
2. [Foundations](#2-foundations)
   - 2.1 [Colour](#21-colour)
   - 2.2 [Typography](#22-typography)
   - 2.3 [Spacing](#23-spacing)
   - 2.4 [Radius](#24-radius)
   - 2.5 [Shadow](#25-shadow)
   - 2.6 [Motion](#26-motion)
   - 2.7 [Iconography](#27-iconography)
   - 2.8 [Tailwind config snippet](#28-tailwind-config-snippet)
3. [Components](#3-components)
4. [Layouts](#4-layouts)
5. [The agent UI chapter](#5-the-agent-ui-chapter)
6. [Per-user-type design](#6-per-user-type-design)
7. [Copy tone](#7-copy-tone)
8. [Accessibility](#8-accessibility)
9. [Don't list](#9-dont-list)

---

## 1. Brand principles

Six principles that govern every visual decision. When in doubt, return to these.

### 1.1 Hospitality-thoughtful, not commodity SaaS
Most B2B SaaS uses cold blue/grey palettes that say "we're a serious tool." AlphaCon's customers run hospitality-adjacent businesses — properties people live in, sleep in, pay rent for. Our visual language reflects that: warm parchment instead of cold blue, serif headlines instead of generic sans, considered colour instead of neon utility. We look like something a property manager would *enjoy* using, not something IT installed for them.

### 1.2 The AI is the centerpiece, not a feature
The Claude-powered agent is the differentiating capability. The design treats it accordingly: the AI bar is the most prominent surface on every authenticated page, the agent gets its own visual language (graphite surfaces, mono labels, structured suggestions), and AI alerts get richer treatment than generic notifications. Decoration is restrained everywhere *except* where the AI lives — there, prominence is earned.

### 1.3 Restraint over decoration
No gradients (except on AI surfaces, intentionally). No glassmorphism. No animated illustrations. No emojis in production UI. No exclamation marks in copy. We sell to property management companies, not consumers. Every visual flourish has to earn its place.

### 1.4 Data is the hero
Property occupancy, device state, energy spend, agent-suggested savings — these are the things customers come to AlphaCon for. Type-set them well, give them breathing room, don't let chrome compete with content. Numbers should be larger than their labels by a clear margin. Status colours should be deeply saturated, not pastel.

### 1.5 Density without cramming
A property manager looks at 12 properties simultaneously. Tight grids, small body text (13–14px), clear hierarchy. But not airless — generous gutters between cards (16–20px), comfortable line-height (1.5–1.65), proper spacing between sections (20–24px). Information-dense but readable.

### 1.6 Every screen is print-screen-shareable
Operators send screenshots to colleagues constantly. Every screen has to read cleanly out of context: clear page title, visible status, no loading skeletons that hint at "this isn't real data," no decorative elements that confuse the meaning. Structure, then style.

---

## 2. Foundations

### 2.1 Colour

**Philosophy:** Warm cream parchment as base, graphite as the AI signal, three deeply-saturated status colours (green/amber/red), no gratuitous brand colour. White surfaces sit *on* parchment for content cards. The system uses 14 named colours total — restraint is intentional.

**Core palette**

| Token | Hex | Use |
|---|---|---|
| `bg` | `#f4f1eb` | App background — the parchment cream |
| `surface` | `#fbf9f4` | Card and panel backgrounds (sits on `bg`) |
| `surface-2` | `#efebe2` | Hover states, subtle alternate rows, sidebar inactive items |
| `border` | `#e0dbcf` | Default borders and dividers |
| `border-strong` | `#cdc6b8` | Emphasised borders, focus ring base |
| `text` | `#1a1814` | Body and heading text — *not* pure black |
| `text-2` | `#5a564e` | Secondary copy, captions, descriptions |
| `text-3` | `#a39d8e` | Tertiary, placeholders, metadata |

**Graphite (the AI palette)**

| Token | Hex | Use |
|---|---|---|
| `graphite` | `#28241e` | AI bar background, primary buttons, avatar backgrounds |
| `graphite-2` | `#3a3530` | Hover state for graphite, AI bar nested elements |

Graphite is *the* signal that the AI is involved. Use it on:
- The global AI bar
- Primary action buttons (where the action is the user's, but the system completes it)
- The AI agent's avatar surfaces
- The conversation panel's send button
- Sidebar `active` icon backgrounds
- Logo mark

Do **not** use graphite for:
- Text colour (use `text` instead — graphite is for surfaces)
- Borders (use `border` or `border-strong`)
- Status (use the green/amber/red palette)

**Status palette**

Three statuses + neutral. Each has a foreground colour and a tinted background.

| Status | Foreground | Background |
|---|---|---|
| Success | `green` `#2d6b2d` | `green-bg` `#eef5ee` |
| Warning | `amber` `#9a5e15` | `amber-bg` `#fbf2e3` |
| Error | `red` `#9a2828` | `red-bg` `#fbeeee` |
| Neutral | `text-2` `#5a564e` | `surface-2` `#efebe2` |

**Critical:** these are the *only* status colours. There is no info-blue, no purple, no separate "AI" colour beyond graphite. If a designer asks for "a blue accent here" — refuse and use neutral instead.

**Forbidden**
- Pure black (`#000`) anywhere — use `text` `#1a1814` or `graphite` `#28241e`
- Pure white (`#fff`) for backgrounds — use `surface` `#fbf9f4`
- Saturated/bright versions of any colour (no `#ff0000`, `#00ff00`, etc.)
- Gradients except on the AI bar's `graphite → graphite-2` subtle vertical (allowed but optional)

### 2.2 Typography

Three faces. Each has a single specific job; don't cross them.

**`Instrument Serif`** — display only
- Wordmark
- Page titles (the H1 of any view)
- Property names in cards (where they want to feel "named, not labeled")
- Marketing pages and landing
- *Not for*: body text, buttons, table headers, navigation, anything functional

**`DM Sans`** — everything else
- Body, navigation, forms, buttons, section titles, table content
- Default for any text that's not display or mono

**`DM Mono`** — metadata and structured data
- Labels in stat cards (`PROPERTIES`, `OCCUPANCY`)
- Sidebar section labels (`WORKSPACE`, `PROPERTIES`)
- Timestamp/category strings on alerts (`ENERGY · MAPLE COURT · TODAY 08:14 · 94% CONFIDENCE`)
- Property addresses in cards (`leeds_ls1`, lowercase intentional)
- IDs, codes, technical fields, model names (`claude-sonnet-4.6`)
- Conversation `YOU` / `AI` row labels
- *Not for*: body copy, descriptions, prose

**Type scale**

| Name | Size | Line height | Weight | Use |
|---|---|---|---|---|
| Display | 26px | 1.2 | 400 (serif) | Page titles |
| Display sm | 17px | 1.3 | 400 (serif) | Property card names |
| H2 | 18px | 1.3 | 600 | Section group titles |
| H3 | 14px | 1.4 | 600 | Section titles, card titles |
| Body lg | 14px | 1.55 | 400 | Body, paragraph copy |
| Body | 13px | 1.55 | 400 | Default body, table content |
| Small | 12px | 1.5 | 450 | Secondary info, descriptions |
| Caption | 11px | 1.4 | 500 | Tags, badges, sidebar items |
| Mono lg | 11px | 1.4 | 500 | Mono metadata, addresses |
| Mono | 10px | 1.4 | 500 | Mono labels (uppercase, with `letter-spacing: 0.08em`) |

**Typography rules**
- Page titles always Instrument Serif. Never sans for a page title.
- Body text never goes below 12px, even in dense tables.
- Mono labels are always UPPERCASE with letter-spacing 0.08em (the `var(--mono)` tracking from the prototype)
- Property addresses are intentionally lowercase mono (`leeds_ls1`) — gives a quietly technical feel that signals "this is a system, with structured data"
- Numbers use feature setting `'tnum'` (tabular numerals) on stat cards and tables to align cleanly. Add `font-feature-settings: 'tnum'` on numeric containers.

### 2.3 Spacing

Eight spacing tokens. Use these — don't invent intermediate values.

| Token | Pixels | Use |
|---|---|---|
| `space-1` | 4px | Inline gaps, tag internal padding |
| `space-2` | 8px | Default gap between adjacent siblings |
| `space-3` | 12px | Card internal padding (small), tag horizontal padding |
| `space-4` | 16px | Card internal padding (default) |
| `space-5` | 20px | Section spacing (between section heading and content) |
| `space-6` | 24px | Major section spacing, page padding |
| `space-7` | 32px | Top-level page header padding bottom |
| `space-8` | 48px | Empty state vertical padding |

**The 12 rule**: when in doubt about gap between two adjacent cards or panels, use 12px. It's the system's default rhythm.

**Page-level spacing**
- Page horizontal padding: 28px (was 24 in the old prototype; bumped up for breathing room)
- Page top padding: 24px
- Page bottom padding: 24px
- Gap between major sections in a page: 20px

### 2.4 Radius

Five radius tokens. Larger objects get larger radius — the rhythm is "bigger thing, more rounded" without crossing into playful.

| Token | Pixels | Use |
|---|---|---|
| `radius-tag` | 20px | Pills, badges, status tags (always fully rounded for tag/pill behaviour) |
| `radius-input` | 9px | Input fields, buttons, segmented controls |
| `radius-icon` | 8–9px | Icon backgrounds, avatars, send buttons |
| `radius-card` | 13px | Cards (alert, property, stat, conversation) |
| `radius-panel` | 14px | The AI bar — slightly larger than cards because it's prominent |

**Forbidden:** `rounded-full` on buttons (only on tags/badges), radius > 14px (we are not a consumer app), pill-shaped inputs.

### 2.5 Shadow

Used sparingly. Shadows have *meaning* — they signal elevation that exists for a functional reason (modals, dropdowns, popovers).

| Token | Value | Use |
|---|---|---|
| `shadow-sm` | `0 1px 2px rgba(26, 24, 20, 0.04)` | Hover lift on cards (subtle) |
| `shadow-md` | `0 4px 12px rgba(26, 24, 20, 0.08)` | Dropdowns, popovers |
| `shadow-lg` | `0 12px 32px rgba(26, 24, 20, 0.12)` | Modals, full-screen overlays |

The shadow colour is `text` rather than pure black — keeps the warm undertone consistent.

**Don't:** use shadow for resting state of cards (borders only), use shadow on the AI bar (it's already prominent), stack multiple shadows on one element.

### 2.6 Motion

Four duration tokens. AlphaCon's motion is functional, not decorative.

| Token | Duration | Easing | Use |
|---|---|---|---|
| `motion-fast` | 120ms | `ease-out` | Hover states, focus, button feedback |
| `motion` | 200ms | `ease-out` | Default transitions (most things) |
| `motion-slow` | 320ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Layout shifts, panel slides |
| `motion-streaming` | varies | `linear` | AI streaming token reveal — see agent chapter |

**Forbidden motion:** bouncy/elastic easing, decorative loops (spinners that exist for "polish"), entrance animations on initial page load, scroll-triggered reveals.

### 2.7 Iconography

Use **Lucide Icons** (already in shadcn/ui). 16px default for inline, 20px for navigation, 14px for tags.

**Stroke width 1.5** consistently. Lucide's default is 2 — change it via the `strokeWidth` prop.

Icons share the colour of their adjacent text. Don't tint icons differently from labels (avoids visual noise).

**Forbidden:** custom illustrated icons, gradients on icons, multi-colour icons, icon fonts other than Lucide.

### 2.8 Tailwind config snippet

This drops directly into `frontend/tailwind.config.ts` and is the implementation source of truth.

```typescript
import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./src/**/*.{ts,tsx}",
    "./node_modules/@/components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#f4f1eb",
        surface: "#fbf9f4",
        "surface-2": "#efebe2",
        border: "#e0dbcf",
        "border-strong": "#cdc6b8",
        text: "#1a1814",
        "text-2": "#5a564e",
        "text-3": "#a39d8e",
        graphite: {
          DEFAULT: "#28241e",
          2: "#3a3530",
        },
        green: {
          DEFAULT: "#2d6b2d",
          bg: "#eef5ee",
        },
        amber: {
          DEFAULT: "#9a5e15",
          bg: "#fbf2e3",
        },
        red: {
          DEFAULT: "#9a2828",
          bg: "#fbeeee",
        },
      },
      fontFamily: {
        serif: ['"Instrument Serif"', "Georgia", "serif"],
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
        mono: ['"DM Mono"', "ui-monospace", "monospace"],
      },
      fontSize: {
        display: ["26px", { lineHeight: "1.2", fontWeight: "400" }],
        "display-sm": ["17px", { lineHeight: "1.3", fontWeight: "400" }],
        h2: ["18px", { lineHeight: "1.3", fontWeight: "600" }],
        h3: ["14px", { lineHeight: "1.4", fontWeight: "600" }],
        "body-lg": ["14px", { lineHeight: "1.55" }],
        body: ["13px", { lineHeight: "1.55" }],
        small: ["12px", { lineHeight: "1.5", fontWeight: "450" }],
        caption: ["11px", { lineHeight: "1.4", fontWeight: "500" }],
        "mono-lg": ["11px", { lineHeight: "1.4", fontWeight: "500" }],
        mono: ["10px", { lineHeight: "1.4", fontWeight: "500", letterSpacing: "0.08em" }],
      },
      borderRadius: {
        tag: "20px",
        input: "9px",
        icon: "8px",
        card: "13px",
        panel: "14px",
      },
      boxShadow: {
        sm: "0 1px 2px rgba(26, 24, 20, 0.04)",
        DEFAULT: "0 4px 12px rgba(26, 24, 20, 0.08)",
        lg: "0 12px 32px rgba(26, 24, 20, 0.12)",
      },
      transitionDuration: {
        fast: "120ms",
        DEFAULT: "200ms",
        slow: "320ms",
      },
      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0, 0, 0.2, 1)",
        "out-soft": "cubic-bezier(0.2, 0.8, 0.2, 1)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
```

**Important**: load the three Google Fonts (Instrument Serif, DM Sans, DM Mono) via `next/font` in the root layout for self-hosting and zero CLS.

---

## 3. Components

Each component lists: anatomy, states, shadcn primitives that compose it, example Tailwind classes, and forbidden variants.

### 3.1 Button

**Anatomy:** `[icon? · label · keyboard-shortcut?]`

**Variants**

| Variant | Use | Tailwind |
|---|---|---|
| `primary` | The main action on a screen | `bg-graphite text-white px-4 py-2 rounded-input text-body font-medium hover:bg-graphite-2` |
| `secondary` | Secondary actions, "View …" buttons | `bg-surface text-text border border-border px-4 py-2 rounded-input text-body font-medium hover:bg-surface-2 hover:border-border-strong` |
| `ghost` | Inline actions, sidebar items | `text-text-2 px-3 py-1.5 rounded-input text-small hover:bg-surface-2 hover:text-text` |
| `tag-primary` | Action button inside an alert card | `bg-graphite text-white px-3 py-1.5 rounded-tag text-caption font-medium hover:bg-graphite-2` |
| `tag-secondary` | Secondary action inside an alert card | `bg-surface-2 text-text-2 border border-border px-3 py-1.5 rounded-tag text-caption font-medium hover:bg-bg` |
| `destructive` | Revoke, delete, irreversible | `bg-red text-white px-4 py-2 rounded-input text-body font-medium hover:bg-red/90` |

**States required**: default, hover, focus, active (pressed), disabled, loading

**shadcn primitive:** `Button` from `@/components/ui/button` — extend with the variants above.

**Forbidden:** rounded-full buttons (except `tag-*`), buttons with icon-only treatment without `aria-label`, pure-text "links that look like buttons", buttons more than one-line tall.

**Maximum 2 buttons per primary CTA group.** If you need 3, the third is `ghost`. If you need 4, redesign.

### 3.2 Tag / Badge

**Anatomy:** `[dot? · label]` — small, pill-shaped.

**Variants**

| Variant | Use | Tailwind |
|---|---|---|
| `tag-ok` | Healthy, all clear, success | `bg-green-bg text-green text-mono px-2 py-0.5 rounded-tag font-medium` |
| `tag-warn` | Vacant, attention, pending | `bg-amber-bg text-amber text-mono px-2 py-0.5 rounded-tag font-medium` |
| `tag-alert` | Error, security, critical | `bg-red-bg text-red text-mono px-2 py-0.5 rounded-tag font-medium` |
| `tag-neutral` | Counts, metadata | `bg-surface-2 text-text-2 border border-border text-mono px-2 py-0.5 rounded-tag font-medium` |

**States:** static (no hover/active — tags are content, not controls)

**Examples in use:**
- `<Tag variant="warn">1 alert</Tag>`
- `<Tag variant="neutral">6 units</Tag>`
- `<Tag variant="ok">All clear</Tag>`

**Forbidden:** tags as buttons (use a button), tags with icons except the optional leading dot, tags larger than 11px, tags that wrap to two lines.

### 3.3 Stat Card

**Anatomy:**
```
[label (mono, uppercase)]
[number (large, display weight)]
[divider]
[sub-line (small, optional trend colour)]
```

**Tailwind composition:**
```tsx
<div className="bg-surface border border-border rounded-card p-5">
  <div className="text-mono text-text-3 mb-3">PROPERTIES</div>
  <div className="text-[30px] font-semibold leading-none tracking-tight">3</div>
  <div className="h-px bg-border my-3" />
  <div className="text-small text-text-3">14 units total</div>
</div>
```

**Variants by trend:**
- `up` — sub-line uses `text-green font-medium` with `↑`
- `down` — sub-line uses `text-red font-medium` with `↓` and the number itself becomes `text-red`
- `neutral` — sub-line stays `text-text-3`, number stays `text-text`

**States:** default, loading (use shadcn `Skeleton` for number + sub-line, leave label visible)

**Forbidden:** stat cards with icons (the label IS the icon), more than 4 stat cards in a row (split into two rows), stat numbers below 24px.

### 3.4 Alert Card (AI-generated)

**Anatomy:**
```
[status dot] [title (body, semibold)]
              [description (small, text-2)]
              [meta (mono, uppercase)]
[primary action] [secondary action] [tertiary]
```

The most distinctive component in AlphaCon. Where the agent surfaces proactive recommendations.

**Tailwind composition:**
```tsx
<div className="bg-surface border border-border rounded-card p-5 cursor-pointer hover:border-border-strong">
  <div className="flex items-start gap-3">
    <div className="w-2.5 h-2.5 rounded-full bg-amber mt-1.5 shrink-0" />
    <div className="flex-1">
      <div className="text-body-lg font-medium leading-snug">
        Vacant unit heating on — Maple Court Flat 3B
      </div>
      <div className="text-small text-text-2 mt-1.5 leading-relaxed">
        Unit has been vacant for 4 days. Heating running at 20°C. Estimated waste £12/day.
        I can turn off and set a pre-arrival schedule automatically.
      </div>
      <div className="text-mono text-text-3 mt-2">
        ENERGY · MAPLE COURT · TODAY 08:14 · 94% CONFIDENCE
      </div>
    </div>
  </div>
  <div className="flex gap-2 mt-3">
    <Button variant="tag-primary">Turn off + schedule</Button>
    <Button variant="tag-secondary">Review unit</Button>
    <Button variant="tag-secondary">Dismiss</Button>
  </div>
</div>
```

**Status dot colours:**
- Amber: warning, optimisation opportunity (energy, vacancy)
- Red: critical, security, offline, error
- Green: positive (rare; usually for "all clear" messages)
- Graphite: neutral information from the agent

**States:** default, hover (border-strong), executing (action in progress — show inline spinner on the active button), executed (replace content with success state for 3s, then collapse), dismissed (fade out)

**Confidence display rule:** if the agent's confidence is below 80%, show "REVIEW NEEDED" instead of the percentage and disable any "auto-apply" primary button — only "Review and decide" remains.

**Forbidden:** alert cards without a meta line (always required), more than 3 actions, action labels longer than 4 words, alert cards that show pure text without any AI context.

### 3.5 Property Card

**Anatomy:**
```
[name (Instrument Serif)]      [status dot]
[address (mono, lowercase)]
[tag] [tag] [tag]
```

**Tailwind composition:**
```tsx
<div className="bg-surface border border-border rounded-card p-4 cursor-pointer hover:border-border-strong">
  <div className="flex items-start justify-between">
    <div>
      <div className="font-serif text-display-sm">Maple Court</div>
      <div className="text-mono-lg text-text-3 mt-0.5">leeds_ls1</div>
    </div>
    <div className="w-2.5 h-2.5 rounded-full bg-amber" />
  </div>
  <div className="flex flex-wrap gap-1.5 mt-2.5">
    <Tag variant="warn">1 alert</Tag>
    <Tag variant="neutral">6 units</Tag>
    <Tag variant="neutral">4 occupied</Tag>
  </div>
</div>
```

**The serif name is the signature.** Property names get Instrument Serif because they're proper nouns the customer named — they deserve typographic dignity.

**States:** default, hover, selected (active in sidebar — `bg-bg border-border` instead of `bg-surface border-border`)

**Forbidden:** property cards with images at MVP (icon-only, the name + address carry it), property cards without a status dot, property cards stacked more than 1 column wide for the sidebar overview (max 1 column to keep names readable).

### 3.6 Conversation Panel

**Anatomy:**
```
[header: dot · "Alphacon AI" · model meta (mono)]
[body: row stack]
  [row: WHO (mono) · message text]
  [row: WHO (mono) · message text]
  ...
[input: field · send button]
```

**Tailwind composition for a row:**
```tsx
<div className="flex items-start gap-2.5">
  <span className="font-mono text-mono font-medium text-text-3 w-8 mt-0.5 uppercase">YOU</span>
  <span className="text-body text-text-2 leading-relaxed flex-1">
    What was my total energy cost last month across all properties?
  </span>
</div>
```

**WHO labels:**
- `YOU` in `text-text-3` (the user)
- `AI` in `text-green` (the agent — green signals "speaking from a position of system knowledge")

**Message colours:**
- User messages: `text-text-2`
- AI messages: `text-text` and slightly stronger weight (`font-medium-ish` via `font-feature-settings: 'cv01'`) — they're authoritative

**States:** idle, streaming (last AI row has a pulsing cursor `▍`), tool-executing (after AI message, before next user input — see agent chapter for full treatment), error, escalated (handover to human — see agent chapter)

**Forbidden:** chat bubbles (we deliberately don't use them — the row format reads as a transcript, more authoritative than a casual chat), avatars in conversation rows, timestamps on every message (only on session start).

### 3.7 AI Bar (the global agent surface)

**Anatomy:**
```
[icon (graphite, with green dot)] [italic placeholder input] [chips] [send →]
```

**The single most important component.** It appears on every authenticated page. It's the primary entry point to the agent.

**Tailwind composition:**
```tsx
<div className="bg-graphite rounded-panel p-5 flex items-center gap-4">
  <div className="w-9 h-9 rounded-icon bg-graphite-2 flex items-center justify-center shrink-0">
    <div className="w-2.5 h-2.5 rounded-full bg-green" />
  </div>
  <input
    className="flex-1 bg-transparent border-none outline-none text-body-lg text-text-3 italic font-sans"
    placeholder="Ask anything about your portfolio — what's my total energy spend this week?"
  />
  <div className="flex gap-2">
    <Chip>energy report</Chip>
    <Chip>vacant units</Chip>
    <Chip>active alerts</Chip>
  </div>
  <button className="w-8 h-8 rounded-icon bg-bg flex items-center justify-center text-body font-bold">→</button>
</div>
```

**Chip component (specific to the AI bar):**
```tsx
<button className="text-caption px-3 py-1 rounded-tag bg-graphite-2 text-text-3 font-mono whitespace-nowrap hover:bg-[#4a4540] hover:text-[#d0c8b8]">
  {label}
</button>
```

**States:** idle (as above), focused (input has focus ring `ring-2 ring-green-bg`), submitting (chip suggestions hide, input shows loading shimmer), with-context (when on a Property page, prepend a context tag like "Maple Court · " inside the input)

**Forbidden:** AI bars not on a page, AI bars with light backgrounds (must be graphite), AI bars without chip suggestions, AI bars that disappear when scrolling (sticky behaviour at top is acceptable; full disappearance is not).

### 3.8 Sidebar Item

**Anatomy:**
```
[icon (rounded square)] [label] [badge?]
```

**Tailwind composition:**
```tsx
<div className="flex items-center gap-3 px-3 py-2.5 rounded-card cursor-pointer hover:bg-surface-2 [&[data-active=true]]:bg-bg [&[data-active=true]]:border [&[data-active=true]]:border-border">
  <div className="w-8 h-8 rounded-icon bg-surface-2 flex items-center justify-center [data-active=true]:bg-graphite">
    <div className="w-3 h-3 rounded-sm bg-text-3 [data-active=true]:bg-white" />
  </div>
  <span className="text-body text-text-2 [data-active=true]:text-text [data-active=true]:font-semibold">
    Overview
  </span>
  {badge && <span className="ml-auto bg-red-bg text-red text-mono px-1.5 py-0.5 rounded-tag font-semibold">{badge}</span>}
</div>
```

**Active state is structural, not just colour-shifted.** Inactive: `bg-surface-2` icon. Active: `bg-graphite` icon with white inner. This makes the active state feel weighted, not just highlighted.

### 3.9 Page Header

**Anatomy:**
```
[Page Title (Instrument Serif)]    [secondary button] [primary button]
[sub-line (small, text-3)]
```

Always sticky at top within the page scroll, with `border-b border-border bg-surface`. Sets context for the entire page.

```tsx
<div className="px-7 pt-6 pb-4.5 flex items-center justify-between border-b border-border bg-surface">
  <div>
    <h1 className="font-serif text-display tracking-tight">Good morning, Marcus</h1>
    <p className="text-small text-text-3 mt-1">Wednesday 1 April 2026 · 3 properties · 14 units · 2 active alerts</p>
  </div>
  <div className="flex gap-2">
    <Button variant="secondary">View portfolio</Button>
    <Button variant="primary">+ Add property</Button>
  </div>
</div>
```

---

## 4. Layouts

Five top-level layouts. Each authenticated page extends one.

### 4.1 Marketing layout (unauthenticated)
- Centered single-column, max-width 768px
- Page padding 64px top, 48px bottom
- Background `bg`, content cards on `surface`
- Used for: landing page, pricing, about, blog

### 4.2 Auth layout (signup, login, magic-link confirmation)
- Centered card on `surface-2` background, max-width 420px
- Vertically centered on viewport
- Logo at top of card
- Used for: `/signup`, `/login`, password reset, magic-link confirmation

### 4.3 App shell (authenticated operators)
- Top nav: 56px, `surface` with `border-b`
- Sidebar: 230px wide, `surface` with `border-r`
- Main: scrollable content with sticky page header
- This is the layout for all `(app)/*` routes (dashboard, portfolio, insights, devices, team, settings)

### 4.4 Tenant magic-link layout
- No sidebar (tenants don't need navigation)
- No top nav (just the AI bar at top, large and inviting)
- Full-width content, max-width 1024px on desktop
- Mobile-first; touch targets ≥ 44px
- Used for: tenant dashboard via magic link

### 4.5 Agent chat full-screen
- Like the conversation panel, but takes the whole viewport
- Top has a smaller header with persona indicator and back button
- Used for: dedicated agent conversations away from a specific page context

---

## 5. The agent UI chapter

The most important and tricky design surface in AlphaCon. The AI is the differentiating capability; how it presents itself shapes the entire product perception.

### 5.1 Three personas

The same Claude model, different filters, different tone, different tool catalogs. Visually distinct.

**OPERATOR persona** (Org/Portfolio/Property managers)
- Tone: precise, professional, action-oriented, data-rich
- Visual: full conversation panel, all chips visible, AgentRun cost displayed in `cp-meta`
- Vocabulary: technical, exact figures, percentages
- Example phrases: "Total energy cost across all 3 properties was £1,247." "I can create an automation."

**CONCIERGE persona** (short-term Tenants — Airbnb-style)
- Tone: warm but brief, helpful, no upselling
- Visual: simplified conversation panel, no AgentRun meta visible to the tenant, no model name shown
- Vocabulary: human, plain English, no jargon
- Example phrases: "The wifi password is `cottage-23-ash`. Anything else?" "I'll let the host know."

**HOME ASSISTANT persona** (long-term Tenants — renters)
- Tone: confident, friendly, like talking to your own home — not someone else's
- Visual: same as Concierge, but with personalised greeting and remembered preferences from `MemoryItem`
- Vocabulary: personal, "your devices", "your usual settings"
- Example phrases: "Welcome home, Sarah. Lights are on, heating is at your usual 20°C." "Want me to start the morning routine?"

**Each persona is visually identifiable by:**
- The header (`cp-title`): "Alphacon AI" (Operator) vs "Cottage assistant" (Concierge) vs "Your home" (Home Assistant)
- Whether `cp-meta` shows the model name (Operator yes, others no)
- Whether the AI's `WHO` label is `AI` (Operator) or hidden behind a softer label like a single avatar dot (others)
- Whether action chips appear (Operator yes, Concierge subtle suggestions only, Home Assistant rare)

### 5.2 Agent states

Five states every conversation must support.

**Idle**
- Last message is a user prompt or a complete AI reply
- Input field is enabled, focused, ready

**Streaming**
- AI is producing tokens
- Last AI row has a pulsing cursor `▍` after its current text content (animation: 1s opacity blink)
- Input is disabled, send button shows a small spinner
- The `cp-meta` line shows "Thinking…" rather than the model name during streaming

**Tool-executing**
- AI has called a tool (e.g., reading a device's current state, creating an automation)
- Inline below the AI message that triggered the call: a small "tool ribbon" — `text-mono text-text-3` with a graphite background pill: `▶ READING THERMOSTAT_LIVING_ROOM_3B…`
- When the tool completes, the ribbon collapses and is replaced by the AI's continuation
- Input remains disabled until the loop completes

**Escalating**
- Agent has determined the task exceeds its scope and is handing off
- An inline notice between rows: `→ Escalated to property manager (Marcus). They'll respond by email within 24h.`
- Notice has a `bg-amber-bg text-amber border-amber/20 rounded-card p-3`
- AgentRun is recorded with `outcome: ESCALATED`

**Error**
- The model failed, a tool failed, or the user hit a rate limit
- Replace the last AI row with an error state: `bg-red-bg text-red border-red/20 rounded-card p-3`
- Error must always include: what failed (in plain English), what to do next (retry / contact support), and the AgentRun ID for support reference (in `text-mono text-text-3`)
- The user can retry — the failed message is preserved, not lost

### 5.3 Agent output types

The agent produces five kinds of structured output (in addition to plain text). Each has a specific visual treatment.

**Plain text**
- The default. Just paragraph text in the conversation row.

**Device card (inline)**
- When the agent's response is "the state of a device" or "I'm controlling a device", render an inline device card *inside* the conversation row, after the agent's text
- Example: Agent says "Living room thermostat is at 19°C", then below it a compact device card showing the thermostat with its current state and an inline toggle/setpoint control
- Composition: small property + room context line, device name, current state, action (toggle / setpoint)

**Automation suggestion**
- When the agent proposes creating an automation, render a "suggestion preview" inside the conversation row
- Composition: a card with `bg-amber-bg/30 border-amber/20`, a title ("Suggested automation: Vacancy heating"), a 1-line summary, and three buttons: `Create`, `Tweak first`, `Not now`

**Tool result inline**
- When the agent shows the result of a database query (e.g., "Top 3 most expensive units this month"), render a small inline table with the same conventions as full tables — but with `text-small` and ≤ 5 rows
- If the result is > 5 rows, show top 5 and a "View all in Insights →" link

**Error explanation**
- See the Error state above

### 5.4 Agent visibility scope (security)

The agent's tool catalog is filtered *before* the LLM sees it, based on the actor's permissions. This is critical and has UX implications:

- A Tenant asking "unlock the front door" gets a polite "I can't help with that here — please contact your host" — because the lock tool is *not in the tool catalog* given to the LLM, not because the LLM refused
- An Operator asking "show me Maple Court flat 3B's current thermostat" gets the data — because the `device.get_state` tool IS in their catalog and includes that device
- The user never sees evidence of the filtering. There's no "Tool not available" — just naturally limited capability

**Design implication:** never show the user a list of "what the AI can do." It should feel boundless within their permission scope.

### 5.5 The handoff to the operator

When a Concierge agent hands off to a Property Manager (operator), the operator sees the conversation in their Insights view. Visual treatment:

- The conversation appears as a card with a header: `[Tenant name] · [Property/Stay] · escalated [time ago]`
- The full conversation transcript is below
- Two buttons at the bottom: `Reply to tenant` (opens an inline reply) and `Mark resolved` (closes without reply, logs to audit)

---

## 6. Per-user-type design

The design system applies broadly, but five user types use the product in different ways. Each gets calibrated treatment.

### 6.1 Org-level operator (e.g., Marcus, the founder/CEO)
- Multi-property dashboards, settings access, billing
- Higher information density (40+ rows per page is fine)
- Settings and admin in primary navigation

### 6.2 Portfolio-level operator (regional manager)
- Sees their portfolio only, not other portfolios
- Same component vocabulary as Org operator
- Billing/settings hidden in nav

### 6.3 Property-level operator (manager of a single building)
- Single-property focus throughout
- Sidebar shows just their assigned property
- Reduced settings (no team management, no billing)

### 6.4 Contractor (cleaner, maintenance, time-bound access)
- Mobile-first treatment
- Sidebar replaced with a flat property/job list
- Big tap targets (≥ 44px)
- Tasks visible, devices abstracted (they don't see the underlying tech)

### 6.5 Tenant (long-term or short-term)
- No sidebar
- Magic-link auth (no password)
- Concierge or Home Assistant persona
- Mobile-first
- The AI bar is the *primary navigation* — everything else is auxiliary

---

## 7. Copy tone

Every word of UI copy goes through this filter.

### 7.1 Voice principles
- **Direct over polite:** "Add property", not "Would you like to add a property?"
- **Specific over generic:** "We couldn't reach the Nest cloud", not "An error occurred"
- **Calm over urgent:** Errors don't yell. "This unit's heating sensor stopped reporting at 06:47" beats "ALERT: SENSOR OFFLINE"
- **Confident over hedging:** "I can create that automation" beats "I think I might be able to create that automation"

### 7.2 Mechanical rules
- Sentence case for everything: buttons, headings, menu items, table headers
- No exclamation marks anywhere in production UI (the AI is not excited; we are not excited)
- No emojis in production UI (acceptable in agent output if the user-initiated message contained one)
- Numbers as numerals always, even small ones: "3 properties", not "three properties"
- Currency always with the symbol prefixed: "£84", not "84 GBP"
- Time as user's locale (12-hour for UK English) with timezone abbreviation when ambiguous
- Dates as "Wednesday 1 April 2026" — full day name + day + month + year, no commas

### 7.3 Per-persona copy examples

**Operator persona** (precise, professional)
- "Your portfolio used 1,247 kWh this month — 12% below budget."
- "Maple Court Flat 3B has been vacant 4 days. I can drop the thermostat to 14°C. Want me to?"

**Concierge persona** (warm, brief)
- "Wifi password is `cottage-23-ash`."
- "I'll pass that to your host. They typically reply within a couple of hours."

**Home Assistant persona** (personal, confident)
- "Welcome home, Sarah. Heating is on, lights are warm in the living room."
- "Your usual evening setup — want me to run it?"

### 7.4 Errors

Every error message must answer three questions:
1. What happened? (in plain English)
2. What can the user do? (one specific action)
3. How can support help? (only if the first two don't resolve it)

Bad: "An error occurred. Please try again."
Good: "We couldn't reach the Nest cloud. This is usually temporary — try again in a minute. If it keeps happening, the device may need re-pairing."

---

## 8. Accessibility

Non-negotiable. Every component meets WCAG 2.1 AA at minimum.

### 8.1 Colour contrast
- Body text on background: 4.5:1 minimum (we test at 7:1 for `text` on `bg`)
- Large text and headings: 3:1 minimum (we test at 4.5:1)
- UI elements (buttons, inputs): 3:1 minimum against their background
- The `text-3` colour `#a39d8e` on `bg` `#f4f1eb` is borderline (3.2:1) — only use for non-essential metadata, never for primary content

### 8.2 Focus
- Every focusable element has a visible focus ring: `ring-2 ring-graphite ring-offset-2 ring-offset-bg`
- Never `outline: none` without a replacement
- Tab order matches visual order
- Skip-link at top of every page jumps to main content

### 8.3 Keyboard
- Every interaction must be keyboard-reachable
- Modals trap focus until dismissed
- Dropdowns close on Escape
- The AI bar opens with `⌘ /` (or `Ctrl /`) from anywhere

### 8.4 Screen readers
- Every icon-only button has `aria-label`
- Status dots have an accompanying `<span class="sr-only">` describing the status
- Loading states announce with `aria-live="polite"`
- The agent's streaming state announces "AlphaCon is responding" once at the start

### 8.5 Motion
- Respect `prefers-reduced-motion`: motion-streaming uses an instant reveal, motion-* tokens collapse to 0ms
- No autoplay video or audio

### 8.6 Form fields
- Labels are always visible (no placeholder-as-label)
- Required fields marked with `*` and announced
- Errors associate with the field via `aria-describedby`
- Error text is always specific to what's wrong

---

## 9. Don't list

Patterns explicitly forbidden. If a design or PR introduces one of these, push back — these aren't suggestions, they're rules.

**Visual**
- ❌ Pure black (`#000`) anywhere — use `text` or `graphite`
- ❌ Pure white (`#fff`) for backgrounds — use `surface`
- ❌ Gradients (except the optional `graphite → graphite-2` on the AI bar)
- ❌ Glassmorphism, neumorphism, skeuomorphism
- ❌ Shadows on resting-state cards (borders only)
- ❌ More than one shadow stacked on an element
- ❌ Animated illustrations, Lottie files, particle effects in MVP
- ❌ Saturated/bright versions of any colour
- ❌ Custom illustrated icons (use Lucide only)
- ❌ Icon fonts other than Lucide
- ❌ Multiple type weights beyond 400, 500, 600
- ❌ Type sizes outside the scale
- ❌ Spacing values outside the scale
- ❌ `rounded-full` on anything that isn't a tag/badge
- ❌ Radius greater than 14px

**Components**
- ❌ Buttons more than one line tall
- ❌ More than 2 primary buttons on a screen
- ❌ Tags as buttons (use a button)
- ❌ Tags larger than 11px
- ❌ Stat cards with icons
- ❌ More than 4 stat cards in a row
- ❌ Stat numbers below 24px
- ❌ Alert cards without a meta line
- ❌ Alert cards with more than 3 actions
- ❌ Property cards with images at MVP
- ❌ Chat bubbles (use the row format)
- ❌ Avatars in conversation rows
- ❌ AI bars with light backgrounds
- ❌ AI bars without chip suggestions
- ❌ Sidebars wider than 240px

**Copy**
- ❌ Exclamation marks
- ❌ Emojis in production UI
- ❌ Title Case
- ❌ "Click here" or generic CTAs
- ❌ "Oops!", "Uh oh!", "Something went wrong"
- ❌ Welcome banners or onboarding tutorials in MVP
- ❌ Empty-state copy that scolds ("You haven't added anything yet")

**Behaviour**
- ❌ Auto-playing video or audio
- ❌ Toasts that disappear after 3s with critical info (use confirm dialogs instead)
- ❌ Dismissable error banners that disappear on first scroll
- ❌ Modals that open without user action
- ❌ Cookies or trackers without a clear opt-in
- ❌ Forced sign-up walls on marketing pages

**Layout**
- ❌ Centered text in dense data screens (always left-align)
- ❌ Vertical text (rotation)
- ❌ Sidebars that disappear on collapse without trace
- ❌ Multi-row sticky headers
- ❌ Horizontal scrolling on the main content area (tables can scroll internally)

---

## Versioning

- **v1.0** *(this document)* — Foundational system calibrated to the Prototype C parchment direction
- v1.1 will add: more component variants as they emerge, agent persona-specific layout examples
- v2.0 only when something structural changes — e.g., palette refresh, typography change, brand evolution

When you change this document, update `prompts/claude_design.md` to match. The two documents are derived from each other — the design system is the source of truth, the prompt is the cached summary for Claude Design sessions.