---
phase: 13
status: complete
completed: 2026-05-17
---

# Phase 13 Summary: Pilot Decision Dashboard

## Delivered

- Added `/api/pilot-decision` deterministic decision-support API.
- Added evidence-adjusted decision score: 70% shortlist score + 30% evidence readiness, with penalties for rejected evidence and high-priority open gaps.
- Added candidate gate labels: `committee_ready`, `needs_evidence`, and `blocked`.
- Added candidate blockers, next actions, portfolio action plan, methodology, and warnings.
- Added `/pilot-decision` page linked from navigation and the Evidence workspace.

## Decisions

- Pilot decision score is read-only and does not mutate stored shortlist ranks.
- Committee-ready requires evidence readiness >= 80%, zero rejected evidence, and zero high-priority open evidence.
- Rejected evidence blocks advancement even when the screening shortlist score is high.

## Verification

- `backend/.venv/bin/pytest backend/tests/test_pilot_decision.py -q` — 2 passed.
- `backend/.venv/bin/pytest -q` — 63 passed.
- `npm run build` — passed.
- Runtime smoke: `/api/pilot-decision?scheme=align&limit=3` returned 3 candidates, lead `UP Paiton`, gate `needs_evidence`, and 12 blockers.
- Runtime smoke: `/pilot-decision` rendered `Pilot Decision Dashboard`, `Candidate Decision Ranking`, `Action Plan`, and `Top Blockers`.

## Runtime Notes

- The dashboard will initially show `needs_evidence` until real evidence is verified in `/evidence`.
- The recommendation updates immediately after evidence statuses are saved.
