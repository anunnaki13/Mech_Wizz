---
phase: 07-cost-vendor-proposal-engine
status: complete
mapped_at: 2026-05-16T15:08:00+07:00
---

# Phase 7 Pattern Map

## Backend Patterns

| New file or behavior | Closest analog | Pattern to reuse |
|----------------------|----------------|------------------|
| `backend/app/models/pre_feed_cost.py` | `pre_feed_package.py`, `financial_assumption.py` | UUID string PK, nullable optional fields, timestamps, SQLAlchemy typed mappings |
| `backend/alembic/versions/0009_phase7_cost_vendor.py` | `0008_phase6_prefeed_packages.py` | SQLite-compatible create tables, indexes, downgrade order |
| `backend/app/schemas/pre_feed_cost.py` | `pre_feed.py`, `financial_assumption.py` | Pydantic create/update/read schemas with `ConfigDict(from_attributes=True)` |
| `backend/app/services/prefeed_costs.py` | `prefeed.py`, `data_quality.py`, `scenarios.py` | Validation helpers, deterministic summaries/gaps, DB session service layer |
| `backend/app/routers/prefeed_costs.py` | `prefeed.py`, `documents.py`, `settings.py` | Dedicated router under `/prefeed`, HTTPException translation |
| `backend/tests/test_prefeed_costs.py` | `test_prefeed.py`, `test_data_quality_settings.py` | In-memory SQLite TestClient tests and direct DB assertions |

## Frontend Patterns

| New file or behavior | Closest analog | Pattern to reuse |
|----------------------|----------------|------------------|
| `frontend/types/prefeed-cost.ts` | `prefeed.ts`, `settings.ts` | Snake_case API types with local unions |
| `frontend/lib/api.ts` helpers | Existing Pre-FEED helpers | Typed `apiFetch` wrappers and query builders |
| `frontend/components/prefeed/CostVendorWorkspace.tsx` | `PreFeedWorkspace.tsx`, `SettingsWorkspace.tsx`, `DocumentWorkspace.tsx` | Client component with load state, forms, tables, backend warning display |
| `frontend/components/prefeed/PreFeedWorkspace.tsx` integration | Current package selector state | Pass selected package/scenario IDs into child workspace |
| CSS classes | Existing `.prefeed-*`, `.settings-*`, `.data-table` | Compact operational panels, table overflow, one-column mobile collapse |

## Existing Constraints To Preserve

- Backend is numeric and audit authority.
- Frontend must not recalculate totals, comparison scores, or gaps.
- Active selection must not overwrite scenario simulation history.
- Documents remain owned by document layer.
- Package records remain the root Pre-FEED audit parent.

## Suggested File Ownership By Plan

### 07-01 Cost Data And Aggregation

- `backend/alembic/versions/0009_phase7_cost_vendor.py`
- `backend/app/models/pre_feed_cost.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/pre_feed_cost.py`
- `backend/app/services/prefeed_costs.py`
- `backend/app/routers/prefeed_costs.py`
- `backend/app/main.py`
- `backend/tests/test_prefeed_costs.py`

### 07-02 Vendor Proposal, Comparison, Active Basis

- `backend/app/models/pre_feed_cost.py`
- `backend/app/schemas/pre_feed_cost.py`
- `backend/app/services/prefeed_costs.py`
- `backend/app/routers/prefeed_costs.py`
- `backend/tests/test_prefeed_costs.py`

### 07-03 Frontend Cost/Vendor Workspace

- `frontend/types/prefeed-cost.ts`
- `frontend/lib/api.ts`
- `frontend/components/prefeed/CostVendorWorkspace.tsx`
- `frontend/components/prefeed/PreFeedWorkspace.tsx`
- `frontend/app/globals.css`
- `README.md`
- `.planning/phases/07-cost-vendor-proposal-engine/07-03-SUMMARY.md`
- `.planning/phases/07-cost-vendor-proposal-engine/07-VERIFICATION.md`
- `.planning/phases/07-cost-vendor-proposal-engine/07-REVIEW.md`

## Verification Commands

- `cd backend && pytest -q tests/test_prefeed_costs.py`
- `cd backend && pytest -q`
- `cd frontend && npm run build`
- `rm -f /tmp/mechwiz_phase7_full.db && cd backend && DATABASE_URL=sqlite:////tmp/mechwiz_phase7_full.db .venv/bin/alembic upgrade head`
- `rg -n "PreFeedCostItem|VendorProposal|CostVendorWorkspace|active-cost-basis" backend frontend`
