---
phase: 02-scenario-simulation-engine
plan: "01"
subsystem: database-api-ui
tags: [fastapi, sqlalchemy, alembic, nextjs, scenarios]
requires:
  - phase: 01-mvp-spine-unit-data
    provides: Plant identity, Tenayan seed data, FastAPI/Next.js shell, and Alembic baseline
provides:
  - BusinessScenario and FinancialAssumption persistence
  - Scenario and financial assumption REST APIs
  - Idempotent Tenayan WIZ Align Base Case seed
  - /scenarios management workbench
affects: [scenario-simulation, calculation-engine, frontend-workbench]
tech-stack:
  added: []
  patterns: [SQLAlchemy one-to-one assumption records, FastAPI upsert endpoint, Next.js client workbench]
key-files:
  created:
    - backend/app/models/business_scenario.py
    - backend/app/models/financial_assumption.py
    - backend/app/routers/scenarios.py
    - frontend/components/scenarios/ScenarioWorkspace.tsx
  modified:
    - backend/app/seed.py
    - backend/app/main.py
    - frontend/lib/api.ts
key-decisions:
  - "Use Phase 1 plants as the scenario parent; no plant_sites/plant_units split in Phase 2."
  - "Expose financial assumptions as one upsertable record per scenario."
  - "Keep Run Simulation disabled until plan 02-03 wires persisted results."
patterns-established:
  - "Business records keep data_status and confidence_level beside numeric assumptions."
  - "Frontend scenario forms submit snake_case payloads directly to the API boundary."
requirements-completed: [DATA-05, DATA-06, UNIT-05, UNIT-06]
duration: 12min
completed: 2026-05-16
---

# Phase 2 Plan 01: Scenario Management Summary

**Persistent WIZ business scenarios with editable financial assumptions and a working `/scenarios` management surface**

## Performance

- **Duration:** 12 min
- **Started:** 2026-05-16T11:31:21+07:00
- **Completed:** 2026-05-16T11:43:21+07:00
- **Tasks:** 3
- **Files modified:** 20

## Accomplishments

- Added `business_scenarios` and `financial_assumptions` models, schemas, migration, router, and API registration.
- Extended the Tenayan seed to create/update `WIZ Align Base Case` and benchmark financial assumptions without duplicates.
- Replaced the `/scenarios` placeholder with a plant selector, scenario CRUD workflow, and financial assumption editor.

## Task Commits

1. **Tasks 1-2: Scenario/financial backend and seed** - `96f94a4`
2. **Task 3: Scenario frontend workbench** - `d89aa04`

## Files Created/Modified

- `backend/alembic/versions/0002_phase2_scenarios.py` - Phase 2 scenario/assumption migration.
- `backend/app/models/business_scenario.py` - Business scenario ORM model.
- `backend/app/models/financial_assumption.py` - Financial assumption ORM model.
- `backend/app/routers/scenarios.py` - Scenario CRUD and financial assumption endpoints.
- `backend/app/seed.py` - Tenayan WIZ Align base scenario and financial assumption seed.
- `backend/tests/test_scenarios.py` - API and idempotent seed tests.
- `frontend/components/scenarios/ScenarioWorkspace.tsx` - `/scenarios` workbench orchestration.
- `frontend/components/scenarios/ScenarioForm.tsx` - Scenario create/edit form.
- `frontend/components/scenarios/FinancialAssumptionsForm.tsx` - Assumption editor form.
- `frontend/lib/api.ts` - Scenario and financial assumption client helpers.

## Decisions Made

- `PUT /api/scenarios/{scenario_id}/financial-assumptions` upserts the single Phase 2 assumption record for ergonomic UI saves.
- CAPEX fields remain nullable so early-stage scenarios can be stored without inventing vendor/FEED numbers.
- Scenario `capture_rate` and `process_efficiency` are persisted on the scenario for calculation reproducibility.

## Deviations from Plan

None - plan scope executed as written.

## Issues Encountered

- Alembic verification initially used the wrong virtualenv path. Re-ran successfully with `backend/.venv/bin/alembic`.

## Verification

- `cd backend && pytest -q tests/test_scenarios.py` - 3 passed.
- `cd backend && pytest -q` - 10 passed.
- `cd frontend && npm run build` - passed.
- `DATABASE_URL=sqlite:////tmp/mechwiz_phase2_plan01.db backend/.venv/bin/alembic upgrade head` - upgraded through `0002_phase2_scenarios`.
- `rg -n "BusinessScenario|FinancialAssumption|WIZ Align Base Case|ScenarioWorkspace" backend frontend` - expected matches found.

## User Setup Required

None.

## Next Phase Readiness

Plan 02-02 can now consume persisted scenario assumptions and implement deterministic calculation services without touching the scenario management UI.

---
*Phase: 02-scenario-simulation-engine*
*Completed: 2026-05-16*
