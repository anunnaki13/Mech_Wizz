---
phase: 11
status: complete
created: 2026-05-17
completed: 2026-05-17
---

# Phase 11 Plan: Top 3 Validation Pack & Committee Memo

## Success Criteria

1. Backend exposes a Top 3 validation pack API derived from shortlist results.
2. Backend exposes a committee memo PDF endpoint.
3. Frontend exposes `/validation-pack` with candidate comparison, validation checklist, memo preview, and PDF link.
4. Tests, frontend build, runtime smoke checks, and GSD validation pass.

## Plan

### 11-01 Backend Validation Pack

- Add validation pack schemas, service, and router.
- Include Top 3 summary, candidate score/evidence cards, comparison axes, committee memo, caveats, and PDF generation.

### 11-02 UI

- Add frontend types and API helper.
- Add `/validation-pack` page and navigation links.
- Link from `/shortlist`.

### 11-03 Verification

- Add backend API/PDF tests.
- Run full backend tests and frontend production build.
- Restart local servers and smoke test.
