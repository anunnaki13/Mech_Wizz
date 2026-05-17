---
phase: 12
status: complete
created: 2026-05-17
completed: 2026-05-17
---

# Phase 12 Plan: Evidence Collection Workspace

## Success Criteria

1. Backend stores validation evidence records for Top 3 candidates.
2. API exposes an evidence workspace that merges Phase 11 default checklist items with persisted evidence status.
3. UI exposes `/evidence` with summary KPIs, candidate-level evidence cards, editable evidence form, and status rollup.
4. Evidence workspace is discoverable from nav and validation pack.
5. Tests, frontend build, runtime smoke checks, GSD validation, commit, and push pass.

## Plan

### 12-01 Backend Evidence Model and API

- Add `ValidationEvidence` SQLAlchemy model and Alembic migration.
- Add schemas for evidence records, workspace candidates, and rollup summary.
- Add service to derive default evidence requirements from the Top 3 validation pack and merge persisted records.
- Add router endpoints for workspace load, create evidence, and update evidence.

### 12-02 Frontend Workspace

- Add frontend types and API helpers.
- Add `/evidence` client workspace with Top 3 candidate filter, status lifecycle controls, metadata fields, and evidence detail cards.
- Add navigation and validation-pack link.

### 12-03 Verification and Ship

- Add backend tests for default checklist, create/update, and readiness summary.
- Run full backend tests, frontend build, GSD validation, diff check, and secret scan.
- Restart local backend/frontend servers, smoke test, commit, and push to GitHub `main`.
