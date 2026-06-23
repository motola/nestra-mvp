# Frontend Capabilities Report

**Last Updated:** June 23, 2026
**Status:** NEM-21 property detail pane complete
**Test Coverage:** 59 passing Vitest + component tests

---

## Executive Summary

The AlphaCon AI frontend is a Next.js 15 TypeScript application built with shadcn/ui components and Tailwind CSS. It provides a complete operator console with 11 authenticated screens plus 2 public pages. All core features are UI-complete with fixture-based test coverage.

**Architecture:** Server Components by default with Client Components for interactivity
**State Management:** TanStack Query for API calls, React Context for auth
**Forms:** react-hook-form + Zod validation
**Testing:** Vitest for unit/component tests, ready for Playwright e2e integration

---

## Public Pages

### Landing Page (`/`)
- Minimal marketing entry point
- Navigation to sign up / login
- Branding and project introduction

### Sign Up (`/auth/signup`)
- Email and password input with form validation
- Real-time feedback on password strength and email validity
- Links to login page
- Fixture-based testing for form state management

### Login (`/auth/login`)
- Email and password input
- JWT-based session management (persisted in cookies)
- Error handling for invalid credentials
- Fixture-based testing for auth flow

---

## Authenticated Pages (Dashboard)

All authenticated routes require active session; redirect to `/login` on auth failure.

### Overview (`/dashboard/overview`)
- **Purpose:** At-a-glance health and status summary
- **Components:**
  - PageHeader with title and action buttons
  - StatCards showing key metrics (properties online, devices active, stays occupied, automations running)
  - Property status grid (upcoming stays, occupancy, device availability)
  - System health indicators
- **Interactivity:** View toggles, filter chips
- **Test Coverage:** Page header render, stat cards render, metric display

### Portfolio (`/dashboard/portfolio`)
- **Purpose:** Multi-property and multi-portfolio workspace
- **Tabs:**
  - **Portfolios:** Nested portfolio/property hierarchy view
  - **All Properties:** Flat list view with filter options
- **Filters:** Critical, Attention, All Clear status badges
- **Layouts:** Card grid and data table (toggleable)
- **Components:**
  - PropertyCard with name, address, alert status
  - DataTable with sortable columns
  - Status tags (alert, warn, all clear)
- **Test Coverage:** Both tabs render, filtering works, layout toggle, property detail navigation

### Devices (`/dashboard/devices`)
- **Purpose:** Vendor device inventory and control interface
- **Columns:** Device name, property, vendor, status, last sync, battery
- **Filters:** Needs attention (offline), Unreachable (unreachable), All
- **Features:**
  - Device state display (on/off, brightness, temperature)
  - Status indicators (online, offline, low battery, syncing)
  - Vendor sync metadata card showing last sync timestamp
  - Device detail drawer (click to open)
- **Components:**
  - DataTable with custom cell renders
  - Device detail drawer with full device specs
- **Test Coverage:** Table render, filter logic, drawer open/close, status display

### Automations (`/dashboard/automations`)
- **Purpose:** Trigger automation management and AI-suggested automations
- **StatCards:** Active automations count, scheduled runs, manual triggers, disabled
- **Sections:**
  - **Agent Suggestions Panel:** AI-generated automation recommendations
    - Cards with trigger, action, frequency
    - Actions: Approve, Tweak, Dismiss
  - **Live Automations Table:** All active and paused automations
    - Toggle switch to enable/disable
    - Edit and delete actions
- **Filters:** Paused, Manual, All
- **Test Coverage:** Stat cards render, suggestions appear, table filters work, toggle state updates

### Integrations (`/dashboard/integrations`)
- **Purpose:** Vendor account management and webhook monitoring
- **Tabs:**
  - **Connected:** Active integrations (Govee, Lifx, etc.)
    - Reauth alert card for expired credentials
    - Vendor cards with account details and disconnect action
  - **Catalog:** Available vendor integrations
    - Vendor grid with category filters (Lighting, Climate, Security, etc.)
    - Connect buttons
  - **Webhooks:** Event delivery logs
    - Vendor, event type, payload, status
    - Retry actions for failed deliveries
  - **Errors:** Error event history
    - Timestamp, vendor, error message, resolution action
- **Test Coverage:** Tab switching, vendor card display, alert render, webhook/error tables

### Intelligence (`/dashboard/intelligence`)
- **Purpose:** AI agent chat workspace and quick actions
- **Features:**
  - **Chat Tabs:** Multiple concurrent conversations with seed examples
    - New Chat button to create blank conversation
    - Seed tab titles: "Control devices", "Check occupancy", "Schedule stay"
  - **Transcript:** Full chat history with user/assistant messages
  - **Input Bar:** Message composition with send action
  - **Quick Actions Tray:** One-click AI operations (emergency shutdown, occupancy report, etc.)
  - **Recent Activity Drawer:** Automation runs, device changes, and alerts in a timeline
