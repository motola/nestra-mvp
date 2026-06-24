# Alphacon AI — Design System

Reference this file for every UI decision. No arbitrary colours or deviations.

> This reflects the current direction: **Stripe IA + Linear precision + a warm
> architectural brand** — a premium property-operations command centre. Light
> warm-grey canvas, white surfaces, one sans-serif (Inter), bronze as a brand
> accent only. It supersedes the earlier cream/serif system. The single source
> of these values is `src/app/globals.css` (`@theme`); if they ever disagree,
> `globals.css` wins.

---

## The organizing rule

**Tables for operational data, cards for summaries, charts for trends, AI for
explanations.** Avoid a beige wash everywhere and avoid a button in every card.

---

## Colour Tokens

| Token                                            | Hex       | Usage                                                                        |
| ------------------------------------------------ | --------- | ---------------------------------------------------------------------------- |
| `--color-bg` / `bg-bg`                           | `#f5f4f2` | Warm light-grey — app canvas                                                 |
| `--color-surface` / `bg-surface`                 | `#ffffff` | White — card and panel background                                            |
| `--color-surface-2` / `bg-surface-2`             | `#f1f0ed` | Subtle section background                                                    |
| `--color-text` / `text-text`                     | `#1a1a17` | Primary text (near-black charcoal)                                           |
| `--color-text-2` / `text-text-2`                 | `#5b5a55` | Secondary text                                                               |
| `--color-text-3` / `text-text-3`                 | `#94938d` | Placeholder, labels, muted                                                   |
| `--color-graphite` / `bg-graphite`               | `#1f1d1a` | Primary buttons, AI surface                                                  |
| `--color-graphite-2` / `bg-graphite-2`           | `#34322e` | Button / graphite hover                                                      |
| `--color-border` / `border-border`               | `#e7e6e2` | Default 1px border                                                           |
| `--color-border-strong` / `border-border-strong` | `#d6d4cf` | Focused or prominent borders                                                 |
| `--color-accent` / `text-accent`                 | `#9a5e15` | **Bronze brand accent** — selected nav, chart highlights, brand moments only |
| `--color-accent-2` / `text-accent-2`             | `#b07a2e` | Accent hover / secondary accent                                              |
| `--color-green` / `text-green`                   | `#2d6b2d` | Success, online, all clear                                                   |
| `--color-green-bg` / `bg-green-bg`               | `#ecf4ec` | Green tint                                                                   |
| `--color-amber` / `text-amber`                   | `#9a5e15` | Warning, needs attention                                                     |
| `--color-amber-bg` / `bg-amber-bg`               | `#faf1e1` | Amber tint                                                                   |
| `--color-red` / `text-red`                       | `#b3261e` | Critical, offline, error                                                     |
| `--color-red-bg` / `bg-red-bg`                   | `#fcecea` | Red tint                                                                     |
| `--color-info` / `text-info`                     | `#44566b` | Informational (blue-grey)                                                    |
| `--color-info-bg` / `bg-info-bg`                 | `#eef1f4` | Info tint                                                                    |

Status colours and the bronze accent are used **sparingly** — most of the UI is
charcoal text on white over a warm-grey canvas.

---

## Typography

One sans-serif across the whole product (Inter). Serif is for the marketing site
only, never the app.

### Display — Inter

- Use for: page titles, headings, KPI numbers
- Tailwind: `font-display`
- Sizes: page title 28–32, KPI 28–36

### Body — Inter

- Use for: all body text, labels, UI copy, buttons
- Weight: 300 (body), 400 (emphasis), 500/600 (strong labels)
- Tailwind: `font-body` (e.g. `font-body font-light text-text-2`)
- Sizes: body 14, table 13–14, labels 11–12

### Mono — DM Mono

- Use for: device IDs, readings, numbers, timestamps, badges
- Tailwind: `font-mono`

---

## Component Patterns

### Cards

```
bg-surface border border-border rounded-xl p-6   (10–12px radius, not toy-like 16–24)
Hover: border-border-strong
```

### Primary Button

```
bg-graphite hover:bg-graphite-2 text-surface
rounded-lg px-5 py-2.5 font-body font-normal text-sm
```

Secondary: `bg-surface border border-border`. Tertiary: text only. Destructive:
`text-red`. Not a button in every card.

### Inputs

```
bg-bg border border-border rounded-lg px-3 py-2.5 text-sm text-text
placeholder:text-text-3 focus:outline-none focus:border-border-strong
```

### Status Badges

```
rounded-full px-2.5 py-0.5 text-xs font-mono

all_clear:        text-green   bg-green-bg  border border-green/20
needs_attention:  text-amber   bg-amber-bg  border border-amber/20
critical:         text-red     bg-red-bg    border border-red/20
```

### Section Headers

```
font-body font-normal text-xs uppercase tracking-widest text-text-3
```

### Back Links

```
text-sm text-text-3 hover:text-text-2 flex items-center gap-1.5
```

### Sidebar

```
Background: bg-surface
Right border: border-r border-border
Nav active: text-text font-normal, bronze accent marker
Nav inactive: text-text-2 font-light hover:text-text
```

---

## Spacing

8px grid. Page padding `p-6`/`p-8`; card padding `p-4`–`p-6`; grid gap `gap-3`/`gap-4`;
section gap `space-y-6`. Avoid excessive vertical space and huge headings.

---

## Do Not Use

- Any `gray-*`, `blue-*`, `green-*` Tailwind defaults — use the tokens above
- `box-shadow` for layout — use 1px borders (elevation only for overlays)
- Any font other than Inter and DM Mono (serif is marketing-site only)
- Dark page backgrounds — the app canvas is warm light-grey; charcoal is for
  buttons and the AI surface only
