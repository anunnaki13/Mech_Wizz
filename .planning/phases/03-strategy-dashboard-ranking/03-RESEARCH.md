# Phase 3 Research: Strategy Dashboard & Ranking

## Current Codebase Findings

- Backend uses FastAPI, SQLAlchemy 2.x ORM, Alembic migrations, and pytest with SQLite `StaticPool`.
- Phase 2 added:
  - `BusinessScenario`
  - `FinancialAssumption`
  - `ScenarioResult`
  - pure calculation services under `backend/app/services/calculations/`
  - scenario simulation endpoint and frontend result display.
- Frontend uses Next.js app router, global CSS, `frontend/lib/api.ts`, and client components for interactive workspaces.
- Current plant seed lacks coordinates in existing DB, but the addendum provides Tenayan coordinates: longitude `101.5567`, latitude `0.5123`.

## Backend Scoring Approach

Add `UnitScoringResult` as the persisted `DATA-09` record:

- `plant_id`
- `scenario_id`
- `scenario_result_id`
- `opportunity_score`
- `readiness_score`
- `confidence_score`
- `composite_score`
- component scores
- `economic_return_score`
- `heatmap_weight`
- `data_gap_count`
- `rank_position`
- `recommended_scheme`
- `key_bottleneck`
- `scoring_version`

Use latest `ScenarioResult` for each scenario. If a scenario has no result yet, scoring endpoint can either skip it or return low/no-calculation metadata. The plan should require tests for both calculated and missing-data paths.

## Score Formula Notes

Opportunity:

```text
0.30 * co2_availability_score
+ 0.20 * methanol_potential_score
+ 0.15 * market_access_score
+ 0.10 * land_availability_score
+ 0.10 * utility_advantage_score
+ 0.05 * carbon_credit_potential_score
+ 0.10 * strategic_value_score
```

Readiness:

```text
0.20 * data_completeness_score
+ 0.20 * emission_data_quality_score
+ 0.15 * land_readiness_score
+ 0.15 * utility_readiness_score
+ 0.15 * h2_strategy_clarity_score
+ 0.15 * permit_logistic_readiness_score
```

Confidence:

| Status | Score |
|---|---:|
| actual | 1.00 |
| estimated | 0.70 |
| benchmark | 0.55 |
| user_assumption | 0.50 |
| partner_supplied | 0.60 |
| unknown | 0.00 |

Composite:

```text
0.45 * opportunity_score + 0.35 * readiness_score + 0.20 * confidence_score
```

Heatmap weight:

- Must include opportunity, readiness, economic return, and confidence.
- Recommended MVP weights: opportunity 35%, readiness 25%, economic return 25%, confidence 15%.

## API Approach

Add routers:

- `POST /api/scoring/recalculate`
- `GET /api/scoring/unit-ranking`
- `GET /api/map/unit-opportunity`
- `GET /api/units/{plant_id}/profile`

Use query params:

- `scenario_id`
- `scheme`
- `region`
- `fuel_type`
- `confidence`
- `opportunity_level`

Use GeoJSON `FeatureCollection` for `/api/map/unit-opportunity`.

## Frontend Map Approach

Use MapLibre GL JS in a client component.

Recommended page structure:

- `frontend/app/dashboard/map/page.tsx`
- `frontend/components/dashboard/MapDashboard.tsx`
- `OpportunityMap.tsx`
- `MapFilters.tsx`
- `RankingTable.tsx`
- `ScoreBreakdownPanel.tsx`
- `SensitivityPanel.tsx` in plan 03-03.

The UI should be operational and dense:

- KPI strip at top.
- Map and ranking table in the main work area.
- Right-side selected unit profile.
- Filters in a compact toolbar.

## Sensitivity Approach

Add `SensitivityResult` persistence tied to `plant_id`, `scenario_id`, and optionally `scenario_result_id`.

Variables:

- `h2_price`
- `electricity_price`
- `methanol_price`
- `capex`
- `capture_rate`
- `plant_availability`
- `carbon_credit_price`
- `exchange_rate`

For MVP:

- Calculate low/high output by perturbing a single variable at a time.
- Store low/high IRR, NPV, LCOM, and impact score.
- If CAPEX or other financial assumptions are missing, persist null output fields with missing-input warning metadata.
- Use HTML/CSS tornado bars rather than adding a chart library.

## Verification Strategy

Backend:

- Unit tests for score formulas and confidence mapping.
- API tests for recalculation, ranking, GeoJSON, profile.
- Sensitivity tests for complete assumptions and missing financial inputs.

Frontend:

- `npm run build`.
- Static acceptance markers for `MapLibre`, `heatmap`, `Ranking`, `Composite Score`, `Sensitivity`.

Full:

- `docker compose config`
- `cd backend && pytest -q`
- `cd frontend && npm run build`
- temp SQLite Alembic upgrade.

## Risks

- Map rendering can fail if external tile styles are unavailable. Mitigation: use a stable MapLibre style configuration and show marker/ranking data even if basemap loading fails.
- Tenayan coordinates are required for the first usable map. Mitigation: update seed with addendum coordinates.
- CAPEX nulls can make IRR/NPV/LCOM unavailable. Mitigation: surface null values and missing-input labels, do not invent final CAPEX.
