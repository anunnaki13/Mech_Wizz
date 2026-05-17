---
phase: 13
status: complete
created: 2026-05-17
completed: 2026-05-17
---

# Phase 13 Plan: Pilot Decision Dashboard

## Success Criteria

1. Backend exposes a deterministic pilot decision API derived from Top 3 shortlist and evidence workspace data.
2. API labels each candidate with evidence-adjusted decision score, gate status, blockers, and next actions.
3. Frontend exposes `/pilot-decision` with an executive recommendation, candidate comparison, blocker list, and action plan.
4. App navigation and evidence workspace link to the pilot decision dashboard.
5. Tests, frontend build, runtime smoke checks, GSD validation, commit, and push pass.

## Plan

### 13-01 Backend Pilot Decision Service

- Add pilot decision schemas, service, and router.
- Combine shortlist score and evidence readiness transparently.
- Penalize rejected evidence and high-priority open gaps without mutating shortlist records.
- Generate deterministic blocker and next-action lists.

### 13-02 Frontend Dashboard

- Add frontend types and API helper.
- Add `/pilot-decision` page and dashboard component.
- Link from navigation and evidence workspace.

### 13-03 Verification

- Add backend tests for default evidence gaps and verified evidence progression.
- Run full backend tests, frontend build, runtime smoke checks, GSD validation, diff check, and secret scan.
