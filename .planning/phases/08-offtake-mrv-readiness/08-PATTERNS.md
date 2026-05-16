---
phase: 08-offtake-mrv-readiness
type: patterns
status: ready
created: 2026-05-16
---

# Phase 8 Patterns

## Backend

- New migration follows `backend/alembic/versions/0009_phase7_cost_vendor.py`.
- New models follow `backend/app/models/pre_feed_cost.py`.
- New schemas follow `backend/app/schemas/pre_feed_cost.py`.
- New services follow `backend/app/services/prefeed_costs.py`.
- New router follows `backend/app/routers/prefeed_costs.py`.
- Tests follow `backend/tests/test_prefeed_costs.py` with in-memory SQLite and `seed_tenayan`.

## Frontend

- New types follow `frontend/types/prefeed-cost.ts`.
- New API helpers append to `frontend/lib/api.ts`.
- New workspace follows `frontend/components/prefeed/CostVendorWorkspace.tsx`.
- Integration point is `frontend/components/prefeed/PreFeedWorkspace.tsx`.
- CSS extends `frontend/app/globals.css` with package-scoped class names.

---
*Pattern map: 2026-05-16*
