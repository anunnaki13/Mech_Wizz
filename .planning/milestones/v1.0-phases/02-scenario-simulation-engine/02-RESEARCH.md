# Phase 2 Research: Scenario Simulation Engine

## Objective

Implement deterministic scenario simulation on top of the Phase 1 unit input spine. The output must become a reliable source for Phase 3 map/scoring and Phase 4 investor views without letting frontend or LLM logic invent numbers.

## Current Codebase Findings

- Backend uses FastAPI, SQLAlchemy 2.x ORM, Pydantic schemas, Alembic migrations, and pytest with SQLite dependency overrides.
- IDs are UUID-like strings stored as `String(36)` for SQLite/PostgreSQL compatibility.
- API routers are included under `/api`.
- Existing nested resource pattern:
  - `/api/plants/{plant_id}/emission-tests`
  - `/api/plants/{plant_id}/site-readiness`
  - `/api/plants/{plant_id}/hydrogen-strategy`
- Frontend uses Next.js app router, server-side page loading through `frontend/lib/api.ts`, and client sections for forms.
- Phase 1 app already has `/scenarios` as a placeholder route.

## Data Model Approach

Add models:

- `BusinessScenario`
  - `plant_id`, `scenario_name`, `scheme`, ownership/capex responsibility fields, `revenue_model`, `capture_rate`, `process_efficiency`, `data_status`, `confidence_level`, timestamps.
- `FinancialAssumption`
  - `scenario_id` one-to-one, pricing fields, exchange rate, discount/tax rates, CAPEX fields, OPEX percentage, `data_status`, `confidence_level`, timestamp.
- `ScenarioResult`
  - `scenario_id`, technical outputs, financial outputs, missing input metadata, calculation version, `confidence_level`, timestamp.

Use Alembic migration `0002_phase2_scenarios.py`.

Reasoning:

- Keeps scenario state explicit and auditable.
- Avoids rewriting Phase 1 `plants` schema.
- Allows Phase 3 ranking/GeoJSON to consume persisted scenario results later.

## Calculation Services

Implement pure service functions under `backend/app/services/calculations/` or equivalent:

- `co2.py`
  - stack area
  - normalized gas flow
  - wet CO2 fraction
  - CO2 kg/s
  - CO2 tons/day/year
  - aggregate across emission tests
- `methanol.py`
  - captured/vented CO2
  - theoretical/actual methanol
- `hydrogen.py`
  - H2 required
  - electrolyzer MW
- `financial.py`
  - gross revenue
  - annualized CAPEX if CAPEX available
  - LCOM
  - NPV
  - IRR via local binary-search implementation or `numpy_financial` if dependency is intentionally added
  - payback

Prefer not adding `numpy_financial` unless necessary; binary-search IRR is sufficient for MVP and avoids dependency churn.

## Formula Decisions

Use blueprint formulas:

```text
A = pi * (D / 2)^2
Q_normal = velocity * A * (273.15 / (273.15 + temperature_c))
CO2_wet_fraction = (CO2_dry_percent / 100) * (1 - moisture_percent / 100)
CO2_kg_s = Q_normal * CO2_wet_fraction * 1.964
CO2_ton_day = CO2_kg_s * 86400 / 1000
CO2_ton_year = CO2_ton_day * operating_days_per_year
captured_CO2 = total_CO2 * capture_rate
methanol_actual_ton_year = captured_CO2 * 0.7273 * process_efficiency
h2_required_ton_year = methanol_actual_ton_year * 0.1875 / h2_utilization_factor
electrolyzer_mw = (h2_required_ton_year * 1000 / operating_days_per_year) / 480
```

Financial calculations require complete enough assumptions. If critical CAPEX/price fields are missing, technical outputs should still persist while financial outputs are null and low-confidence.

## API Approach

Add routers:

- `/api/plants/{plant_id}/scenarios`
  - list/create scenarios for plant
- `/api/scenarios/{scenario_id}`
  - read/update/delete scenario
- `/api/scenarios/{scenario_id}/financial-assumptions`
  - get/create/update one assumption record
- `/api/scenarios/{scenario_id}/simulate`
  - create persisted scenario result from current inputs
- `/api/scenarios/{scenario_id}/results`
  - list persisted results
- `/api/scenario-results/{result_id}`
  - read one persisted result

This keeps REST paths consistent with Phase 1 nested resources.

## Frontend Approach

Use `/scenarios` as the Phase 2 work surface:

- Load plants.
- Allow selecting a plant.
- Show scenario list for selected plant.
- Allow creating WIZ Access/Align/Augment scenario.
- Allow editing financial assumptions.
- Run simulation.
- Display latest persisted result in compact KPI/detail panels.

No map, ranking, sensitivity, investor summary, or LLM UI in this phase.

## Verification Strategy

Backend:

- Pure calculation tests for known simple values.
- API tests for scenario CRUD.
- API tests for financial assumptions create/update.
- Simulation endpoint test using Tenayan-like plant/emission data and complete assumptions.
- Simulation missing-input test proving explicit low-confidence/null financial handling.
- Seed idempotency test for Tenayan scenario/assumptions.

Frontend:

- `npm run build` type-checks `/scenarios`.
- Static acceptance markers for API helper names and visible output labels.

Full:

- `docker compose config`
- `cd backend && pytest -q`
- `cd frontend && npm run build`
- Alembic upgrade against SQLite temp DB.

## Risks

- Financial formulas can become misleading if CAPEX defaults are silently invented. Mitigation: require explicit complete assumptions for financial outputs or mark benchmark/low confidence.
- IRR can fail when cashflows do not cross zero. Mitigation: return `null` and explicit warning instead of forcing a value.
- Multiple emission tests need aggregation. Mitigation: sum CO2 ton/year per stack record after calculating each valid stack test.
- Phase 3 will need scores and heatmap output. Mitigation: persist enough scenario result fields now but defer scoring to Phase 3.
