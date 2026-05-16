---
phase: 06-pre-feed-package-foundation
status: complete
mapped_at: 2026-05-16T14:38:00+07:00
---

# Phase 6 Pattern Map

## Backend Patterns

| New file or behavior | Closest analog | Pattern to reuse |
|----------------------|----------------|------------------|
| `backend/app/models/pre_feed_package.py` | `backend/app/models/document.py`, `backend/app/models/business_scenario.py` | UUID string PK, FK strings, timestamps, nullable optional fields |
| `backend/app/schemas/pre_feed.py` | `backend/app/schemas/document.py`, `backend/app/schemas/application_setting.py` | Pydantic create/update/read schemas, `model_config = ConfigDict(from_attributes=True)` |
| `backend/app/routers/prefeed.py` | `backend/app/routers/documents.py`, `backend/app/routers/settings.py`, `backend/app/routers/scenarios.py` | Dedicated `APIRouter`, dependency-injected DB session, HTTPException for 404/validation |
| `backend/app/services/prefeed.py` | `backend/app/services/data_quality.py`, `backend/app/services/settings.py` | Thin service layer for deterministic summaries/gaps |
| `backend/tests/test_prefeed.py` | `backend/tests/test_documents.py`, `backend/tests/test_data_quality_settings.py` | TestClient API tests plus direct DB assertions |
| Alembic migration `0008_phase6_prefeed_packages.py` | `0007_phase5_llm_documents.py`, `0006_phase4_quality_settings.py` | Create tables and indexes with SQLite-compatible DDL |

## Frontend Patterns

| New file or behavior | Closest analog | Pattern to reuse |
|----------------------|----------------|------------------|
| `frontend/types/prefeed.ts` | `frontend/types/document.ts`, `frontend/types/settings.ts` | TypeScript API payload/read types matching backend snake_case |
| `frontend/components/prefeed/PreFeedWorkspace.tsx` | `DocumentWorkspace.tsx`, `SettingsWorkspace.tsx`, `ScenarioWorkspace.tsx` | Client component with load state, selectors, save handlers, table/detail panels |
| `frontend/app/prefeed/page.tsx` | `frontend/app/documents/page.tsx`, `frontend/app/settings/page.tsx` | `dynamic = "force-dynamic"` page wrapper inside `AppShell` |
| `frontend/lib/api.ts` helpers | Existing document/settings helpers | Typed helper functions around `apiFetch`; preserve FormData behavior |
| CSS classes | `.document-workspace`, `.settings-workspace`, `.investor-controls`, `.data-table` | Sibling panels, compact grids, status chips, notices, responsive collapse |
| Navigation | `frontend/components/layout/AppShell.tsx` | Add `{ label: "Pre-FEED", href: "/prefeed" }` near Investor/Documents |

## Existing Constraints To Preserve

- Frontend does not recalculate technical or financial outputs.
- Backend is numeric and audit authority.
- Missing data appears as explicit gaps/warnings.
- LLM is not used in Phase 6 package gap calculation.
- Uploaded document records remain owned by the document layer.
- Package changes must not overwrite prior scenario results.

## Suggested File Ownership By Plan

### 06-01 Backend Data Foundation

- `backend/alembic/versions/0008_phase6_prefeed_packages.py`
- `backend/app/models/pre_feed_package.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/pre_feed.py`

### 06-02 Backend API And Gap Service

- `backend/app/services/prefeed.py`
- `backend/app/routers/prefeed.py`
- `backend/app/main.py`
- `backend/tests/test_prefeed.py`

### 06-03 Frontend Workspace

- `frontend/types/prefeed.ts`
- `frontend/lib/api.ts`
- `frontend/app/prefeed/page.tsx`
- `frontend/components/prefeed/PreFeedWorkspace.tsx`
- `frontend/components/layout/AppShell.tsx`
- `frontend/app/globals.css`
- `README.md`

## Verification Commands

- `cd backend && pytest -q tests/test_prefeed.py`
- `cd backend && pytest -q`
- `cd frontend && npm run build`
- `rm -f /tmp/mechwiz_phase6_full.db && cd backend && DATABASE_URL=sqlite:////tmp/mechwiz_phase6_full.db .venv/bin/alembic upgrade head`
- `rg -n "PreFeedPackage|pre_feed_packages|PreFeedWorkspace|/api/prefeed" backend frontend`
