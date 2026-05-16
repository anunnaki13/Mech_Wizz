# Phase 3 Verification

## Verdict

PASS - Strategy Dashboard & Ranking is implemented and verified for the v1 MVP scope.

## Commands Run

| Check | Result |
|---|---|
| `docker compose config` | PASS |
| `cd backend && pytest -q` | PASS, 25 passed |
| `cd frontend && npm run build` | PASS |
| `DATABASE_URL=sqlite:////tmp/mechwiz_phase3_full.db .venv/bin/alembic upgrade head` | PASS, upgraded through `0005_phase3_sensitivity` |
| `rg -n "SensitivityResult\|run_sensitivity_analysis\|Dominant sensitivity driver\|MapDashboard" backend frontend` | PASS |
| Local API smoke for simulate, scoring, GeoJSON, profile, sensitivity, and `/dashboard/map` | PASS |

## Requirement Coverage

- DATA-09: `UnitScoringResult` persists ranking/scoring outputs.
- UNIT-07: Unit profile combines plant, scenario, result, scoring, confidence, and gap metadata.
- SCORE-01 through SCORE-07: Opportunity/readiness/confidence/composite/heatmap/ranking APIs implemented and tested.
- DASH-01 through DASH-07: `/dashboard/map` implements MapLibre heatmap, markers, filters, ranking, selected profile, score breakdown, and confidence/data-gap labels.
- SENS-01 through SENS-03: Sensitivity persistence, API, perturbation engine, and tornado UI implemented.

## Acceptance Evidence

- `POST /api/scoring/recalculate` creates scoring rows from latest `ScenarioResult`.
- `GET /api/scoring/unit-ranking` returns rank, scores, CO2, methanol, IRR, scheme, and bottleneck fields.
- `GET /api/map/unit-opportunity` returns GeoJSON with Tenayan coordinates `[101.5567, 0.5123]`.
- `GET /api/units/{plant_id}/profile` returns selected unit profile with score breakdown and data gaps.
- `/dashboard/map` renders the MapLibre dashboard route and builds successfully.
- `POST /api/sensitivity/run` persists one row per sensitivity variable and returns warning metadata for missing CAPEX.

## Notes

- Docker daemon was not used for `up`; `docker compose config` validated Compose syntax.
- The running Next dev server produced one transient dev manifest error after hot reload and then returned `/dashboard/map` 200 after recompilation. Production build passed.
- `npm install maplibre-gl` reported two moderate audit findings; no forced audit fix was applied.
