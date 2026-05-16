# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 - MVP

**Shipped:** 2026-05-16
**Phases:** 5 | **Plans:** 15 | **Sessions:** 1

### What Was Built

- Runnable FastAPI/Next.js/Docker Compose MVP with Tenayan seed data and unit input workflows.
- Deterministic scenario simulation for CO2, e-methanol, H2, revenue, LCOM, NPV, IRR, payback, and persisted outputs.
- MapLibre strategy dashboard with opportunity heatmap, ranking, selected profile, score breakdown, and sensitivity view.
- Investor dashboard with deterministic aggregate data, data gaps, confidence labels, editable defaults, and scoring weights.
- OpenRouter-backed insight workflows with persisted prompt/response audit trail and document upload/extraction/Q&A.

### What Worked

- Vertical MVP slicing kept every phase user-visible and reduced integration surprises.
- Deterministic backend calculations stayed the source of truth; frontend pages consumed stored outputs.
- Null-safe economics avoided fabricated IRR/NPV/LCOM when CAPEX inputs were missing.
- Phase summaries and verification artifacts were useful for milestone audit and requirement reconciliation.

### What Was Inefficient

- `REQUIREMENTS.md` was not updated continuously during phase execution, so milestone close needed a reconciliation pass.
- Next.js `next build` conflicted with the running dev `.next` cache; dev server restart became part of the verification routine.
- Local SQLite dev DB drifted once because app-created tables existed before Alembic version stamping; fresh migration checks caught the issue.
- Some browser-level visual QA remains manual; production readiness would benefit from Playwright screenshots for dashboard/map routes.

### Patterns Established

- Persist calculation outputs and read models; do not recalculate in the browser.
- Use explicit `data_status`, `confidence_level`, and data gap records whenever inputs are incomplete.
- Keep LLM prompts backend-only, guardrailed, and fully persisted.
- Treat document Q&A as grounded context over extracted text until vector retrieval is justified.
- Use `GIT_DIR=.git-real GIT_WORK_TREE=.` for git operations in this workspace because `.git` is a read-only tmpfs mount.

### Key Lessons

1. Requirement checkboxes should be updated at each phase close, not only at milestone close.
2. Fresh database migrations are the best guard against hidden dev DB drift.
3. Backend aggregate endpoints make dashboard and LLM integration simpler than duplicating cross-module logic in the frontend.
4. Missing configuration should fail explicitly and persist audit records rather than producing fake fallback responses.

### Cost Observations

- Model mix: Codex primary execution with no spawned subagents.
- Sessions: 1 milestone execution session.
- Notable: Inline execution was efficient, but future milestone audits can benefit from explicit user permission for subagents if cross-phase review grows.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 1 | 5 | Established full GSD plan/execute/verify/archive loop for MECH WIZ |

### Cumulative Quality

| Milestone | Tests | Verification | Notable Debt |
|-----------|-------|--------------|--------------|
| v1.0 | 37 backend tests plus frontend build | 5/5 phase verifications PASS, milestone audit PASS | Live OpenRouter key validation, OCR, production map tiles |

### Top Lessons

1. Keep numeric authority deterministic and auditable before adding narrative AI.
2. Preserve nulls and confidence labels rather than hiding incomplete assumptions.
3. Archive milestone artifacts immediately after completion so active planning files stay small.
