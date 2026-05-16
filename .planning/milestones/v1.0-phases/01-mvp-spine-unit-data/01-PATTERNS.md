# Phase 1: MVP Spine & Unit Data - Pattern Map

**Mapped:** 2026-05-16
**Codebase status:** Greenfield application; no backend/frontend source files exist yet.

## Summary

There are no existing application components, services, schemas, or tests to reuse. Phase 1 establishes the first local patterns for all later phases.

## Closest Local Analogs

| Planned Area | Existing Analog | Guidance |
|--------------|-----------------|----------|
| Project scaffold | `docs/blueprint.md` §19 | Use the blueprint folder structure as the initial project shape. |
| Backend API | `docs/blueprint.md` §16.1-16.4 | Implement Phase 1 endpoints under `/api` for plants, emission tests, site readiness, and hydrogen strategy. |
| Database schema | `docs/blueprint.md` §9.1-9.4 | Implement plants, emission tests, site readiness, and hydrogen strategy tables first. |
| UI shell | `.planning/phases/01-mvp-spine-unit-data/01-UI-SPEC.md` | Use the UI-SPEC as the design contract. |
| Seed data | `docs/blueprint.md` §22 | Seed Tenayan without inventing missing fields. |

## Patterns To Establish

### Backend

- `backend/app/main.py` should include a FastAPI app and mount API routers with `prefix="/api"`.
- `backend/app/config.py` should read settings from environment variables, not hardcoded secrets.
- `backend/app/database.py` should centralize SQLAlchemy engine/session setup.
- `backend/app/models/` should own SQLAlchemy ORM models.
- `backend/app/schemas/` should own Pydantic request/response schemas.
- `backend/app/routers/` should own route definitions.
- `backend/app/services/` should own reusable business logic such as seed helpers.

### Frontend

- `frontend/app/` should use Next.js App Router route directories.
- `frontend/components/ui/` should contain shadcn-generated UI primitives.
- `frontend/components/layout/` should contain app shell/navigation.
- `frontend/components/units/` should contain unit list, unit profile, and Phase 1 forms.
- `frontend/lib/api.ts` should be the single API fetch wrapper.
- `frontend/types/` should contain TypeScript types matching API responses.

### Tests

- Backend tests should start with health, plants list/create, Tenayan seed idempotence, and enum validation.
- Frontend checks should include lint/build and targeted component/page tests only if the scaffold includes a test runner.

## File Ownership Boundaries

Plan 01 owns scaffold and cross-cutting project files:
- `docker-compose.yml`
- `.env.example`
- `README.md`
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `frontend/Dockerfile`
- `frontend/package.json`
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`
- `frontend/app/dashboard/page.tsx`

Plan 02 owns database, seed, and backend API files:
- `backend/alembic/`
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/app/routers/`
- `backend/app/services/`
- `backend/app/seed.py`
- `backend/tests/`

Plan 03 owns user-facing Phase 1 frontend feature files:
- `frontend/components/layout/`
- `frontend/components/units/`
- `frontend/components/ui/`
- `frontend/lib/api.ts`
- `frontend/types/`
- `frontend/app/units/`
- `frontend/app/dashboard/page.tsx`

## Risks For Executors

- Do not create conflicting duplicate definitions for `data_status` or `confidence_level`; centralize allowed values in backend schemas and mirror them explicitly in frontend types.
- Do not fabricate Phase 2+ metrics in the dashboard.
- Do not make a static frontend-only demo. `/dashboard` must call the API and load database-backed Tenayan data by the end of Phase 1.
- Do not rely on the workspace `.git` mount. Use `GIT_DIR=.git-real GIT_WORK_TREE=.` for git status/commit unless the environment is repaired.
