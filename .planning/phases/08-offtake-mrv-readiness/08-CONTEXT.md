---
phase: 08-offtake-mrv-readiness
gathered: 2026-05-16T15:45:00+07:00
status: ready_for_planning
mode: auto
---

# Phase 8: Offtake & MRV Readiness - Context

<domain>
## Phase Boundary

Phase 8 adds commercial offtake, price deck, MRV, carbon intensity, carbon credit readiness, deterministic revenue impact, and readiness/gap outputs for the selected Pre-FEED package.

This phase does not implement the risk register, decision gates, final Pre-FEED dashboard, committee brief generation, OCR/table extraction, live MRV telemetry, or legal/financing approval workflows. Those remain Phase 9 or future scope.

</domain>

<decisions>
## Implementation Decisions

### Parentage And Audit

- **D-01:** Offtake prospects belong to `pre_feed_package_id`; the package remains the audit parent.
- **D-02:** Price decks belong to a Pre-FEED package and may reference the scenario the package is evaluating.
- **D-03:** MRV assumptions belong to a Pre-FEED package and may reference an existing uploaded MRV document.
- **D-04:** Phase 8 must not mutate `FinancialAssumption`, `ScenarioResult`, `UnitScoringResult`, or prior Phase 7 active cost-basis selections. It returns scenario-ready patches/summaries only.
- **D-05:** Supporting documents reuse the existing `documents` table and Phase 6 package document roles.

### Offtake And Price Deck

- **D-06:** Offtake records capture counterparty, product, target volume, term, pricing basis, optional price, status, supporting document, `data_status`, `confidence_level`, and notes.
- **D-07:** Initial product vocabulary is `e_methanol`, `carbon_credit`, `co2_supply`, `hydrogen`, and `other`.
- **D-08:** Initial offtake status vocabulary is `lead`, `discussion`, `loi`, `term_sheet`, `contracted`, `signed`, and `inactive`.
- **D-09:** Price decks capture methanol, carbon credit, electricity, hydrogen, exchange rate, escalation, `data_status`, `confidence_level`, and active/inactive state.
- **D-10:** Only one price deck should be active per package. Creating or activating a deck with `is_active=true` deactivates prior active decks for that package.
- **D-11:** Revenue summary is deterministic backend code and uses the active package price deck plus stored offtake prospects. LLMs must not calculate revenue.
- **D-12:** Revenue summary may return a scenario-ready patch for market assumptions and gross revenue, but it does not write those values into scenario history.

### Offtake Readiness

- **D-13:** Offtake readiness score is rule-based and uses counterparty/status strength, methanol volume coverage, term certainty, pricing clarity, and document/confidence strength.
- **D-14:** Methanol volume coverage uses the latest stored `ScenarioResult.methanol_ton_per_year` when available; otherwise it returns a warning and keeps the score conservative.
- **D-15:** Offtake gaps should flag missing prospects, missing active price deck, missing methanol price, missing carbon credit price, missing target volume, unclear pricing basis, weak status, missing supporting document, and low/unknown confidence.

### MRV And Carbon Market Readiness

- **D-16:** MRV assumptions capture baseline emissions, captured CO2 accounting, methanol pathway, electricity source, electricity emission factor, carbon credit methodology, verification status, eligibility status, eligibility basis, `data_status`, `confidence_level`, and notes.
- **D-17:** Initial verification status vocabulary is `not_started`, `method_selected`, `data_collected`, `third_party_review`, and `verified`.
- **D-18:** Initial carbon credit eligibility vocabulary is `unknown`, `screening`, `potentially_eligible`, `eligible`, and `not_eligible`.
- **D-19:** Carbon intensity and abatement values are indicative deterministic backend outputs. If stored product carbon intensity exists, use it; otherwise derive a conservative intensity from scenario baseline/captured CO2 and methanol output when possible.
- **D-20:** MRV readiness score is rule-based and uses baseline data, captured CO2 accounting, methodology, verification status, electricity/source evidence, carbon credit eligibility, and confidence.
- **D-21:** MRV gaps should include impact, priority, owner, recommendation, status, and confidence, and flag missing baseline, captured accounting, methodology, verification, electricity source/emission factor, eligibility basis, supporting document, and low/unknown confidence.

### UI Behavior

- **D-22:** Extend existing `/prefeed` rather than adding a new route.
- **D-23:** Add a compact Offtake & MRV workspace below the existing cost/vendor panels.
- **D-24:** Frontend must render backend readiness scores, revenue/carbon outputs, and gaps. It must not recalculate revenue, readiness, carbon intensity, or gaps.
- **D-25:** Keep the Phase 8 UI operational and dense: price deck panel, offtake prospect panel, MRV assumption panel, summary cards, and gap lists.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md` - Product guardrails and deterministic-source-of-truth constraint.
- `.planning/REQUIREMENTS.md` - Phase 8 requirements `OFFT-01` through `MRV-04`.
- `.planning/ROADMAP.md` - Phase 8 goal, success criteria, and plan split.
- `.planning/STATE.md` - Current GSD state and gitdir constraint.
- `.planning/phases/06-pre-feed-package-foundation/06-CONTEXT.md` - Package and document parentage decisions.
- `.planning/phases/07-cost-vendor-proposal-engine/07-CONTEXT.md` - Cost/vendor active basis and backend-only calculation decisions.
- `docs/blueprint.md` - Original MECH WIZ formulas and market assumptions.
- `docs/MECH_WIZ_Heatmap_Map_Addendum.md` - Score/confidence/data status vocabulary.

</canonical_refs>

<code_context>
## Existing Code Insights

- `backend/app/models/pre_feed_package.py` is the Phase 8 parent model.
- `backend/app/models/pre_feed_cost.py` shows Phase 7 package-scoped Pre-FEED extension patterns.
- `backend/app/services/prefeed_costs.py` has reusable package/document validation and scenario-history preservation patterns.
- `backend/app/models/scenario_result.py` provides latest deterministic scenario outputs for methanol, captured CO2, and revenue context.
- `backend/app/services/calculations/financial.py` already has carbon credit and revenue helper formulas that Phase 8 can reuse or mirror.
- `frontend/components/prefeed/PreFeedWorkspace.tsx` should import a new child component for Phase 8.
- `frontend/components/prefeed/CostVendorWorkspace.tsx` is the closest frontend pattern for package-scoped create/list/summary/gap panels.
- `frontend/lib/api.ts` should add typed helpers under existing `/prefeed` API paths.

</code_context>

<deferred>
## Deferred Ideas

- Automatic structured extraction of offtake/MRV data from documents remains future document intelligence scope.
- Legal enforceability review and financing approval remain outside v2.0.
- Final Pre-FEED dashboard integration and committee brief generation are Phase 9.
- Live MRV telemetry remains v3 operational digital twin scope.

</deferred>

---
*Phase: 08-Offtake & MRV Readiness*
*Context gathered: 2026-05-16T15:45:00+07:00*
