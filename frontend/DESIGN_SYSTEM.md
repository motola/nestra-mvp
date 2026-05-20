# Alphacon AI — Design System

Reference this file for every UI decision. No arbitrary colours or deviations.

---

## Colour Tokens

| Token                                      | Hex       | Usage                             |
| ------------------------------------------ | --------- | --------------------------------- |
| `--bg` / `bg-bg`                           | `#f4f1eb` | Warm cream — main page background |
| `--surface` / `bg-surface`                 | `#fbf9f4` | Card and panel background         |
| `--surface-2` / `bg-surface-2`             | `#efebe2` | Subtle section background         |
| `--text` / `text-text`                     | `#1a1814` | Primary text                      |
| `--text-2` / `text-text-2`                 | `#5a564e` | Secondary text                    |
| `--text-3` / `text-text-3`                 | `#a39d8e` | Placeholder, labels, muted        |
| `--graphite` / `bg-graphite`               | `#28241e` | Primary buttons, dark elements    |
| `--graphite-2` / `bg-graphite-2`           | `#3a3530` | Button hover state                |
| `--border` / `border-border`               | `#e0dbcf` | Default border                    |
| `--border-strong` / `border-border-strong` | `#cdc6b8` | Focused or prominent borders      |
| `--green` / `text-green`                   | `#2d6b2d` | Success, online, all clear        |
| `--green-bg` / `bg-green-bg`               | `#eef5ee` | Green tinted background           |
| `--amber` / `text-amber`                   | `#9a5e15` | Warning, needs attention          |
| `--amber-bg` / `bg-amber-bg`               | `#fbf2e3` | Amber tinted background           |
| `--red` / `text-red`                       | `#8b2020` | Critical, offline, error          |
| `--red-bg` / `bg-red-bg`                   | `#fdf0f0` | Red tinted background             |

---

## Typography

### Display — Instrument Serif

- Use for: page titles, property names, large headings
- Weight: 400 (regular and italic)
- Tailwind: `font-display`
- Example: `<h1 className="font-display text-3xl text-text">`

### Body — DM Sans

- Use for: all body text, labels, UI copy, buttons
- Weight: 300 (default body), 400 (emphasis), 500 (strong labels)
- Tailwind: `font-body`
- Example: `<p className="font-body font-light text-text-2">`

### Mono — DM Mono

- Use for: device IDs, readings, numbers, timestamps, badges
- Weight: 400 (default), 500 (emphasis)
- Tailwind: `font-mono`
- Example: `<span className="font-mono text-text-3 text-xs">`

---

## Component Patterns

### Cards

```
bg-surface border border-border rounded-xl p-6
Hover: border-border-strong
```

### Primary Button

```
bg-graphite hover:bg-graphite-2 text-surface
rounded-lg px-5 py-2.5 font-body font-normal text-sm
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

### Insight Card Severity Borders

```
info:     border-l-4 border-l-[#2d6b2d] bg-green-bg
warning:  border-l-4 border-l-amber      bg-amber-bg
critical: border-l-4 border-l-red        bg-red-bg
```

### Sidebar

```
Background: bg-surface
Right border: border-r border-border
Nav active: border-l-2 border-l-graphite text-text font-normal
Nav inactive: text-text-2 font-light hover:text-text
```

---

## Spacing

- Page padding: `p-6` or `p-8`
- Card padding: `p-6`
- Card gap in grids: `gap-4`
- Section gap: `space-y-6`
- Component internal gap: `gap-3` or `gap-4`

---

## Do Not Use

- Any `gray-*`, `blue-*`, `green-*` (Tailwind defaults) — use tokens above
- `box-shadow` — use borders
- Any font other than DM Sans, Instrument Serif, DM Mono
- Dark backgrounds except `bg-graphite` on buttons
