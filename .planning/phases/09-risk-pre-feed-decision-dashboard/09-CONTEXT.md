---
phase: 09-risk-pre-feed-decision-dashboard
gathered: 2026-05-16T19:34:33+07:00
status: ready_for_planning
mode: auto
---

# Phase 9: Risk & Pre-FEED Decision Dashboard - Context

<domain>
## Phase Boundary

Phase 9 turns the completed Pre-FEED package, cost/vendor, offtake, and MRV data into a management-facing decision workspace. It adds package-scoped risk register records, decision gate checklist records, deterministic blockers and next actions, dashboard aggregate panels, and a committee brief LLM workflow.

This phase does not implement legal approval workflows, financing workflow automation, live operational telemetry, document extraction of risk items, or automatic mutation of scenario/financial assumptions. Those remain future workflow or operational digital twin scope.

</domain>

<decisions>
## Implementation Decisions

### Risk Register

- **D-01:** Risk records belong to `pre_feed_package_id`; the Pre-FEED package remains the audit parent.
- **D-02:** Risk categories start with `technical`, `commercial`, `legal`, `land`, `grid`, `offtake`, `mrv`, `financing`, `economics`, `execution`, and `other`.
- **D-03:** Risk likelihood and impact are integer scales from 1 to 5; severity is deterministic backend output as `likelihood * impact`.
- **D-04:** Risk status starts with `open`, `monitoring`, `mitigating`, `escalated`, and `closed`.
- **D-05:** Risk records capture risk statement, mitigation, owner, due date, status, `data_status`, `confidence_level`, and notes.
- **D-06:** Risk summaries are deterministic backend outputs. They expose top risks, severity distribution, open/escalated counts, and warnings without mutating package, scenario, cost, offtake, MRV, or historical result tables.

### Decision Gates And Blockers

- **D-07:** Decision gate checklist items belong to `pre_feed_package_id`.
- **D-08:** Gate categories start with `technical`, `commercial`, `legal`, `land`, `grid`, `offtake`, `mrv`, `financing`, and `committee`.
- **D-09:** Gate status starts with `not_started`, `in_progress`, `ready`, `blocked`, and `waived`.
- **D-10:** Gate items capture title, evidence, owner, due date, critical flag, status, `data_status`, `confidence_level`, and notes.
- **D-11:** Blockers are generated deterministically from escalated/high risks, critical gates that are blocked or not ready, high-priority cost/vendor/offtake/MRV/package gaps, and missing active package assumptions.
- **D-12:** Next actions are rule-based, ordered by urgency, and include source, owner, priority, recommendation, and status.

### Dashboard Aggregate

- **D-13:** Add a backend dashboard aggregate endpoint for the selected package; frontend consumes it rather than assembling management KPIs itself.
- **D-14:** The aggregate composes package metadata, package gaps, cost summary, active cost basis, vendor comparison, offtake summary/gaps, MRV summary/gaps, risk summary, decision gate summary, blockers, and next actions.
- **D-15:** The dashboard may read existing Phase 6-8 services but must not mutate `FinancialAssumption`, `ScenarioResult`, `UnitScoringResult`, `SensitivityResult`, active cost basis records, price decks, offtake records, or MRV records.
- **D-16:** Missing upstream data must be surfaced as warnings and blockers, not hidden or guessed.

### Committee Brief LLM Workflow

- **D-17:** Add a `prefeed_committee_brief` LLM insight type using the existing `LlmInsight` persistence and OpenRouter transport.
- **D-18:** Committee brief context is generated from backend-stored and deterministic aggregate data only; prompts must forbid invented numbers and recalculation.
- **D-19:** If OpenRouter is not configured, the workflow records a failed insight and returns the existing unavailable error pattern.
- **D-20:** The brief is Indonesian, management-facing, and structured around recommendation, readiness, economics, risks, blockers, and next actions.

### UI Behavior

- **D-21:** Extend the existing `/prefeed` workspace rather than adding a new route.
- **D-22:** Add the decision dashboard near the selected package summary so users can see readiness before editing detailed cost/offtake/MRV inputs.
- **D-23:** Add compact risk register and decision gate panels with create/update/delete controls.
- **D-24:** Frontend renders backend dashboard, blocker, next-action, risk, and gate outputs. It must not calculate severity, readiness, blockers, next actions, revenue, carbon, or cost totals.
- **D-25:** Final v2.0 verification must map every Phase 9 requirement and confirm the full Pre-FEED milestone is coherent.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md` - Product guardrails and deterministic-source-of-truth constraint.
- `.planning/REQUIREMENTS.md` - Phase 9 requirements `RISK-01` through `RISK-04` and `PFDASH-01` through `PFDASH-05`.
- `.planning/ROADMAP.md` - Phase 9 goal, success criteria, dependency, and plan split.
- `.planning/STATE.md` - Current GSD state and gitdir constraint.
- `.planning/phases/06-pre-feed-package-foundation/06-CONTEXT.md` - Package/document parentage, confidence, and gap foundation.
- `.planning/phases/07-cost-vendor-proposal-engine/07-CONTEXT.md` - Cost/vendor active basis, deterministic aggregation, and scenario history protection.
- `.planning/phases/08-offtake-mrv-readiness/08-CONTEXT.md` - Offtake/MRV readiness, market summaries, and backend-only calculation decisions.
- `docs/blueprint.md` - Original MECH WIZ formulas and management/investor context.
- `docs/MECH_WIZ_Heatmap_Map_Addendum.md` - Score/confidence/data status vocabulary.

</canonical_refs>

<code_context>
## Existing Code Insights

- `backend/app/models/pre_feed_package.py` remains the package parent and document audit anchor.
- `backend/app/models/pre_feed_cost.py` and `backend/app/models/pre_feed_market.py` show Phase 7/8 package-scoped extension patterns.
- `backend/app/services/prefeed_costs.py` exposes cost summary, vendor comparison, vendor gaps, and active cost basis selection.
- `backend/app/services/prefeed_market.py` exposes offtake summary/gaps and MRV summary/gaps.
- `backend/app/services/llm.py` already owns prompt construction, provider errors, failed insight records, and calculation-authority rules.
- `frontend/components/prefeed/PreFeedWorkspace.tsx` is the integration point for all Phase 9 UI.
- `frontend/components/prefeed/CostVendorWorkspace.tsx` and `frontend/components/prefeed/OfftakeMrvWorkspace.tsx` are the closest operational-panel patterns.
- `frontend/lib/api.ts` and `frontend/types/prefeed-*.ts` should receive typed Phase 9 helpers and contracts.

</code_context>

<deferred>
## Deferred Ideas

- Automatic extraction of risks/gates from uploaded documents remains future document intelligence scope.
- Legal, financing, and committee approval workflow routing remains future workflow scope.
- Live risk telemetry and operational decision support remain v3 operational digital twin scope.

</deferred>

---
*Phase: 09-Risk & Pre-FEED Decision Dashboard*
*Context gathered: 2026-05-16T19:34:33+07:00*
