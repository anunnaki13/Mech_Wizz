# Phase 9 Patterns

## Closest Backend Analogs

- `backend/app/models/pre_feed_cost.py` -> package-scoped tables with optional upstream references.
- `backend/app/models/pre_feed_market.py` -> package-scoped market/MRV records with confidence and data status.
- `backend/app/services/prefeed_costs.py` -> deterministic summaries, validation, and active basis handling.
- `backend/app/services/prefeed_market.py` -> readiness scoring, gap generation, and scenario-history preservation.
- `backend/app/routers/prefeed_costs.py` and `backend/app/routers/prefeed_market.py` -> thin FastAPI route pattern.
- `backend/tests/test_prefeed_costs.py` and `backend/tests/test_prefeed_market.py` -> in-memory SQLite tests with Tenayan seed package.

## Closest Frontend Analogs

- `frontend/components/prefeed/CostVendorWorkspace.tsx` -> compact package-scoped forms, tables, summaries, and gap panels.
- `frontend/components/prefeed/OfftakeMrvWorkspace.tsx` -> multi-panel operational workspace with backend-authored summaries.
- `frontend/components/prefeed/PreFeedWorkspace.tsx` -> package/scenario selection and child workspace composition.
- `frontend/lib/api.ts` -> typed API helper registration.
- `frontend/types/prefeed-cost.ts` and `frontend/types/prefeed-market.ts` -> typed contracts with snake_case backend fields.

## Constraints To Preserve

- Frontend must consume backend aggregate values and avoid duplicate calculation logic.
- New Phase 9 tables must be package-scoped and cascade when a package is deleted.
- Existing scenario results and assumptions are read-only context for this phase.
- LLM prompt context must be deterministic and bounded.
