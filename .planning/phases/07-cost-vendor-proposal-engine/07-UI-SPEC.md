# Phase 7 UI Spec: Cost & Vendor Proposal Engine

**Date:** 2026-05-16T15:08:00+07:00  
**Status:** Ready for planning  
**Route:** `/prefeed`

## UI Contract

Phase 7 extends the existing Pre-FEED package workspace. The first screen remains operational, not a landing page. Users should keep plant/scenario/package context visible while adding cost items, vendor proposals, proposal comparison, and active cost-basis selection.

## Layout

- Keep the Phase 6 top control band: plant selector, scenario selector, package selector, selected package summary.
- Add a cost/vendor section below the package metadata and linked document panels.
- Use compact cards and tables consistent with existing `.prefeed-*`, `.data-table`, `.field`, `.button`, `.notice`, `.status-line`, `.chip`, and `.data-gap-row` patterns.
- Avoid adding a new top-level navigation item. `/prefeed` remains the workspace route.

## Required Views

### Cost Items

- Cost item form:
  - Cost type: CAPEX or OPEX.
  - CAPEX component or OPEX category.
  - Amount, currency, source label.
  - Contingency percent and escalation percent for CAPEX.
  - Unit basis and recurrence for OPEX.
  - Optional vendor proposal selector.
  - `data_status`, `confidence_level`, notes.
- Cost item table:
  - Type, component/category, amount/currency, source, confidence, linked proposal, updated timestamp.
  - Delete action for mistaken entries.
- Aggregate summary:
  - CAPEX totals by currency.
  - Annual OPEX totals by currency.
  - Scenario-ready USD patch fields when available.

### Vendor Proposals

- Proposal form:
  - Vendor name, proposal name.
  - Supporting document selector from existing documents.
  - Validity date.
  - Scope coverage checkboxes: capture package, electrolyzer, methanol plant, storage/port, grid power, land, MRV.
  - Commercial basis, delivery assumptions, exclusions, `data_status`, `confidence_level`, notes.
- Proposal table:
  - Vendor/proposal, validity, scope completeness, CAPEX/OPEX totals, confidence, supporting document.
  - Select proposal for editing.

### Comparison And Active Cost Basis

- Comparison panel:
  - One row per vendor proposal.
  - CAPEX/OPEX totals by currency.
  - Scope completeness percentage.
  - Missing scope list.
  - Gap count and confidence.
- Active cost-basis panel:
  - Select `blended_package` or `vendor_proposal`.
  - For vendor proposal, choose proposal.
  - Save selection for current scenario.
  - Show current active selection and snapshot totals.

### Warnings

- Display backend proposal gaps in the existing warning style.
- Do not generate warning text in frontend code.
- Show empty states explicitly: no package selected, no cost items, no vendor proposals, no active cost basis.

## Interaction Rules

- Save actions call backend APIs and then refresh backend aggregate/comparison data.
- Frontend must not recalculate CAPEX/OPEX totals, scope completeness, proposal ranking, or gaps.
- Active cost-basis selection is disabled until a scenario and package are selected.
- Existing Phase 6 package/document controls must keep working.

## Visual Constraints

- Dense, work-focused, dashboard-like layout.
- No hero section, marketing copy, gradient decoration, nested cards, or oversized display text.
- Buttons use lucide icons where applicable.
- Tables must keep stable dimensions and horizontal overflow where needed.
- Mobile collapses to one column without text overlap.

## Verification

- `cd frontend && npm run build`
- `/prefeed` route appears in build output.
- Browser smoke route: `curl -fsSI http://localhost:3000/prefeed`.
