---
phase: 14
status: reviewed
created: 2026-05-17
---

# UAT Audit: Operator Workflow

## Runtime Status

All main frontend pages returned HTTP 200. Key backend APIs returned HTTP 200.

## Backend API Smoke

| API | Status |
|-----|--------|
| `/api/health` | PASS |
| `/api/plants/` | PASS |
| `/api/scoring/unit-ranking` | PASS |
| `/api/map/unit-opportunity` | PASS |
| `/api/shortlist/decision-matrix` | PASS |
| `/api/validation-pack/top3` | PASS |
| `/api/evidence/workspace` | PASS |
| `/api/pilot-decision` | PASS |
| `/api/investor-case` | PASS |
| `/api/settings/openrouter/provider` | PASS |
| `/api/documents` | PASS |

## Human UAT Risks

| Risk | Severity | Why It Matters |
|------|----------|----------------|
| User does not know where to start | HIGH | The app has many modules but no guided operator flow. |
| User updates data but does not know what to refresh next | HIGH | Saved data may not be reflected in scoring/decision unless the user knows the sequence. |
| Destructive delete/archive actions lack confirmation | HIGH | Accidental deletion can damage Pre-FEED or scenario work. |
| Evidence proof upload/linking is not obvious | MEDIUM | Evidence status can be changed without a clear source-document path. |
| Pre-FEED page overload | MEDIUM | Too many sub-workflows on one page cause confusion. |
| Technical terms are not translated into operator intent | MEDIUM | User cannot easily map module names to business tasks. |

## Suggested Human Test Script

1. Open `/dashboard`.
2. Identify the current recommended candidate.
3. Open `/pilot-decision`.
4. Read blockers and action plan.
5. Open `/evidence`.
6. Select the top candidate and mark one evidence item as `requested`.
7. Return to `/pilot-decision` and confirm blocker count/status changed.
8. Open `/validation-pack` and verify the management pack is still readable.
9. Try opening `/settings`, `/prefeed`, and `/scenarios` and assess whether they feel like advanced/admin tools.

## UAT Verdict

Runtime: **PASS**.

Operator simplicity: **FAIL until Phase 15 simplification is implemented**.
