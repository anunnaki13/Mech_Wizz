---
phase: 03-strategy-dashboard-ranking
plan: "01"
subsystem: backend-scoring-map-profile
tags: [fastapi, sqlalchemy, geojson, scoring, ranking]
requires:
  - phase: 02-scenario-simulation-engine
    provides: Persisted ScenarioResult records
provides:
  - UnitScoringResult persistence and migration
  - Opportunity, readiness, confidence, composite, and heatmap scoring service
  - Ranking API
  - GeoJSON map API
  - Selected unit profile API
affects: [phase-3-map-dashboard, phase-3-sensitivity, phase-4-data-quality]
tech-stack:
  added: []
  patterns: [backend numeric authority, persisted read models, GeoJSON response assembly]
key-files:
  created:
    - backend/alembic/versions/0004_phase3_scoring.py
    - backend/app/models/unit_scoring_result.py
    - backend/app/services/scoring.py
    - backend/app/routers/scoring.py
    - backend/app/routers/map.py
    - backend/app/routers/unit_profiles.py
    - backend/tests/test_scoring.py
  modified:
    - backend/app/main.py
    - backend/app/seed.py
    - backend/app/models/__init__.py
key-decisions:
  - "Scoring consumes latest persisted ScenarioResult records; no frontend score calculation is introduced."
  - "Phase 1 Plant remains the unit/site identity, with plant_id also exposed as site_id for map compatibility."
  - "Heatmap weight uses opportunity, readiness, economic return, and confidence per addendum."
  - "Tenayan seed coordinates use addendum latitude 0.5123 and longitude 101.5567."
patterns-established:
  - "Scoring formulas live in backend/app/services/scoring.py."
  - "Ranking rows are assembled once and reused by GeoJSON/profile-oriented APIs."
requirements-completed: [DATA-09, UNIT-07, SCORE-01, SCORE-02, SCORE-03, SCORE-04, SCORE-05, SCORE-06, SCORE-07]
duration: 16min
completed: 2026-05-16
---

# Phase 3 Plan 01: Backend Scoring Summary

**Implemented backend scoring, ranking, GeoJSON, and selected unit profile APIs.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-05-16T12:05:00+07:00
- **Completed:** 2026-05-16T12:21:04+07:00
- **Tasks:** 3
- **Files modified:** 16

## Accomplishments

- Added `UnitScoringResult` persistence and Alembic migration `0004_phase3_scoring`.
- Added backend scoring formulas for opportunity, readiness, confidence, composite, economic return, heatmap weight, data gaps, and bottleneck derivation.
- Added `POST /api/scoring/recalculate` and `GET /api/scoring/unit-ranking`.
- Added `GET /api/map/unit-opportunity` returning MapLibre-ready GeoJSON.
- Added `GET /api/units/{plant_id}/profile` combining plant, scenario, latest simulation, latest score, confidence labels, and data gaps.
- Updated Tenayan seed coordinates from the addendum.

## Verification

- `cd backend && pytest -q tests/test_scoring.py` - passed, 5 tests.
- `cd backend && pytest -q` - passed, 23 tests.
- `rg -n "UnitScoringResult|calculate_unit_scores|unit-opportunity|unit-ranking" backend` - expected matches found.
- `cd backend && DATABASE_URL=sqlite:////tmp/mechwiz_phase3_scoring.db .venv/bin/alembic upgrade head` - upgraded through `0004_phase3_scoring`.

## Notes

- CAPEX remains nullable from Phase 2. Scoring therefore surfaces missing CAPEX/data gaps and null financial economics rather than inventing IRR/NPV/LCOM.
- Full data gap persistence is still Phase 4; Phase 3 exposes derived profile gap metadata for map/detail panels.

## Next Plan Readiness

Plan `03-02` can consume the new ranking, GeoJSON, and profile APIs to build `/dashboard/map` with MapLibre.

---
*Phase: 03-strategy-dashboard-ranking*
*Completed: 2026-05-16*
