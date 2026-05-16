---
phase: 07-cost-vendor-proposal-engine
plan: "02"
subsystem: prefeed-vendor-comparison
tags: [fastapi, vendor-proposals, comparison, active-cost-basis]
requires:
  - phase: 07-cost-vendor-proposal-engine
    plan: "01"
    provides: Cost item persistence and aggregation
provides:
  - Vendor proposal persistence
  - Deterministic proposal comparison
  - Vendor proposal gap detection
  - Active cost-basis selection records
affects: [phase-7-prefeed-ui, phase-8-offtake-mrv-readiness, phase-9-dashboard]
tech-stack:
  added: []
  patterns: [structured scope booleans, deterministic gaps, active selection snapshots]
key-files:
  created:
    - backend/app/models/pre_feed_cost.py
    - backend/app/schemas/pre_feed_cost.py
    - backend/app/services/prefeed_costs.py
    - backend/app/routers/prefeed_costs.py
    - backend/tests/test_prefeed_costs.py
  modified:
    - backend/app/main.py
    - backend/app/models/__init__.py
key-decisions:
  - "Vendor proposal scope coverage is stored as explicit booleans for deterministic comparison."
  - "Proposal gaps flag missing scope, commercial basis, validity, cost items, and low/unknown confidence."
  - "Active cost-basis selections create auditable snapshots and mark prior active selections inactive."
requirements-completed: [COST-03, VEND-01, VEND-02, VEND-03, VEND-04]
duration: 8min
completed: 2026-05-16
---

# Phase 7 Plan 02: Vendor Comparison And Active Basis Summary

Implemented vendor proposal comparison, proposal gaps, and active cost-basis selection.

## Performance

- **Duration:** 8 min
- **Started:** 2026-05-16T15:18:00+07:00
- **Completed:** 2026-05-16T15:26:00+07:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added `PreFeedVendorProposal` and `PreFeedCostBasisSelection` models in the Phase 7 migration/model file.
- Added vendor proposal CRUD endpoints under `/api/prefeed`.
- Added deterministic vendor comparison rows with totals, scope completeness, missing scopes, gaps, confidence, and validity.
- Added vendor proposal gap endpoint.
- Added active cost-basis get/select endpoints that preserve prior selection history and avoid scenario result mutation.
- Added targeted tests for proposal CRUD, comparison, gaps, active selection, prior inactive selections, and history preservation.

## Verification

- `cd backend && pytest -q tests/test_prefeed_costs.py` - passed, 2 tests.
- `DATABASE_URL=sqlite:////tmp/mechwiz_phase7_plan01.db .venv/bin/alembic upgrade head` - passed through migration 0009.
- `rg -n "VendorProposal|vendor-comparison|active-cost-basis|missing_scopes" backend` - expected matches found.

## Notes

- Phase 7 records whether MRV scope is present in a proposal; MRV calculations remain Phase 8.
- Ready for Plan 07-03 frontend cost/vendor workspace.

---
*Phase: 07-cost-vendor-proposal-engine*
*Completed: 2026-05-16*
