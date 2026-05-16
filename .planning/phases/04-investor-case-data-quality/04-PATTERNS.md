# Phase 4 Patterns: Investor Case & Data Quality

## Backend Patterns

- Keep ORM models in `backend/app/models/`.
- Add schema files under `backend/app/schemas/`.
- Add routers under `backend/app/routers/` and include in `backend/app/main.py`.
- Put aggregation/business logic in `backend/app/services/`.
- Preserve nulls for uncalculable economics.
- Avoid frontend or LLM calculation authority.

## Frontend Patterns

- Add types under `frontend/types/`.
- Extend `frontend/lib/api.ts` with typed helpers.
- Use AppShell and existing dark operational CSS.
- Keep `/investor` and `/settings` as real work screens, not marketing pages.
- Use compact panels, tables, chips, and bars; no nested decorative cards.

## Expected New Files

Backend:

- `backend/alembic/versions/0006_phase4_quality_settings.py`
- `backend/app/models/data_gap.py`
- `backend/app/models/application_setting.py`
- `backend/app/schemas/investor.py`
- `backend/app/schemas/data_quality.py`
- `backend/app/schemas/application_setting.py`
- `backend/app/routers/investor.py`
- `backend/app/routers/settings.py`
- `backend/app/services/investor_case.py`
- `backend/app/services/data_quality.py`
- `backend/app/services/settings.py`
- `backend/tests/test_investor.py`
- `backend/tests/test_data_quality_settings.py`

Frontend:

- `frontend/types/investor.ts`
- `frontend/types/settings.ts`
- `frontend/components/investor/InvestorDashboard.tsx`
- `frontend/components/settings/SettingsWorkspace.tsx`

## API Contract Conventions

- Use `plant_id` and `scenario_id` consistently.
- Return `warnings` and `data_gaps` arrays rather than hiding missing inputs.
- Use `None`/`null` for missing economics.
- Keep display-ready text deterministic and clearly labelled as template-derived.
