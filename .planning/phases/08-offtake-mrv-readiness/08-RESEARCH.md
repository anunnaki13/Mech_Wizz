---
phase: 08-offtake-mrv-readiness
type: research
status: ready
created: 2026-05-16
---

# Phase 8 Research

## Relevant Existing Patterns

- Phase 7 Pre-FEED extensions use package-scoped SQLAlchemy models, Pydantic schemas, service-layer validation, thin FastAPI routers under `/api/prefeed`, and frontend helpers in `frontend/lib/api.ts`.
- Phase 7 active selections return scenario-ready patches without mutating `FinancialAssumption` or historical result tables.
- Scenario outputs already persist methanol production and captured CO2 in `ScenarioResult`.
- Existing calculation helpers convert carbon price and calculate gross revenue in deterministic backend code.
- `/prefeed` is already a dense operational workspace with child components for package and cost/vendor workflows.

## Implementation Guidance

- Keep Phase 8 records in one new model module, schema module, service module, router module, and migration.
- Prefer rule-based scores with simple transparent weights over hidden heuristics.
- Keep active price deck selection inside the price deck service; do not introduce global market settings.
- Use latest `ScenarioResult` for scenario output context when available, and return warnings when it is unavailable.
- Preserve package/document validation from Phase 7: supporting documents must exist and match package plant/scenario.
- Add focused tests for CRUD, active deck behavior, revenue summary, MRV summary, gaps, and no history mutation.

## Risks

- Carbon intensity formulas are indicative only. Label them as such and return warnings where source inputs are incomplete.
- Price deck and offtake values may duplicate existing `FinancialAssumption` fields. Phase 8 should return patches/summaries, not mutate existing scenario assumptions.
- UI can become too large if added directly to `PreFeedWorkspace.tsx`; implement a child component.

---
*Research completed: 2026-05-16*
