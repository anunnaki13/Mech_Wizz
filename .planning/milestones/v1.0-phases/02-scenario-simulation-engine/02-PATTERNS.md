# Phase 2 Patterns: Scenario Simulation Engine

## Backend Patterns to Follow

### Models

- Put each ORM model in `backend/app/models/<resource>.py`.
- Import models in `backend/app/models/__init__.py` so `Base.metadata` sees them.
- Use `String(36)` primary keys with `default=lambda: str(uuid.uuid4())`.
- Use `DateTime(timezone=True)` with `server_default=func.now()`.
- Use cascade foreign keys for resources owned by `plants` or `business_scenarios`.

### Schemas

- Put Pydantic schemas in `backend/app/schemas/<resource>.py`.
- Use `ConfigDict(from_attributes=True)` for read schemas.
- Reuse `DataStatus` and `ConfidenceLevel` from `backend/app/schemas/common.py`.
- Keep create/update/read classes aligned with existing Phase 1 style.

### Routers

- Put routers in `backend/app/routers/<resource>.py`.
- Include routers in `backend/app/main.py` under `/api`.
- Use `get_*_or_404` helpers inside routers.
- Catch `IntegrityError` and return `409`.
- Use `status.HTTP_201_CREATED` for create and `204` for delete.

### Tests

- Use SQLite `StaticPool` test fixture and override `get_db`.
- Use FastAPI `TestClient`.
- Keep test fixtures local per test file for now, matching existing Phase 1 tests.
- Test both service functions and API endpoints when calculation risk is high.

### Migrations

- Add `backend/alembic/versions/0002_phase2_scenarios.py`.
- Do not mutate `0001_phase1_schema.py`.
- Use string UUID columns for consistency with Phase 1.
- Test migration with a temporary SQLite `DATABASE_URL`.

## Frontend Patterns to Follow

- Add TypeScript types under `frontend/types/`.
- Extend `frontend/lib/api.ts` with typed helper functions.
- Use server components for page-level data loading where possible.
- Use client components for create/edit forms and run-simulation actions.
- Reuse existing classes from `frontend/app/globals.css`: `app-shell`, `card`, `grid`, `detail-list`, `chip`, `button`, `form-grid`, `notice`.
- Keep controls dense and operational; no landing/marketing page.

## Phase 2 New Files Expected

Backend:

- `backend/app/models/business_scenario.py`
- `backend/app/models/financial_assumption.py`
- `backend/app/models/scenario_result.py`
- `backend/app/schemas/business_scenario.py`
- `backend/app/schemas/financial_assumption.py`
- `backend/app/schemas/scenario_result.py`
- `backend/app/routers/scenarios.py`
- `backend/app/services/calculations/co2.py`
- `backend/app/services/calculations/methanol.py`
- `backend/app/services/calculations/hydrogen.py`
- `backend/app/services/calculations/financial.py`
- `backend/app/services/scenario_simulation.py`
- `backend/alembic/versions/0002_phase2_scenarios.py`
- `backend/tests/test_calculations.py`
- `backend/tests/test_scenarios.py`
- `backend/tests/test_simulation.py`

Frontend:

- `frontend/types/scenario.ts`
- `frontend/types/financial-assumption.ts`
- `frontend/types/scenario-result.ts`
- `frontend/components/scenarios/ScenarioWorkspace.tsx`
- `frontend/components/scenarios/ScenarioForm.tsx`
- `frontend/components/scenarios/FinancialAssumptionsForm.tsx`
- `frontend/components/scenarios/SimulationResultPanel.tsx`
- `frontend/app/scenarios/page.tsx`

## Naming Conventions

- API model names: `BusinessScenario`, `FinancialAssumption`, `ScenarioResult`.
- Frontend helper names: `getPlantScenarios`, `createScenario`, `updateScenario`, `getFinancialAssumption`, `saveFinancialAssumption`, `runScenarioSimulation`, `getScenarioResults`.
- Calculation service names should be explicit and unit-bearing, e.g. `calculate_co2_ton_year`, `calculate_h2_required_ton_year`.
