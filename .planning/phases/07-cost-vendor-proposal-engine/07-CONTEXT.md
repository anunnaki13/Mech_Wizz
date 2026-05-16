# Phase 7: Cost & Vendor Proposal Engine - Context

**Gathered:** 2026-05-16T15:08:00+07:00
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 7 turns Phase 6 Pre-FEED package records into auditable cost and vendor proposal data. It delivers detailed CAPEX/OPEX line items, vendor/EPC proposal records, deterministic proposal comparison, proposal gap detection, and active cost-basis selection for a scenario.

This phase does not implement offtake contracts, market price decks, MRV calculations, risk register, decision gates, committee brief generation, OCR/RAG extraction, or live operational data. Those remain Phase 8, Phase 9, or future document intelligence scope.

</domain>

<decisions>
## Implementation Decisions

### Cost Line Item Model

- **D-01:** Cost line items belong to a `pre_feed_package_id`; a later vendor proposal reference may optionally narrow the source, but the package remains the root audit parent.
- **D-02:** Use one detailed cost item model/table with `cost_type` (`capex` or `opex`) rather than separate CAPEX/OPEX tables. This keeps aggregation, filtering, and package totals consistent.
- **D-03:** CAPEX items must capture component, amount, currency, source label, contingency percent, escalation percent, `data_status`, `confidence_level`, and notes.
- **D-04:** OPEX items must capture category, amount, currency, unit basis, recurrence, source label, `data_status`, `confidence_level`, and notes.
- **D-05:** Standard CAPEX component vocabulary starts with `capture_package`, `electrolyzer`, `methanol_plant`, `storage_port`, `grid_power`, `land`, `mrv`, and `other`.
- **D-06:** Standard OPEX category vocabulary starts with `fixed_opex`, `variable_opex`, `electricity`, `water`, `chemicals`, `labor`, `maintenance`, `transport`, `mrv`, and `other`.

### Aggregation And Scenario-Ready Outputs

- **D-07:** Aggregation is deterministic backend code. LLMs must not calculate CAPEX/OPEX totals or proposal rankings.
- **D-08:** Aggregation returns package/proposal totals by currency. Do not silently convert currencies in Phase 7.
- **D-09:** For USD CAPEX components that map to current simulation fields, aggregation should expose a scenario-ready patch for `capex_capture_usd`, `capex_electrolyzer_usd`, `capex_methanol_plant_usd`, and `capex_storage_port_usd` without directly mutating `FinancialAssumption`.
- **D-10:** Active cost-basis selection must be a separate auditable selection record with snapshot totals and source metadata. It must not overwrite `FinancialAssumption`, `ScenarioResult`, `UnitScoringResult`, or `SensitivityResult`.
- **D-11:** When a new active cost basis is selected for a scenario, prior selection records should be retained and marked inactive rather than deleted.

### Vendor Proposal Model

- **D-12:** Vendor proposals belong to a Pre-FEED package and may reference an existing uploaded document as supporting evidence.
- **D-13:** Vendor proposal fields include vendor name, proposal name, commercial basis, delivery assumptions, exclusions, validity date, `data_status`, `confidence_level`, notes, and timestamps.
- **D-14:** Proposal scope coverage should be explicit structured booleans for capture package, electrolyzer, methanol plant, storage/port, grid power, land, and MRV. This enables deterministic comparison and gap flags.
- **D-15:** Proposal comparison ranks/compares proposals by deterministic totals, scope completeness, missing scopes, assumptions/exclusions presence, validity, and confidence.

### Proposal Gaps

- **D-16:** Vendor proposal gaps are deterministic and rule-based, using the same data quality language as Phase 4 and Phase 6.
- **D-17:** Phase 7 proposal gaps should flag missing electrolyzer scope, capture package, methanol plant, storage/port, grid power, land, MRV scope, missing commercial basis, missing validity date, missing cost items, and low/unknown confidence.
- **D-18:** Missing offtake/MRV readiness calculations remain Phase 8. Phase 7 only records whether MRV scope is included in a vendor proposal.

### UI Behavior

- **D-19:** Extend the existing `/prefeed` workspace rather than creating a separate `/costs` or `/vendors` route.
- **D-20:** The Phase 7 UI should keep the package selector from Phase 6 and add compact cost/vendor panels for line items, proposal scope, comparison, and active cost-basis selection.
- **D-21:** The UI must display backend aggregation and gap outputs. It must not recalculate totals or rank proposals in frontend code.

