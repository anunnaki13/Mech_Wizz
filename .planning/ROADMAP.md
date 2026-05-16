# Roadmap: MECH WIZ AI Digital Twin

## Milestones

- [x] **v1.0 MVP** - Shipped 2026-05-16. Five-phase pre-feasibility simulator with deterministic calculations, MapLibre strategy dashboard, investor case, OpenRouter insight workflows, and document intelligence.
- [ ] **v2.0 Pre-FEED** - In planning. Cost package validation, vendor comparison, offtake readiness, MRV assumptions, risk governance, and Pre-FEED decision dashboard.

## Completed Milestones

<details>
<summary>v1.0 MVP (Phases 1-5) - SHIPPED 2026-05-16</summary>

Full archive:

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.0-phases/`

Milestone result:

- Phases complete: 5/5
- Plans complete: 15/15
- Requirements satisfied: 69/69
- Audit status: PASS

</details>

## Active Milestone: v2.0 Pre-FEED

The v2.0 milestone extends the v1.0 pre-feasibility simulator into a Pre-FEED decision workspace. It adds auditable cost packages, vendor proposal comparison, offtake and MRV readiness, detailed risk governance, and a management-facing Pre-FEED dashboard without allowing LLMs to become the numeric source of truth.

## Phases

**Phase Numbering:**
- Phase numbering continues from the completed v1.0 milestone.
- Phase 6 is the first v2.0 phase.
- Decimal phases may be inserted later for urgent fixes.

- [x] **Phase 6: Pre-FEED Package Foundation** - Package records, document links, source/version metadata, confidence, and package-level gaps. (completed 2026-05-16)
- [x] **Phase 7: Cost & Vendor Proposal Engine** - Detailed CAPEX/OPEX line items, proposal comparison, selected active cost basis, and scenario-ready aggregates. (completed 2026-05-16)
- [x] **Phase 8: Offtake & MRV Readiness** - Offtake prospects, price decks, revenue impact, MRV assumptions, carbon intensity, and carbon credit readiness. (completed 2026-05-16)
- [ ] **Phase 9: Risk & Pre-FEED Decision Dashboard** - Risk register, decision gates, blockers, dashboard panels, and committee brief generation.

## Phase Details

### Phase 6: Pre-FEED Package Foundation

**Goal:** Add the Pre-FEED package data layer that ties plants, scenarios, documents, source metadata, confidence, and missing-data warnings together.
**Mode:** mvp
**Depends on:** v1.0 Phase 5
**Requirements:** PFD-01, PFD-02, PFD-03, PFD-04, PFD-05
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can create, view, update, and archive a Pre-FEED package for a selected plant and scenario.
  2. User can assign owner, status, source organization, received date, version, `data_status`, and `confidence_level`.
  3. User can link existing uploaded documents to a package and classify document role.
  4. Package history remains auditable and does not overwrite prior scenario simulation results.
  5. Backend exposes package-level missing data and confidence warnings.
**Plans:** 3/3 plans complete

Plans:
**Wave 1**
- [x] 06-01: Pre-FEED package models, migration, schemas, seed/update safety, and document link schema.

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 06-02: Pre-FEED package REST APIs with package gap/confidence service and tests.

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 06-03: `/prefeed` package workspace shell with plant/scenario/package selection and linked document management.

**Cross-cutting constraints:**
- D-04: Existing Document records are reused; Phase 6 adds an association table rather than a new upload system.
- D-05: Package document links include relationship-level document roles.
- D-06: Document metadata and extracted text remain owned by the document layer.

### Phase 7: Cost & Vendor Proposal Engine

**Goal:** Turn Pre-FEED cost and proposal data into auditable scenario-ready assumptions and vendor comparison outputs.
**Mode:** mvp
**Depends on:** Phase 6
**Requirements:** COST-01, COST-02, COST-03, VEND-01, VEND-02, VEND-03, VEND-04
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can store CAPEX and OPEX line items with source, version, currency, contingency, escalation, and confidence.
  2. User can store EPC/vendor proposals with scope, commercial basis, validity, exclusions, and supporting documents.
  3. Backend aggregates detailed cost lines into scenario-ready assumptions without losing source package/version.
  4. User can compare vendor proposals by cost, scope completeness, missing sections, and confidence.
  5. User can select an active cost basis for a scenario while preserving previous simulation history.
**Plans:** 3/3 plans complete

Plans:
**Wave 1**
- [x] 07-01: CAPEX/OPEX line-item data model, aggregation service, and tests.

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 07-02: Vendor proposal model, gap detection, comparison service, and active package selection API.

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 07-03: Cost and vendor proposal UI with breakdown, comparison table, and active cost-basis workflow.

### Phase 8: Offtake & MRV Readiness

**Goal:** Add commercial and carbon-market readiness inputs that refine revenue assumptions and expose MRV/carbon intensity gaps.
**Mode:** mvp
**Depends on:** Phase 7
**Requirements:** OFFT-01, OFFT-02, OFFT-03, OFFT-04, MRV-01, MRV-02, MRV-03, MRV-04
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can store offtake prospects/contracts with counterparty, product, volume, term, pricing basis, status, and confidence.
  2. User can manage price decks for methanol, carbon credits, electricity, hydrogen, exchange rate, and escalation assumptions.
  3. Backend calculates scenario revenue using selected price deck/offtake assumptions through deterministic code.
  4. User can store MRV assumptions and view indicative carbon intensity/abatement values.
  5. System surfaces offtake and MRV readiness scores, carbon credit assumptions, and gaps.
**Plans:** 3/3 plans complete

Plans:
**Wave 1**
- [x] 08-01: Offtake and price deck models, APIs, deterministic revenue integration, and tests.

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 08-02: MRV assumptions, carbon intensity service, carbon credit eligibility tracking, and gap service.

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 08-03: Offtake and MRV readiness UI integrated into the Pre-FEED workspace.

### Phase 9: Risk & Pre-FEED Decision Dashboard

**Goal:** Package Pre-FEED data into a management-facing decision workspace with risk register, blockers, dashboard panels, and committee brief generation.
**Mode:** mvp
**Depends on:** Phase 8
**Requirements:** RISK-01, RISK-02, RISK-03, RISK-04, PFDASH-01, PFDASH-02, PFDASH-03, PFDASH-04, PFDASH-05
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can manage a risk register with likelihood, impact, mitigation, owner, due date, and status.
  2. Backend summarizes top risks, severity distribution, decision blockers, and next actions.
  3. User can manage decision gate checklist items across technical, commercial, legal, land, grid, offtake, MRV, and financing readiness.
  4. `/prefeed` dashboard shows package confidence, CAPEX/OPEX breakdown, vendor comparison, offtake/MRV readiness, top risks, blockers, and next actions.
  5. User can generate a Pre-FEED committee brief through the existing LLM insight layer using only stored and deterministic data.
**Plans:** 0/3 plans executed

Plans:
**Wave 1**
- [ ] 09-01: Risk register, decision gate models/APIs, blocker summary service, and tests.

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 09-02: Pre-FEED decision dashboard panels and integrated package/cost/vendor/offtake/MRV/risk view.

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 09-03: Pre-FEED committee brief LLM workflow, final v2.0 verification, and review artifacts.

**Cross-cutting constraints:**
- D-11: Blockers are generated deterministically from risks, gates, gaps, and missing active package assumptions.
- D-12: Next actions are rule-based and ordered by urgency.

## Progress

**Execution Order:**
Phases execute in numeric order: 6 -> 7 -> 8 -> 9

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. MVP Spine & Unit Data | v1.0 | 3/3 | Complete | 2026-05-16 |
| 2. Scenario Simulation Engine | v1.0 | 3/3 | Complete | 2026-05-16 |
| 3. Strategy Dashboard & Ranking | v1.0 | 3/3 | Complete | 2026-05-16 |
| 4. Investor Case & Data Quality | v1.0 | 3/3 | Complete | 2026-05-16 |
| 5. LLM & Document Intelligence | v1.0 | 3/3 | Complete | 2026-05-16 |
| 6. Pre-FEED Package Foundation | v2.0 | 3/3 | Complete | 2026-05-16 |
| 7. Cost & Vendor Proposal Engine | v2.0 | 3/3 | Complete    | 2026-05-16 |
| 8. Offtake & MRV Readiness | v2.0 | 3/3 | Complete    | 2026-05-16 |
| 9. Risk & Pre-FEED Decision Dashboard | v2.0 | 0/3 | Planned    |  |
