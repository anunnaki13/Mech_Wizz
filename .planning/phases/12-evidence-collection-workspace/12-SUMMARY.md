---
phase: 12
status: complete
completed: 2026-05-17
---

# Phase 12 Summary: Evidence Collection Workspace

## Delivered

- Added `validation_evidence` persistence with plant/scenario/category/evidence-key uniqueness.
- Added `/api/evidence/workspace`, `/api/evidence/records`, and `/api/evidence/records/{id}`.
- Merged Phase 11 Top 3 checklist defaults with persisted evidence records.
- Added deterministic evidence readiness score, verified item count, status mix, and high-priority open gap rollups.
- Added `/evidence` UI with candidate evidence board, editable evidence form, status lifecycle controls, and readiness summary.
- Linked Evidence from app navigation and `/validation-pack`.

## Decisions

- Evidence status is tracked separately from shortlist ranking so validation readiness does not silently change screening results.
- Default checklist items start as `missing` until a user saves evidence, even when the source screening pack has benchmark/public basis.
- Readiness scoring is deterministic: `verified` = 1.0, `received` = 0.7, `requested` = 0.35, `missing`/`rejected` = 0.

## Verification

- `backend/.venv/bin/pytest backend/tests/test_validation_evidence.py -q` — 3 passed.
- `backend/.venv/bin/pytest -q` — 61 passed.
- `npm run build` — passed.
- `gsd-sdk query state.validate` — valid.
- Runtime smoke: `/api/evidence/workspace?scheme=align&limit=3` returned 3 candidates and 15 evidence items.
- Runtime smoke: `/evidence` rendered `Top 3 Evidence Collection`, `Candidate Evidence Board`, and `Evidence Record`.

## Runtime Notes

- The local SQLite runtime database already had phase 6-9 tables but an old Alembic stamp. The table was created via SQLAlchemy metadata and Alembic was stamped to `0012_phase12_validation_evidence` without dropping existing data.
