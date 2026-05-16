# Phase 4 Research: Investor Case & Data Quality

## Current Codebase Findings

- Backend already persists core inputs and outputs:
  - `Plant`, `EmissionTest`, `SiteReadiness`, `HydrogenStrategy`
  - `BusinessScenario`, `FinancialAssumption`
  - `ScenarioResult`, `UnitScoringResult`, `SensitivityResult`
- Phase 3 profile and scoring services already derive data gaps and confidence labels for selected units.
- `/investor` and `/settings` are placeholders.
- Frontend uses App Router, client components for interactive workspaces, `frontend/lib/api.ts` for API helpers, and global CSS for the dark dashboard system.

## Investor Aggregation Approach

Add a backend service that builds a structured investor case:

- Selected plant and scenario.
- Latest simulation result.
- Latest scoring result.
- Latest sensitivity run results.
- Financial assumptions.
- Investor KPIs:
  - project IRR
  - NPV
  - LCOM
  - payback
  - e-methanol capacity
  - CO2 abatement / captured CO2
  - CAPEX structure
- Revenue mix:
  - methanol sales
  - carbon credits
  - asset/utility/service placeholder segments from stored assumptions where available
- Scenario comparison across Access / Align / Augment for same plant.
- Risk and mitigation list from gaps, sensitivity dominant driver, and missing financial inputs.
- Roadmap to scale and why-this-wins deterministic template facts.

The API should not invent missing CAPEX, IRR, NPV, LCOM, or payback. Use `None` and warning metadata.

## Data Quality Approach

Centralize data status and confidence validation with reusable constants:

- `DATA_STATUS_VALUES`
- `CONFIDENCE_LEVEL_VALUES`

Add a data quality service:

- Collect source records for a plant/scenario.
- Produce input status summary by module.
- Produce output confidence summary by module.
- Produce gap recommendations with impact and priority.

Persist gaps in Phase 4 plan 03 so Phase 5 LLM can consume them.

## Settings Approach

Use an `ApplicationSetting` model with:

- `key`
- `value` JSON
- `category`
- `data_status`
- `confidence_level`
- timestamps

Seed default assumptions and scoring weights:

- financial defaults: methanol price, H2 price, electricity price, carbon credit price, discount/tax rates, OPEX percent
- scoring weights: opportunity/readiness/confidence/composite/heatmap defaults

Settings API:

- `GET /api/settings`
- `GET /api/settings/{key}`
- `PUT /api/settings/{key}`

## Frontend Approach

Investor page:

- Scenario selector based on real plants/scenarios.
- KPI strip.
- Investment thesis flow.
- Revenue mix.
- Scenario comparison.
- Risk and mitigation list.
- Roadmap to scale.
- Why this project wins.
- Data quality/gap panel.

Settings page:

- Editable JSON/value forms for default assumptions and scoring weights.
- Clear labels for `data_status` and `confidence_level`.
- Save/refresh states.

## Verification Strategy

Backend:

- Tests for investor aggregation with complete and missing economics.
- Tests for data quality gap generation.
- Tests for settings CRUD and validation.

Frontend:

- `npm run build`.
- Marker search for investor/dashboard/settings labels.

Full:

- `docker compose config`
- `cd backend && pytest -q`
- `cd frontend && npm run build`
- temp SQLite Alembic upgrade.

## Risks

- CAPEX nulls are expected in seed data. Mitigation: expose null economics and urgent CAPEX gap recommendations.
- Scenario comparison may only have one scenario in seed data. Mitigation: show missing Access/Augment slots clearly.
- Settings can be over-designed. Mitigation: use JSON key/value MVP settings and validate known keys.