- **Components:**
  - ChatMessage component for user/assistant rendering
  - MessageInput with button state
  - QuickActionTile for preset actions
  - ActivityTimeline in drawer
- **Test Coverage:** Tab creation, message sending, quick action selection, activity drawer, state clearing

### Team (`/dashboard/team`)
- **Purpose:** Organization member and permission management
- **Components:**
  - Members table with name, email, role, status
  - Role permission cards (Organization Admin, Portfolio Manager, Property Manager, Contractor)
  - Invite form to add new members
  - Revoke/edit actions on member rows
- **Features:**
  - Role description and permission breakdown
  - Member status badges (Active, Pending, Inactive)
  - Bulk permission matrix display
- **Test Coverage:** Member table render, role card display

### Settings (`/dashboard/settings`)
- **Purpose:** Organization, account, and system configuration
- **Tabs (7 total):**
  - **Organization:** Name, description, slug, subscription tier
  - **Billing:** Subscription plan, usage, invoice history
  - **Security:** Password change, session management, two-factor auth setup
  - **Notifications:** Email preferences, alert routing rules
  - **Integrations:** Connected vendor accounts (read-only view of Connected tab)
  - **Audit Log:** Immutable event history (who, what, when, why)
    - Sortable by date, filterable by action type and actor
    - Full event payloads in expandable rows
  - **Danger Zone:** Deactivate organization, purge all data
- **Test Coverage:** Tab navigation, form state, audit log table display

### Property Detail (`/dashboard/properties/[id]`)
- **Purpose:** Deep dive into a single property's configuration and status
- **Tabs (6 total):**
  - **Overview:** Property metadata, address, occupancy status, device count, stay schedule
  - **Devices:** Scoped device list filtered to this property only
  - **Automations:** Property-specific automation rules
  - **Team:** Assigned contractors and their permissions for this property
  - **Stays:** Tenant occupancy schedule with check-in/check-out dates
  - **Settings:** Property-specific config (access codes, smart lock pairing, guest wifi)
- **Features:**
  - Breadcrumb navigation back to portfolio
  - Property header with status and quick-action buttons
  - Tab persistence in URL
- **Test Coverage:** Tab rendering, detail data display (fixture-based)

---

## Shared/Reusable Components

### UI Components (shadcn/ui + custom)

#### Layout
- **Sidebar:** Collapsible navigation (240px → 64px)
  - Logo and branding
  - Main nav items (Overview, Portfolio, Devices, etc.)
  - User menu (profile, sign out)
  - Collapse/expand toggle
- **TopNav:** Secondary navigation bar
  - Breadcrumbs for context
  - Organization/Portfolio switcher
  - Quick search
  - Notification bell

#### Display Components
- **PageHeader:** Page title, description, primary action button(s)
- **StatCard:** Metric label, value, unit suffix, trend indicator
- **PropertyCard:** Property name, address, status badge, click handler
- **AlertCard:** Title, description, action buttons (e.g., for reauth alerts)
- **DataTable:** Generic table with headers, rows, click handlers, optional filters
- **Tabs:** Tab labels with optional count badges, onChange handler
- **Tag:** Status badges (ok/warn/alert variants) with optional dot indicator
- **Card:** Basic container (shadcn base)

#### Form Components
- **Button:** Primary, secondary, ghost, destructive variants
- **Input:** Text input with placeholder and validation error states
- **Form:** react-hook-form wrapper with Zod schema integration
- **Label:** Form field labels with required indicators

#### Interactive Components
- **AIBar:** Floating action bar for quick agent access (on intelligence page)
- **DeviceDetailDrawer:** Side panel with full device specs and control actions
- **ActivityDrawer:** Timeline panel for recent activity viewing

---

## Data & State Management

### API Client (`lib/api/client.ts`)
- Type-safe fetch wrapper
- Auto-includes JWT from cookie
- Response parsing with shared types
- Error handling and logging

### Auth Provider (`lib/auth/provider.tsx`)
- React Context for session state
- `useAuth()` hook for consuming components
- Automatic redirect on auth failure
- Session persistence via HTTPOnly cookie

### Fixtures (`lib/fixtures.ts`)
- Mock data for all screens
- Pre-built objects for testing
- Includes: users, organizations, properties, devices, automations, integrations, chat, team, settings, audit log

### API Hooks (`lib/api/hooks/use-auth.ts`)
- `useAuth()`: Current user and org context
- Pattern: Can be extended with TanStack Query hooks for real API data fetching

---

## Architecture & Patterns

### Page Structure
```
(auth)/
├── login/page.tsx
└── signup/page.tsx

(dashboard)/
├── layout.tsx          # Sidebar + TopNav
├── overview/page.tsx
├── portfolio/page.tsx
├── devices/page.tsx
├── automations/page.tsx
├── integrations/page.tsx
├── intelligence/page.tsx
├── team/page.tsx
├── settings/page.tsx
└── properties/[id]/page.tsx
```

