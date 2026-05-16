# Phase 6: Pre-FEED Package Foundation - Context

**Gathered:** 2026-05-16T14:36:00+07:00
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 6 delivers the foundational Pre-FEED package layer only. It creates auditable package records linked to existing plants, scenarios, and uploaded documents; captures source/version/status/confidence metadata; and exposes package-level gaps and warnings for later cost, vendor, offtake, MRV, risk, dashboard, and LLM phases.

This phase does not implement CAPEX/OPEX line items, vendor comparison, offtake, MRV calculations, risk register, or the final Pre-FEED decision dashboard. Those are explicitly Phase 7, Phase 8, and Phase 9.

</domain>

<decisions>
## Implementation Decisions

### Package Identity And Parentage

- **D-01:** A Pre-FEED package belongs to a `plant_id` and may optionally reference a `scenario_id`.
- **D-02:** Phase 6 should not split `plants` into `plant_sites` / `plant_units`; continue using the v1.0 `Plant` identity unless a later phase proves multi-unit modelling is required.
- **D-03:** A package should have a stable UUID, human-readable package name, package status, owner, source organization, received date, version label, `data_status`, `confidence_level`, notes, and timestamps.

### Document Linking

- **D-04:** Reuse the existing `Document` model and upload/extraction workflow from Phase 5; Phase 6 adds package-document association rather than a second upload system.
- **D-05:** Package document links need a document role/category such as `vendor_proposal`, `epc_estimate`, `offtake_document`, `mrv_document`, `permit_document`, or `internal_note`.
- **D-06:** Existing document metadata and extracted text stay owned by the document layer. Package links should reference documents and add relationship-specific metadata only.

### Audit And History

- **D-07:** Creating or updating a Pre-FEED package must not overwrite historical `ScenarioResult`, `UnitScoringResult`, `SensitivityResult`, or prior LLM insight records.
- **D-08:** Phase 6 should persist package metadata as its own source-of-truth records. Later phases can derive active assumptions from packages, but this phase only prepares the package foundation.
- **D-09:** Package archival should be a soft state/status, not destructive deletion, so committee review history remains auditable.

### Gaps And Confidence

- **D-10:** Package-level gap detection should be deterministic and rule-based, not LLM-generated.
- **D-11:** Gap output should reuse the existing data quality language: missing data name, source module, impact, priority, recommendation, status, and confidence.
- **D-12:** For Phase 6, gaps should focus on package metadata and document readiness, such as missing owner, source organization, received date, version, required document role, or low-confidence package status.

### UI Behavior

- **D-13:** Add a `/prefeed` workspace route rather than overloading `/documents`, `/settings`, or `/investor`.
- **D-14:** The first `/prefeed` screen should be an operational workspace with plant/scenario/package selectors, package metadata editor, linked documents table, and package warnings. Avoid a marketing-style page.
- **D-15:** Keep the UI consistent with existing dashboard patterns: `AppShell`, compact panels, table/list views, status pills, and null-safe labels.

### the agent's Discretion

- Choose exact enum names and field names conservatively, matching existing Python/TypeScript snake_case API patterns.
- Decide whether package gap summaries are backed by a new table or computed on read, as long as the behavior is deterministic and testable.
- Pick the smallest viable frontend component split that keeps `/prefeed` maintainable and consistent with existing `/documents` and `/settings` workspaces.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone And Phase Scope

- `.planning/PROJECT.md` - Current product state, v2.0 Pre-FEED target, validated v1.0 decisions, and active constraints.
- `.planning/REQUIREMENTS.md` - v2.0 requirements and Phase 6 requirement traceability for `PFD-01` through `PFD-05`.
- `.planning/ROADMAP.md` - Phase 6 goal, success criteria, and plan split.
- `.planning/STATE.md` - Current milestone state, decisions, and known blockers.

### v1.0 Archive Context