### the agent's Discretion

- Choose exact endpoint names under `/api/prefeed` as long as they are consistent and typed in `frontend/lib/api.ts`.
- Choose a compact component split for `/prefeed` that avoids making `PreFeedWorkspace.tsx` unmaintainable.
- Use SQLite-compatible migrations and tests that keep Phase 6 package behavior intact.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone And Phase Scope

- `.planning/PROJECT.md` - Current v2.0 Pre-FEED product state and deterministic-source-of-truth constraints.
- `.planning/REQUIREMENTS.md` - Phase 7 requirements `COST-01` through `COST-03` and `VEND-01` through `VEND-04`.
- `.planning/ROADMAP.md` - Phase 7 goal, success criteria, dependencies, and plan split.
- `.planning/STATE.md` - Current milestone state and known gitdir constraint.

### Direct Dependency

- `.planning/phases/06-pre-feed-package-foundation/06-CONTEXT.md` - Phase 6 package parentage, document linking, audit, and UI decisions.
- `.planning/phases/06-pre-feed-package-foundation/06-VERIFICATION.md` - Evidence that package/document/gap foundation is complete.
- `.planning/phases/06-pre-feed-package-foundation/06-03-SUMMARY.md` - `/prefeed` workspace implementation summary.

### Source Blueprint And v1 Archive

- `docs/MECH_WIZ_Heatmap_Map_Addendum.md` - Existing score/confidence/data status vocabulary.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - Completed v1.0 constraints and deferred Pre-FEED scope.
- `.planning/milestones/v1.0-phases/02-scenario-simulation-engine/02-03-SUMMARY.md` - Scenario result persistence and history protection patterns.
- `.planning/milestones/v1.0-phases/04-investor-case-data-quality/04-03-SUMMARY.md` - Data gap vocabulary and settings patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/models/pre_feed_package.py`: Use `PreFeedPackage` as Phase 7 package parent and document audit anchor.
- `backend/app/schemas/pre_feed.py`: Reuse package/document read schemas where cost/vendor responses need package context.
- `backend/app/services/prefeed.py`: Reuse package lookup, parent validation, and deterministic gap style.
- `backend/app/models/financial_assumption.py`: Use field names only for scenario-ready patch output; do not update it in Phase 7.
- `backend/app/models/scenario_result.py`, `unit_scoring_result.py`, `sensitivity_result.py`: Must remain untouched by active cost-basis selection.
- `frontend/components/prefeed/PreFeedWorkspace.tsx`: Extend this route/workspace rather than building another top-level app area.
- `frontend/types/prefeed.ts` and `frontend/lib/api.ts`: Add Phase 7 types/helpers beside existing package helpers.

### Established Patterns

- Backend models use UUID string IDs and SQLAlchemy typed mappings.
- FastAPI routes live under `/api`, with thin routers and validation/service logic.
- Tests use in-memory SQLite dependency overrides and seed Tenayan records where useful.
- Frontend should consume backend calculations and display null-safe explicit values.
- UI uses compact cards, tables, status chips, notices, and AppShell navigation.

### Integration Points

- New APIs should live under `/api/prefeed/...`.
- Cost items and vendor proposals should reference `pre_feed_packages.id`.
- Vendor proposal supporting documents should reference existing `documents.id`.
- Active cost-basis selection should reference `business_scenarios.id`, package, and optional vendor proposal.
- `/prefeed` should expose cost and vendor controls for the selected package/scenario.

</code_context>

<specifics>
## Specific Ideas

- Treat package-level totals as a "blended package" option for active cost basis when no single vendor proposal is selected.
- Initial aggregation can return totals by currency plus a USD-only simulation patch for fields that already exist.
- Proposal comparison should expose missing scope lists rather than hiding incomplete vendor submissions.

</specifics>

<deferred>
## Deferred Ideas

- Currency conversion and FX decks belong to Phase 8 price deck work unless a later phase explicitly promotes them.
- Offtake readiness, MRV calculations, carbon intensity, and carbon credit assumptions belong to Phase 8.
- Risk register, decision gates, blockers, and final Pre-FEED dashboard belong to Phase 9.
- OCR/table extraction from vendor PDFs remains future document intelligence scope.

</deferred>

---

*Phase: 7-Cost & Vendor Proposal Engine*
*Context gathered: 2026-05-16T15:08:00+07:00*
