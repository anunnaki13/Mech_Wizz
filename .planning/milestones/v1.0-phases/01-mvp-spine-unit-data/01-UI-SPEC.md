---
phase: 01
slug: mvp-spine-unit-data
status: approved
shadcn_initialized: false
preset: premium-enterprise-dashboard
created: 2026-05-16
---

# Phase 01 — UI Design Contract

> Visual and interaction contract for Phase 1 frontend work. This phase establishes the usable dashboard shell and unit data management foundation for MECH WIZ AI Digital Twin.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | shadcn/ui intended; initialize during frontend scaffold |
| Preset | premium-enterprise-dashboard |
| Component library | Radix primitives through shadcn/ui |
| Icon library | lucide-react |
| Font | Geist or Inter |

Phase 1 must use the actual application screen as the first experience. Do not build a landing page, marketing hero, or explanatory splash screen.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, compact metadata rows |
| sm | 8px | Button/icon spacing, form field internal gaps |
| md | 16px | Default component spacing, card padding |
| lg | 24px | Panel padding, sidebar section gaps |
| xl | 32px | Dashboard grid gaps, page-level horizontal padding |
| 2xl | 48px | Large vertical separation between main regions |
| 3xl | 64px | Rare page-level separation only |

Exceptions: none.

Layout constraints:
- Main app frame must fit common 16:9 desktop viewports without horizontal scrolling.
- Dashboard cards and panels must have stable dimensions via grid tracks, min/max widths, and fixed header/sidebar sizing.
- Mobile layout must collapse sidebar/navigation into a compact top or drawer pattern, with no overlapping KPI text.
- Do not nest cards inside cards. Use panels for major app regions and cards only for repeated items or KPI tiles.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 12px | 500 | 1.35 |
| Heading | 20px | 650 | 1.25 |
| Display | 32px | 700 | 1.1 |

Typography rules:
- Do not scale font size with viewport width.
- Letter spacing must be `0`; avoid negative tracking.
- Use uppercase sparingly for labels, route section tags, and technical status badges.
- KPI numbers may use Display size, but panel headings, form labels, and table headers must stay compact.
- Long plant names, stack names, and status labels must wrap cleanly or truncate with tooltip; they must not overflow cards or buttons.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#020817` | Page background and app shell |
| Secondary (30%) | `#071426`, `#0B1B33` | Sidebar, panels, cards, input surfaces |
| Accent (10%) | `#00E5FF`, `#00C2A8`, `#0EA5E9` | Active nav, focus rings, selected site, primary CTA, data highlights |
| Success | `#7CFF6B` | Healthy status, actual data, positive readiness |
| Warning | `#FFD84D`, `#FF9F1C` | Estimated/benchmark data, medium risk, attention states |
| Destructive | `#FF4D6D` | Delete actions, high-risk flags, destructive confirmation |
| Text Primary | `#F8FAFC` | Main text and KPI values |
| Text Secondary | `#94A3B8` | Metadata, helper text, disabled secondary text |

Accent reserved for: active navigation item, primary command button, focus state, selected Tenayan marker, KPI highlights, and key data status chips. Do not apply cyan/teal to every border or every piece of text.

Visual guardrails:
- Avoid one-note blue/cyan dominance by using neutral slate surfaces and semantic green/yellow/orange/red status colors.
- Avoid decorative gradient orbs, bokeh blobs, and marketing hero gradients.
- Card radius should be 8px or less unless a shadcn default is reused consistently.
- Borders should be subtle and functional: `#163B5C` or low-opacity slate/cyan only where they separate data regions.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | Add Unit |
| Secondary CTA | Add Emission Test |
| Empty state heading | No unit data yet |
| Empty state body | Add a power plant unit or run the Tenayan seed to start screening. |
| Error state | Data could not be loaded. Check the API connection and try again. |
| Destructive confirmation | Delete unit: This removes the unit and its linked Phase 1 input records. |

Copy rules:
- Use concise professional Indonesian for user-facing business copy where the screen is investor/management-facing.
- Developer-only or API/debug messages may stay in English.
- Do not include in-app text explaining keyboard shortcuts, design choices, or how the UI was built.
- Do not present Phase 2+ outputs as real values in Phase 1. If a later KPI is shown as a placeholder, label it as unavailable until simulation is implemented.

---

## Phase 1 Screen Contract

### App Frame

- Persistent app frame with product label `MECH WIZ AI Digital Twin`.
- Sidebar or compact navigation must expose: Dashboard, Units, Scenarios, Investor, Sensitivity, Documents, Settings.
- Phase 1 may disable later routes or show minimal placeholders, but `/dashboard` and unit/profile surfaces must be usable.
- Header should include environment/API status and selected site when available.

### `/dashboard`

Purpose: prove the app spine and seeded data are connected.

Required regions:
- Compact header with scenario selector placeholder and site context.
- KPI row using backend-loaded Tenayan/unit facts available in Phase 1: capacity, fuel type, owner, data status, confidence, and emission test count.
- Main panel showing unit/site summary for Tenayan.
- Secondary panel listing emission stack records.
- Insight placeholder that clearly says simulation insights are available after Scenario Simulation Engine is built.

Do not fake IRR, NPV, LCOM, scoring, heatmaps, or sensitivity numbers in Phase 1.

### `/units`

Purpose: manage plant/unit records.

Required behavior:
- Table or dense list with plant name, unit name, province/city, capacity, fuel type, status, data status, confidence.
- Add/edit flows for plant fields required by Phase 1.
- Empty state uses the copywriting contract above.
- Row action opens unit profile.

### `/units/:id`

Purpose: combine Phase 1 input records for one plant.

Required sections:
- Unit identity and location summary.
- Emission tests section with add/edit flow.
- Site readiness section with add/edit flow.
- Hydrogen strategy section with add/edit flow.
- Data status and confidence chips visible in each relevant section.

### Placeholder Routes

The routes `/scenarios`, `/investor`, `/sensitivity`, `/documents`, and `/settings` may exist as restrained placeholders in Phase 1. They must not claim unfinished capabilities are ready. Settings may include early static assumptions placeholders if the executor wants a future-proof shell, but editable assumptions are Phase 4 scope.

---

## Interaction Contract

- Use icon buttons with lucide icons for common actions: add, edit, delete, refresh, upload, settings, search/filter if present.
- Include accessible labels/tooltips for icon-only buttons.
- Use segmented controls or tabs when switching between unit profile sections.
- Use select controls for allowed enum-like fields: `data_status`, `confidence_level`, fuel type, status, H2 strategy, H2 cost case.
- Use numeric inputs for capacity, coordinates, stack diameter, gas velocity, temperature, percentages, and readiness values.
- Use confirmation modal for destructive actions.
- Use loading skeletons or compact loading rows for API calls; avoid layout shift.
- Use inline validation beside fields rather than only toast messages.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | button, card, input, select, dialog, table, tabs, badge, tooltip, skeleton | not required |
| third-party shadcn registries | none approved for Phase 1 | shadcn view + diff required before use |

Do not use third-party component blocks unless the implementation explicitly reviews the generated code and keeps only necessary parts.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-05-16
