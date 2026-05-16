---
phase: 08-offtake-mrv-readiness
plan: "03"
subsystem: prefeed-offtake-mrv-ui
tags: [nextjs, prefeed-ui, offtake, mrv, readiness]
requires:
  - phase: 08-offtake-mrv-readiness
    plan: "01"
    provides: Offtake and price deck APIs
  - phase: 08-offtake-mrv-readiness
    plan: "02"
    provides: MRV summary and gap APIs
provides:
  - `/prefeed` Offtake & MRV workspace
  - Frontend Phase 8 API types and helpers
  - Phase 8 README workflow and API documentation
  - Phase 8 verification and review artifacts
requirements-completed: [OFFT-01, OFFT-02, OFFT-03, OFFT-04, MRV-01, MRV-02, MRV-03, MRV-04]
duration: 14min
completed: 2026-05-16
---

# Phase 8 Plan 03: Offtake And MRV UI Summary

Extended `/prefeed` with package-scoped offtake, price deck, MRV, readiness, revenue, carbon, and gap panels.

## Performance

- **Duration:** 14 min
- **Started:** 2026-05-16T16:03:00+07:00
- **Completed:** 2026-05-16T16:17:00+07:00
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added typed frontend contracts for price decks, offtake prospects, offtake summary/gaps, MRV assumptions, MRV summary/gaps.
- Added API helpers for all Phase 8 endpoints.
- Added `OfftakeMrvWorkspace` with price deck, offtake, MRV, summary cards, and backend-authored gap panels.
- Integrated Phase 8 UI into the existing `/prefeed` workspace.
- Updated README with the Phase 8 user workflow and API endpoints.
- Added final verification and review artifacts for the full Phase 8 scope.

## Verification

- `cd frontend && npm run build` - passed.
- `docker compose config` - passed.
- `cd backend && pytest -q` - passed, 45 tests.
- `DATABASE_URL=sqlite:////tmp/mechwiz_phase8_full.db .venv/bin/alembic upgrade head` - passed through migration 0010.
- `rg -n "OfftakeMrvWorkspace|PreFeedOfftakeProspect|PreFeedMrvAssumption|OFFT-01|MRV-04|offtake-summary|mrv-summary" backend frontend .planning/phases/08-offtake-mrv-readiness README.md` - expected matches found.

---
*Phase: 08-offtake-mrv-readiness*
*Completed: 2026-05-16*
