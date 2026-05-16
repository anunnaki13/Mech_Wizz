# Phase 9 Research: Risk & Pre-FEED Decision Dashboard

## Implementation Direction

Phase 9 can be implemented with the same local stack and patterns used in Phases 6-8:

- SQLAlchemy models with UUID string IDs and SQLite-compatible Alembic migrations.
- FastAPI routers under `/api/prefeed`.
- Pydantic schemas with explicit Literal vocabularies and backend validation.
- Deterministic service functions that compose upstream Phase 6-8 outputs.
- Next.js client components integrated into `/prefeed`.
- Existing OpenRouter LLM integration for committee brief generation.

No new framework or external service is required.

## Backend Pattern

Use a new `pre_feed_decision` model/service/schema/router set:

- `PreFeedRisk`
- `PreFeedDecisionGate`
- `build_risk_summary`
- `build_decision_gate_summary`
- `build_prefeed_decision_dashboard`
- `build_prefeed_committee_brief_context`

The service can import Phase 6-8 service functions:

- `get_package_gaps` or equivalent from `app.services.prefeed`
- `build_cost_summary`, `build_vendor_comparison`, `get_active_cost_basis`
- `build_offtake_summary`, `generate_offtake_gaps`
- `build_mrv_summary`, `generate_mrv_gaps`

When upstream data is incomplete, the dashboard should return warnings and blockers. It should not fill missing numeric values with fabricated assumptions.

## Risk Scoring

Use a simple deterministic severity model:

- severity score = likelihood * impact
- severity band:
  - `low`: 1-5
  - `medium`: 6-11
  - `high`: 12-19
  - `critical`: 20-25

Top risks sort by severity score descending, escalated/open status first, then due date.

## Decision Gates

Gate readiness can be summarized by counts and a readiness score:

- `ready` and `waived` count as complete.
- `blocked` is a blocker.
- Critical gates that are not `ready`/`waived` are blockers.
- Readiness score = complete gates / total gates, rounded by backend.

## Committee Brief

Extend the LLM insight type vocabulary with `prefeed_committee_brief`. The prompt should reuse the project calculation authority rules:

- Use only supplied context.
- Do not invent numbers.
- Do not recalculate deterministic outputs.
- Separate actual data, assumptions, confidence, and gaps.
- Write concise professional Indonesian.

The insight can persist against `plant_id` and `scenario_id` because `LlmInsight` has no package field. The prompt context must include the package ID/name so the audit trail remains clear.

## UI Pattern

Add a `DecisionDashboardWorkspace` child component to `/prefeed`:

- Management summary cards from the backend aggregate.
- Blockers and next actions lists.
- Risk register form/table.
- Decision gate form/table.
- Committee brief trigger and latest response/status.

Keep the layout operational and dense. The component should not calculate severity, readiness, blockers, revenue, carbon, or cost totals.
