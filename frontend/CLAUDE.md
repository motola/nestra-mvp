# Alphacon AI — Frontend Rules for Claude Code

Before writing any frontend code, read DESIGN_SYSTEM.md in this folder.
Every component you build must use the design tokens defined there.

NEVER:

- Use dark backgrounds (the site is light/warm cream)
- Use arbitrary hex colours not in the design system
- Use Tailwind default colours (blue-500, gray-900 etc)
- Use box-shadow (use borders instead)
- Use any font other than DM Sans, Instrument Serif, DM Mono

ALWAYS:

- Use CSS variables from DESIGN_SYSTEM.md
- Use Instrument Serif for page titles and property names
- Use DM Sans weight 300 for body text
- Use DM Mono for numbers, readings, timestamps, IDs
- Use bg-graphite for primary buttons
- Use border-border for card borders
- Use bg-surface for card backgrounds
- Use bg-bg for page backgrounds

COMPONENT PATTERNS:

- Cards: bg-surface, border border-border, rounded-xl, p-6
- Buttons: bg-graphite text-surface rounded-lg
- Status badges: rounded-full, font-mono, colour pair from design system
- Back links: text-text-3, small, arrow left
- Section headers: font-body font-normal text-xs uppercase tracking-widest text-text-3

This file must be read before every frontend code change.
