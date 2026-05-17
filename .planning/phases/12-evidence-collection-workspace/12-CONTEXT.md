---
phase: 12
status: complete
created: 2026-05-17
milestone: v2.3
---

# Phase 12 Context: Evidence Collection Workspace

## Goal

Turn the Phase 11 Top 3 validation pack into an operational evidence collection workspace. The app should let PLN/site/vendor/port/offtake/MRV evidence be tracked against each Top 3 candidate, persist evidence status, and show whether the shortlist is becoming decision-ready.

## Inputs

- Phase 11 `build_top3_validation_pack` candidate and checklist output.
- Existing plant/scenario/scoring data for the curated PLTU target dataset.
- Existing document repository for optional evidence document linkage.

## Scope

- Persist validation evidence records by plant, scenario, category, and evidence key.
- Support status lifecycle: `missing`, `requested`, `received`, `verified`, `rejected`.
- Surface evidence readiness score and high-priority unresolved gaps.
- Add backend API and frontend page for managing evidence records.
- Link the workspace from navigation and validation pack UI.

## Out of Scope

- Automated document extraction validation.
- External workflow approvals or role-based access control.
- Re-ranking the shortlist based on human-approved evidence. Phase 12 only shows readiness and confidence rollup.

## Verification Target

- Backend tests cover workspace defaults, create/update persistence, and rollup.
- Full backend test suite passes.
- Frontend production build passes.
- Runtime smoke checks confirm `/api/evidence/workspace` and `/evidence` are reachable.