- `.planning/milestones/v1.0-ROADMAP.md` - Shipped phase scope and ordering from v1.0.
- `.planning/milestones/v1.0-REQUIREMENTS.md` - Completed v1.0 requirement set and terminology.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 verification evidence and deferred technical debt.
- `.planning/milestones/v1.0-phases/05-llm-document-intelligence/05-03-SUMMARY.md` - Document upload/extraction/Q&A implementation summary.
- `.planning/milestones/v1.0-phases/04-investor-case-data-quality/04-03-SUMMARY.md` - Data gap/settings implementation summary.
- `.planning/milestones/v1.0-phases/02-scenario-simulation-engine/02-03-SUMMARY.md` - Scenario result persistence and history patterns.

### Source Blueprint

- `docs/MECH_WIZ_Heatmap_Map_Addendum.md` - Scoring and confidence vocabulary already imported for map/ranking context.
- `MECH_WIZ_AI_Digital_Twin_Blueprint.md` - Original MECH WIZ product blueprint, if present locally. If absent, use `docs/` imports and planning archives as the canonical local source.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/models/document.py` and `backend/app/routers/documents.py`: Reuse document metadata, storage, extraction status, and extracted text ownership.
- `backend/app/models/business_scenario.py`: Use existing scenario parent/reference pattern for optional `scenario_id`.
- `backend/app/models/plant.py`: Continue using `Plant` as the v2.0 package parent.
- `backend/app/models/data_gap.py` and `backend/app/services/data_quality.py`: Reuse data gap vocabulary and deterministic gap style.
- `backend/app/models/application_setting.py` and `backend/app/services/settings.py`: Reuse validated JSON/settings patterns if package defaults are needed.
- `frontend/components/documents/DocumentWorkspace.tsx`: Reuse document table/detail/upload interaction patterns for linked documents.
- `frontend/components/settings/SettingsWorkspace.tsx`: Reuse dense settings/editor layout patterns.
- `frontend/lib/api.ts`: Add typed Pre-FEED API helpers following existing `apiFetch` and FormData-safe conventions.

### Established Patterns

- Backend ORM models use UUID string IDs, timestamps, `data_status`, and `confidence_level` where relevant.
- FastAPI routers live under `/api`, are registered in `backend/app/main.py`, and have focused Pydantic schemas.
- Alembic migrations are versioned and must pass from a fresh SQLite database during verification.
- Tests use SQLite dependency overrides and should cover service behavior plus API happy/error paths.
- Frontend pages use App Router, `dynamic = "force-dynamic"` when data is API-backed, and domain workspaces under `frontend/components/<domain>/`.
- Frontend should display unavailable values explicitly rather than fabricating or hiding important data.

### Integration Points

- New backend route group should likely be `/api/prefeed` or `/api/pre-feed-packages`; choose one consistent name and expose typed frontend helpers.
- New frontend route should be `/prefeed` and should be added to `AppShell` navigation.
- Document links should connect existing `Document.id` records to package records without changing document upload semantics.
- Package gap/confidence output should be available to later Phase 7-9 aggregate services and Phase 9 LLM context.

</code_context>

<specifics>
## Specific Ideas

- Phase 6 should seed or allow creating a Tenayan Pre-FEED starter package only if it helps local smoke testing and does not imply real Pre-FEED data exists.
- Package statuses should distinguish draft/in review/validated/archived or equivalent operational states.
- Required document roles for gap detection can start with vendor proposal, EPC estimate, offtake document, MRV document, and internal note; later phases can refine the list.

</specifics>

<deferred>
## Deferred Ideas

- Detailed CAPEX/OPEX line item entry and aggregation belongs to Phase 7.
- Vendor comparison and active cost basis selection belongs to Phase 7.
- Offtake, price decks, MRV assumptions, carbon intensity, and carbon credit readiness belong to Phase 8.
- Risk register, decision gates, blockers, committee dashboard, and Pre-FEED LLM brief belong to Phase 9.
- OCR, vector retrieval, and structured table extraction from proposal PDFs remain future document intelligence scope.

</deferred>

---

*Phase: 6-Pre-FEED Package Foundation*
*Context gathered: 2026-05-16T14:36:00+07:00*
