---
phase: 13
status: complete
created: 2026-05-17
milestone: v2.4
---

# Phase 13 Context: Pilot Decision Dashboard

## Goal

Convert the Top 3 shortlist and Phase 12 evidence status into a management-facing pilot decision dashboard. The app should answer: which candidate is currently strongest, what blocks committee advancement, and what evidence must be closed next.

## Inputs

- Phase 10 shortlist decision matrix.
- Phase 11 Top 3 validation pack.
- Phase 12 persisted evidence workspace.

## Scope

- Backend decision service that combines shortlist score, evidence readiness, rejected evidence, and high-priority open gaps.
- Deterministic candidate recommendation labels and action plan.
- Frontend `/pilot-decision` dashboard with lead recommendation, candidate comparison, blockers, and next actions.
- Navigation links from the app shell and evidence workspace.

## Out of Scope

- Final investment approval automation.
- Changing stored shortlist ranks automatically.
- LLM-based decision scoring.

## Verification Target

- Backend tests cover default not-ready state and verified-evidence advancement.
- Full backend tests and frontend production build pass.
- Runtime smoke checks confirm `/api/pilot-decision` and `/pilot-decision` are reachable.
