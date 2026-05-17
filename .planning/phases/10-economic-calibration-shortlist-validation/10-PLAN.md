---
phase: 10
status: complete
created: 2026-05-17
completed: 2026-05-17
---

# Phase 10 Plan: Economic Calibration & Shortlist Validation

## Success Criteria

1. Backend exposes a shortlist decision matrix derived from current scoring, scenario results, port proximity/readiness, economics, and confidence.
2. The matrix produces transparent Top 3/Top 5/watchlist recommendations with rationale and next actions.
3. Frontend exposes `/shortlist` as a usable decision page linked from navigation.
4. Tests, production frontend build, API smoke checks, and GSD state validation pass.

## Plan

### 10-01 Backend Decision Matrix

- Add shortlist schemas.
- Add deterministic shortlist service.
- Add `/api/shortlist/decision-matrix`.
- Include score components: screening, economics, logistics, confidence, final shortlist score.

### 10-02 Validation And Tests

- Add backend tests for empty state and seeded ranked candidate behavior.
- Extend existing scoring assertions for ranking aggregate fields.

### 10-03 Shortlist UI

- Add frontend type/API helper.
- Add `/shortlist` page with KPI summary, score method, Top 3/Top 5 table, caveats, and next actions.
- Add navigation link.

## Non-Goals

- No external market-price scraping in this phase.
- No replacement of deterministic scoring math with LLM output.
- No final investment approval logic.
