---
phase: 02-scenario-simulation-engine
plan: "03"
subsystem: simulation-api-ui
tags: [fastapi, sqlalchemy, nextjs, scenario-results]
requires:
  - phase: 02-scenario-simulation-engine
    provides: Scenario/financial assumptions and deterministic calculation services
provides:
  - ScenarioResult persistence and migration
  - Simulation orchestration service
  - Scenario simulation/result APIs
  - Frontend Run Simulation and latest-result display
affects: [phase-3-map-ranking, phase-4-investor-dashboard, phase-5-llm-insights]
tech-stack:
  added: []
  patterns: [persisted calculation outputs, assumption snapshots, null-safe result UI]
key-files:
  created:
    - backend/app/models/scenario_result.py
    - backend/app/services/scenario_simulation.py
    - frontend/components/scenarios/SimulationResultPanel.tsx
  modified:
    - backend/app/routers/scenarios.py
    - frontend/components/scenarios/ScenarioWorkspace.tsx
    - README.md
key-decisions:
  - "Persist each simulation run rather than recalculating in the frontend."
  - "Store missing input metadata and assumption snapshots with every ScenarioResult."
  - "Null financial outputs are displayed explicitly rather than hidden or fabricated."
patterns-established:
  - "Simulation services load ORM records, call pure calculation services, and persist read models."
  - "Frontend reads stored results and never recomputes numeric outputs."
requirements-completed: [CALC-10, UNIT-05, UNIT-06]
duration: 10min
completed: 2026-05-16
---

# Phase 2 Plan 03: Scenario Simulation Summary

**Persisted scenario simulations with backend-authored outputs and a frontend latest-result workflow**

## Performance

- **Duration:** 10 min
- **Started:** 2026-05-16T11:49:03+07:00
- **Completed:** 2026-05-16T11:58:56+07:00
- **Tasks:** 3
- **Files modified:** 17

## Accomplishments

- Added `ScenarioResult` model, schema, Alembic migration, and result read/list endpoints.
- Added `run_scenario_simulation` to load scenario, plant, emission tests, and financial assumptions, then persist deterministic outputs with missing-input metadata.
- Enabled `/scenarios` to run a simulation and show stored technical and financial result fields.
- Updated README with Phase 2 workflow and verification commands.

## Task Commits

1. **Task 1: Scenario result backend** - `1bb48eb`
2. **Task 2: Frontend result flow** - `f711a74`
3. **Task 3 fix: Invalid financial outputs return null** - `75bb074`

## Files Created/Modified

- `backend/alembic/versions/0003_phase2_scenario_results.py` - Scenario result migration.
- `backend/app/models/scenario_result.py` - Persisted result model.
- `backend/app/services/scenario_simulation.py` - Simulation orchestration service.
- `backend/app/routers/scenarios.py` - Simulate/results endpoints.
- `backend/tests/test_simulation.py` - Persisted simulation and missing financial input tests.
- `frontend/types/scenario-result.ts` - Scenario result type.
- `frontend/components/scenarios/SimulationResultPanel.tsx` - Result display.
- `frontend/components/scenarios/ScenarioWorkspace.tsx` - Run Simulation flow.
- `README.md` - Phase 2 workflow and endpoint notes.

## Decisions Made

- Scenario results keep `missing_inputs`, `assumption_snapshot`, `calculation_version`, and `confidence_level` for reproducible downstream use.
- `financial_cashflow.non_positive` is surfaced as result metadata and invalid IRR/payback return `None`.
- Final Phase 2 verification uses `docker compose config` because Docker daemon is not required for config validation.

## Deviations from Plan

### Auto-fixed Issues

**1. Invalid financial outputs should be null**
- **Found during:** Task 3 review
- **Issue:** Payback with non-positive cashflow raised `ValueError`.
- **Fix:** `calculate_project_irr` and `calculate_payback_years` now return `None` for invalid economics.
- **Files modified:** `backend/app/services/calculations/financial.py`, `backend/tests/test_calculations.py`
- **Verification:** `cd backend && pytest -q` passed.
- **Committed in:** `75bb074`

## Issues Encountered

- A repeated Next build failed once because `.next` cache was stale. Removing generated `.next` and rebuilding succeeded.

## Verification

- `docker compose config` - passed.
- `cd backend && pytest -q` - 18 passed.
- `cd frontend && npm run build` - passed after clearing stale `.next`.
- `DATABASE_URL=sqlite:////tmp/mechwiz_phase2_full.db backend/.venv/bin/alembic upgrade head` - upgraded through `0003_phase2_scenario_results`.
- `rg -n "runScenarioSimulation|ScenarioResult|Captured CO2|calculate_irr" backend frontend` - expected matches found.

## User Setup Required

None.

## Next Phase Readiness

Phase 3 can consume persisted scenario results for map/ranking/scoring without recalculating in the frontend. The key backend source is `ScenarioResult`; the key frontend source is the `/scenarios` latest result panel.

---
*Phase: 02-scenario-simulation-engine*
*Completed: 2026-05-16*
