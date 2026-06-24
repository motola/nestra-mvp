# Alphacon AI — Frontend Rules for Claude Code

Before writing any frontend code, read `DESIGN_SYSTEM.md` in this folder.
Every component you build must use the design tokens defined there. The single
source of token values is `src/app/globals.css` (`@theme`).

Direction: **Stripe IA + Linear precision + a warm architectural brand** — a
premium property-operations command centre. Light warm-grey canvas, white
surfaces, one sans-serif (Inter), bronze as a brand accent only.

NEVER:

- Use dark page backgrounds (the app canvas is warm light-grey `bg-bg`; charcoal
  `bg-graphite` is for buttons and the AI surface only)
- Use arbitrary hex colours not in the design system
- Use Tailwind default colours (`blue-500`, `gray-900`, etc.)
- Use `box-shadow` for layout (use 1px borders; elevation only for overlays)
- Use any font other than Inter and DM Mono (serif is marketing-site only)

ALWAYS:

- Use CSS variable tokens from `DESIGN_SYSTEM.md`
- Use `font-display` (Inter) for page titles and headings
- Use `font-body` (Inter) weight 300 for body text
- Use `font-mono` (DM Mono) for numbers, readings, timestamps, IDs
- Use `bg-graphite` for primary buttons
- Use `border-border` for card borders
- Use `bg-surface` (white) for card backgrounds
- Use `bg-bg` (warm light-grey) for page backgrounds
- Use the bronze `accent` token sparingly — selected nav, chart highlights, brand moments

ORGANIZING RULE:

- **Tables** for operational data, **cards** for summaries, **charts** for
  trends, **AI** for explanations. Avoid a beige wash everywhere and a button in
  every card.

COMPONENT PATTERNS:

- Cards: `bg-surface border border-border rounded-xl p-6`, hover `border-border-strong`
- Buttons: `bg-graphite hover:bg-graphite-2 text-surface rounded-lg`
- Inputs: `bg-bg border border-border rounded-lg focus:border-border-strong`
- Status badges: `rounded-full font-mono`, colour pair from the design system
- Back links: `text-text-3`, small, arrow left
- Section headers: `font-body font-normal text-xs uppercase tracking-widest text-text-3`

This file must be read before every frontend code change.
