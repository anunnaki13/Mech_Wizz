---
phase: 08-offtake-mrv-readiness
type: ui-spec
status: ready
created: 2026-05-16
---

# Phase 8 UI Spec

## Surface

Extend `/prefeed` with an `OfftakeMrvWorkspace` rendered for the selected package and scenario.

## Layout

- Keep the existing package selector and Phase 6/7 panels.
- Add one full-width Phase 8 section below cost/vendor.
- Use two-column desktop layout:
  - Left: price deck and offtake prospect entry/list.
  - Right: MRV assumption entry/list and readiness/gap panels.
- Collapse to one column below 900px using existing responsive CSS conventions.

## Controls

- Price deck form: deck name, active flag, methanol price, carbon credit price, electricity price, hydrogen price, exchange rate, escalation, status, confidence, notes.
- Offtake form: counterparty, product, target volume, term, pricing basis, price, status, supporting document, status/confidence, notes.
- MRV form: baseline emissions, captured accounting, pathway, electricity source, electricity emission factor, methodology, verification status, eligibility, eligibility basis, supporting document, status/confidence, notes.
- Summary cards: backend revenue, offtake readiness, carbon intensity, abatement, MRV readiness.
- Gap lists: backend-authored offtake and MRV gaps.

## Data Rules

- Frontend does not calculate revenue, readiness, carbon intensity, abatement, or gaps.
- Missing values are explicit, not hidden.
- Mixed or missing market assumptions are shown as backend warnings.
- Existing Phase 6/7 controls must remain usable.

## Accessibility And Responsiveness

- Use native labels for form fields.
- Use icon buttons only where the action is obvious and has `aria-label`/`title`.
- Keep stable grid dimensions and prevent table text overflow with existing `.table-wrap` behavior.

---
*UI contract: 2026-05-16*
