---
phase: 04-investor-case-data-quality
plan: "01"
subsystem: investor-api
tags: [fastapi, aggregation, investor, data-quality]
requires:
  - phase: 03-strategy-dashboard-ranking
    provides: Scenario results, scoring results, sensitivity results, and profile gap metadata
provides:
  - Investor aggregate service
  - Investor case API
  - Investor API tests
affects: [phase-4-investor-ui, phase-4-settings-quality, phase-5-llm-insights]
tech-stack:
  added: []
  patterns: [backend aggregate read model, null-safe economics, deterministic investor template content]
key-files:
  created:
    - backend/app/schemas/investor.py
    - backend/app/services/investor_case.py
    - backend/app/routers/investor.py
    - backend/tests/test_investor.py
  modified:
    - backend/app/main.py
key-decisions:
  - "Investor dashboard data is assembled by backend service and returned as a single aggregate."
  - "Unavailable economics remain null and generate warnings rather than being fabricated."
  - "Investment thesis, risks, roadmap, and why-this-wins are deterministic template outputs, not LLM outputs."
patterns-established:
  - "Investor UI can consume one `GET /api/investor-case` payload instead of recomputing cross-module data."
  - "Data gaps are enriched with investor-facing recommendations in the backend."
requirements-completed: [INV-01, INV-02, INV-03, INV-04, QUAL-02, QUAL-05]
duration: 6min
completed: 2026-05-16
---

# Phase 4 Plan 01: Investor API Summary

**Implemented backend investor dashboard aggregation and API.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-16T12:50:43+07:00
- **Completed:** 2026-05-16T12:56:53+07:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added `build_investor_case` service to aggregate plant, scenario, latest simulation result, latest scoring result, latest sensitivity run, financial assumptions, KPIs, CAPEX structure, revenue mix, scenario comparison, thesis flow, risks, roadmap, why-this-wins, data gaps, confidence, and warnings.
- Added `GET /api/investor-case?plant_id=&scenario_id=`.
- Added tests for service aggregation, explicit plant/scenario API use, and default seeded plant/scenario behavior.

## Verification

- `cd backend && pytest -q tests/test_investor.py` - passed, 3 tests.
- `cd backend && pytest -q` - passed, 28 tests.
- `rg -n "build_investor_case|investor-case|Investment thesis" backend` - expected matches found.

## Notes

- Tenayan seed CAPEX remains null, so investor KPIs correctly return null IRR/NPV/LCOM/payback and CAPEX warnings.
- Phase 4 plan 02 can now replace `/investor` placeholder with a real dashboard using the aggregate API.

---
*Phase: 04-investor-case-data-quality*
*Completed: 2026-05-16*
