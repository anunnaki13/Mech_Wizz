# Phase 3 Patterns: Strategy Dashboard & Ranking

## Backend Patterns

- Keep each ORM model in `backend/app/models/<resource>.py`.
- Import each model in `backend/app/models/__init__.py`.
- Use `String(36)` UUID-like primary keys for SQLite/PostgreSQL compatibility.
- Use Alembic migrations only for schema changes; do not mutate prior migrations.
- Put API schemas in `backend/app/schemas/`.
- Put routers in `backend/app/routers/` and include them in `backend/app/main.py`.
- Put scoring and sensitivity logic under `backend/app/services/`.
- Return explicit `None` for uncalculable financial outputs; do not fabricate CAPEX-driven values.

## Frontend Patterns

- Add TypeScript types under `frontend/types/`.
- Extend `frontend/lib/api.ts` with typed API helpers.
- Keep map and filter interactions in client components.
- Reuse existing CSS tokens/classes where possible.
- Add map-specific classes to `frontend/app/globals.css`.
- Keep the dashboard operational and information-dense; avoid hero/marketing layout.

## Naming

Backend:

- `UnitScoringResult`
- `SensitivityResult`
- `calculate_unit_scores`
- `build_unit_opportunity_geojson`
- `run_sensitivity_analysis`

Frontend:

- `MapDashboard`
- `OpportunityMap`
- `MapFilters`
- `RankingTable`
- `ScoreBreakdownPanel`
- `SensitivityPanel`

## Expected New Files

Backend:

- `backend/alembic/versions/0004_phase3_scoring.py`
- `backend/alembic/versions/0005_phase3_sensitivity.py`
- `backend/app/models/unit_scoring_result.py`
- `backend/app/models/sensitivity_result.py`
- `backend/app/schemas/scoring.py`
- `backend/app/schemas/sensitivity.py`
- `backend/app/routers/scoring.py`
- `backend/app/routers/map.py`
- `backend/app/routers/unit_profiles.py`
- `backend/app/routers/sensitivity.py`
- `backend/app/services/scoring.py`
- `backend/app/services/map_geojson.py`
- `backend/app/services/unit_profile.py`
- `backend/app/services/sensitivity.py`
- `backend/tests/test_scoring.py`
- `backend/tests/test_sensitivity.py`

Frontend:

- `frontend/app/dashboard/map/page.tsx`
- `frontend/components/dashboard/MapDashboard.tsx`
- `frontend/components/dashboard/OpportunityMap.tsx`
- `frontend/components/dashboard/MapFilters.tsx`
- `frontend/components/dashboard/RankingTable.tsx`
- `frontend/components/dashboard/ScoreBreakdownPanel.tsx`
- `frontend/components/dashboard/SensitivityPanel.tsx`
- `frontend/types/scoring.ts`
- `frontend/types/sensitivity.ts`

## API Contract Conventions

- Use `plant_id` in responses instead of addendum `site_id` for v1 compatibility.
- GeoJSON properties may include `site_id` as an alias, but it must equal `plant_id`.
- Always include `data_status`, `confidence_level`, or score confidence context in UI-facing records.
- Filter params should be optional and default to all/current records.