### Component Hierarchy
- **Server Components** by default (all page.tsx files)
- **Client Components** for interactivity:
  - Layout components (sidebar, nav)
  - Screen components (e.g., `DevicesScreen`)
  - Interactive UI (tabs, buttons, drawers, tables)
  - Form components

### Styling
- **Tailwind CSS 4** exclusively
- **Design tokens** from `prompts/claude_design.md`:
  - Colors: Primary navy (#1A365D), accent green (#2F855A), warning amber (#DD6B20), danger red (#9B2C2C)
  - Typography: Inter font, 400/500/600 weights only
  - Spacing: 4px, 8px, 12px, 16px, 24px, 32px, 48px scale
  - Radius: 4px (badges), 6px (buttons/cards), 10px (modals)

### Form Handling
- **react-hook-form** for form state
- **Zod** for runtime validation
- **Type inference** from Zod schemas
- Patterns in signup and login pages

---

## Test Coverage

### Test Files (8 total)

| File | Tests | Coverage |
|------|-------|----------|
| demo.test.ts | 4 | Demo fixture data and helpers |
| portfolio-screen.test.tsx | 7 | Portfolio page tabs, filters, layout toggle |
| devices-screen.test.tsx | 8 | Device table, filters, drawer, status display |
| automations-screen.test.tsx | 8 | Stat cards, suggestions, table, filters |
| integrations-screen.test.tsx | 7 | Tabs, vendor cards, webhook/error tables, reauth alert |
| intelligence.test.tsx | 10 | Chat tabs, messages, quick actions, activity drawer |
| portfolio.test.tsx | 10 | PropertyCard, DataTable, Tabs components |
| overview.test.tsx | 5 | StatCard, Tag, AlertCard components |

**Total: 59 tests passing**

### Testing Patterns
- Mock fixture data instead of API calls
- Test rendering, state updates, and user interactions
- Use Vitest `describe`/`it` syntax
- Mock next/navigation for routing context
- Test both happy path and edge cases (e.g., filter interactions)

### Not Yet Covered
- End-to-end Playwright tests (ready to add)
- Real API integration tests (pending backend endpoint stabilization)
- Accessibility (a11y) tests
- Visual regression tests

---

## Ready-to-Build Features

The UI foundation is complete. These items can be built next:

### Backend Integration
1. Replace fixture data with real API calls via TanStack Query
2. Implement all CRUD endpoints for properties, devices, automations, etc.
3. Add WebSocket for real-time device state and chat updates

### Features Requiring Endpoint Wiring
- Device control (toggle, set brightness, etc.)
- Automation creation/edit/delete
- Integration connect/disconnect
- Chat message sending and streaming
- Team member invite and permission management
- Audit log queries

### UI Polish
- Loading states for all async operations
- Error boundaries and fallback pages
- Notification toasts for actions (created, updated, deleted)
- Confirmation modals for destructive actions
- Empty states for all tables and lists

---

## Dependencies & Setup

### Key Packages
- **next@15** — React framework
- **react-hook-form** — Form state
- **zod** — Schema validation
- **@tanstack/react-query** — Data fetching (installed, not yet wired)
- **tailwindcss@4** — Styling
- **shadcn/ui** — Component library

### Dev Dependencies
- **vitest** — Unit testing
- **@testing-library/react** — Component testing
- **@playwright/test** — E2E ready (not yet used)

### Local Development
```bash
make dev          # Start Next.js dev server (port 3000)
npm run test      # Run Vitest suite
npm run lint      # Run ESLint
npm run type-check # Run TypeScript compiler
```

---

## Known Limitations & Debt

1. **Fixtures Only:** All data is currently mocked. No real backend integration yet.
2. **No Real-Time Updates:** Changes don't persist or broadcast to other users.
3. **No E2E Tests:** Vitest tests exist but Playwright suite not yet created.
4. **Limited Error Handling:** Form errors and API errors partially handled.
5. **No Offline Support:** No service worker or offline queue.
6. **No Accessibility Audit:** WCAG compliance not yet verified.
7. **Mock Auth:** Session is mocked in fixtures; real JWT validation pending.

---

## Next Steps

1. **Merge NEM-21** and consolidate into main
2. **Create TanStack Query hooks** for API data fetching
3. **Wire endpoints** (start with property CRUD, then devices/automations)
4. **Add Playwright E2E tests** covering signup → property create → device list flow
5. **Error handling:** Add error boundaries, toast notifications, and retry logic
6. **Real-time:** Implement WebSocket for chat and device state updates

---

**Generated:** June 23, 2026
**Checked Against:** Commit d699b39 (NEM-21 formatting fix)
