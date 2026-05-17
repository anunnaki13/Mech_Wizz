# Requirements: MECH WIZ AI Digital Twin

**Defined:** 2026-05-16
**Milestone:** v2.5 Workflow UX Audit & Simplification Plan
**Core Value:** Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.

## v2.5 Requirements

Requirements for the workflow audit milestone. Each requirement maps to Phase 14.

### Workflow UX Audit

- [x] **UXA-01**: Audit all primary frontend routes for runtime reachability.
- [x] **UXA-02**: Audit key backend APIs for runtime reachability.
- [x] **UXA-03**: Inventory button, link, and form complexity by main route.
- [x] **UXA-04**: Identify workflow friction for non-technical operators.
- [x] **UXA-05**: Produce a prioritized simplification plan for the next phase.

## v2.4 Requirements

Requirements for the pilot decision milestone. Each requirement maps to Phase 13.

### Pilot Decision Dashboard

- [x] **PDEC-01**: Backend can generate a pilot decision dashboard from Top 3 shortlist and evidence workspace data.
- [x] **PDEC-02**: System calculates evidence-adjusted decision score without mutating stored shortlist rank.
- [x] **PDEC-03**: System labels candidates as `committee_ready`, `needs_evidence`, or `blocked` using deterministic evidence gates.
- [x] **PDEC-04**: System surfaces candidate blockers and next actions from high-priority open or rejected evidence.
- [x] **PDEC-05**: Frontend exposes `/pilot-decision` with lead recommendation, comparison cards, blockers, methodology, and action plan.

## v2.3 Requirements

Requirements for the evidence collection milestone. Each requirement maps to Phase 12.

### Evidence Collection Workspace

- [x] **EVID-01**: Backend persists validation evidence records by plant, scenario, category, and evidence key.
- [x] **EVID-02**: Evidence records support status lifecycle values `missing`, `requested`, `received`, `verified`, and `rejected`.
- [x] **EVID-03**: Backend can generate a Top 3 evidence workspace by merging Phase 11 checklist defaults with persisted records.
- [x] **EVID-04**: System calculates evidence readiness score, status mix, verified item count, and high-priority unresolved gaps from stored statuses.
- [x] **EVID-05**: Frontend exposes `/evidence` for editing and saving evidence status and metadata.

## v2.2 Requirements

Requirements for the Top 3 validation pack milestone. Each requirement maps to Phase 11.

### Top 3 Validation Pack And Committee Memo

- [x] **VALP-01**: Backend can generate a Top 3 validation pack from current shortlist results.
- [x] **VALP-02**: System produces evidence checklist items across technical, economics, logistics, power/H2, commercial, and MRV categories.
- [x] **VALP-03**: System produces comparison axes, decision questions, no-go triggers, caveats, and a deterministic committee memo.
- [x] **VALP-04**: Backend exposes a PDF endpoint for the committee memo.
- [x] **VALP-05**: Frontend exposes `/validation-pack` for management review and PDF access.

## v2.1 Requirements

Requirements for the shortlist validation milestone. Each requirement maps to Phase 10.

### Economic Calibration And Shortlist Validation

- [x] **ECAL-01**: Backend can generate a shortlist decision matrix from current scoring, simulation economics, port/logistics intelligence, confidence, and data gaps.
- [x] **ECAL-02**: System separates score components for screening, economics, logistics, confidence, and final shortlist score.
- [x] **ECAL-03**: System labels candidates as Top 3, Top 5, or watchlist with decision rationale and next validation actions.
- [x] **ECAL-04**: Frontend exposes a `/shortlist` page for management review of Top 3/Top 5 candidates.
- [x] **ECAL-05**: System states caveats that shortlist results are screening outputs and require PLN/site/vendor/port confirmation.

## v2.0 Requirements

Requirements for the Pre-FEED milestone. Each requirement maps to exactly one roadmap phase.

### Pre-FEED Package Data

- [x] **PFD-01**: User can create, view, update, and archive a Pre-FEED package linked to a plant and scenario.
- [x] **PFD-02**: User can assign package owner, package status, source organization, received date, version, `data_status`, and `confidence_level`.
- [x] **PFD-03**: User can link uploaded documents to a Pre-FEED package and classify them as vendor proposal, EPC estimate, offtake document, MRV document, permit document, or internal note.
- [x] **PFD-04**: System keeps package history auditable without overwriting prior simulation or scoring results.
- [x] **PFD-05**: System surfaces package-level missing data and confidence warnings for downstream dashboards and LLM prompts.

### CAPEX/OPEX And Vendor Proposals

- [x] **COST-01**: User can store detailed CAPEX line items by package component, amount, currency, source, contingency, escalation, and confidence.
- [x] **COST-02**: User can store detailed OPEX line items by cost category, amount, unit basis, recurrence, source, and confidence.
- [x] **COST-03**: Backend can aggregate detailed CAPEX/OPEX into scenario-ready assumptions while preserving the source package and version.
- [x] **VEND-01**: User can store EPC/vendor proposals with vendor name, scope coverage, commercial basis, delivery assumptions, exclusions, validity date, and supporting documents.
- [x] **VEND-02**: User can compare vendor proposals by CAPEX, OPEX, scope completeness, missing sections, assumptions, and confidence.
- [x] **VEND-03**: User can select a vendor proposal or blended package as the active Pre-FEED cost basis for a scenario.
- [x] **VEND-04**: System flags proposal gaps such as missing electrolyzer scope, capture package, methanol plant, storage/port, grid power, land, or MRV scope.

### Offtake And Market Readiness

- [x] **OFFT-01**: User can store offtake prospects, counterparties, product, target volume, term, pricing basis, status, and confidence.
- [x] **OFFT-02**: User can manage market price decks for methanol, carbon credits, electricity, hydrogen, exchange rate, and escalation assumptions.
- [x] **OFFT-03**: Backend can calculate scenario revenue using a selected price deck and offtake assumptions without using LLM calculations.
- [x] **OFFT-04**: System calculates an offtake readiness score from counterparty status, volume coverage, term certainty, pricing clarity, and document confidence.

### MRV And Carbon Market Readiness

- [x] **MRV-01**: User can store MRV assumptions for baseline emissions, captured CO2 accounting, methanol pathway, electricity source, carbon credit methodology, and verification status.
- [x] **MRV-02**: Backend can calculate indicative carbon intensity and abatement values from stored MRV assumptions and deterministic scenario outputs.
- [x] **MRV-03**: System identifies MRV data gaps and labels them by impact, priority, owner, and recommended follow-up.
- [x] **MRV-04**: System tracks carbon credit eligibility assumptions and separates confirmed data from benchmark or user assumptions.

### Risk Register And Decision Gates

- [x] **RISK-01**: User can create and manage a detailed risk register with category, risk statement, likelihood, impact, severity, mitigation, owner, due date, and status.
- [x] **RISK-02**: Backend can summarize top risks and calculate risk severity distribution for the selected plant/scenario/package.
- [x] **RISK-03**: User can manage Pre-FEED decision gate checklist items for technical, commercial, legal, land, grid, offtake, MRV, and financing readiness.
- [x] **RISK-04**: System identifies decision blockers and required next actions before investment committee review.

### Pre-FEED Decision Dashboard

- [x] **PFDASH-01**: User can open a Pre-FEED dashboard for a selected plant, scenario, and package.
- [x] **PFDASH-02**: Dashboard shows CAPEX/OPEX breakdown, package confidence, missing cost items, and comparison against the v1.0 benchmark assumptions.
- [x] **PFDASH-03**: Dashboard shows vendor comparison with proposal scope, cost, exclusions, confidence, and selected active package.
- [x] **PFDASH-04**: Dashboard shows offtake readiness, MRV readiness, carbon intensity indicators, top risks, decision blockers, and next actions.
- [x] **PFDASH-05**: User can generate a Pre-FEED committee brief through the existing LLM insight layer using only stored package, cost, offtake, MRV, risk, and deterministic scenario data.

## Future Requirements

Deferred to later releases. Tracked but not in the current v2.0 roadmap.

### Document Intelligence Expansion

- **DOCX-01**: System can run OCR on scanned PDFs and image-only documents.
- **DOCX-02**: System can index long documents with vector retrieval for multi-document Q&A.
- **DOCX-03**: System can extract structured cost tables from vendor proposal documents into reviewable draft line items.

### Production Readiness

- **PROD-01**: System has VPS/Nginx/HTTPS deployment hardening with backup and restore procedures.
- **PROD-02**: System has observability for backend errors, LLM usage, document extraction failures, and long-running jobs.
- **PROD-03**: Map dashboard uses a controlled production tile provider or hosted style.

### Operational Digital Twin

- **OPS-01**: System connects to DCS/SCADA or plant historian data.
- **OPS-02**: System supports real-time process optimization.
- **OPS-03**: System supports predictive maintenance workflows.
- **OPS-04**: System supports live MRV and production optimization.

## Out of Scope

Explicitly excluded from the Pre-FEED milestone to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time DCS/SCADA integration | v2.0 remains a Pre-FEED decision workflow, not operational plant control |
| Automatic legal or financing approval | The app can surface readiness and blockers, but approval remains a human governance process |
| LLM-generated financial calculations | Deterministic backend calculations remain the numeric source of truth |
| OCR/vector RAG implementation | Document extraction expansion is tracked separately to keep v2.0 focused on Pre-FEED workflows |
| Production infrastructure hardening | Important, but separate from the functional Pre-FEED product milestone |

## Traceability

Each v2.0 requirement maps to exactly one roadmap phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PFD-01 | Phase 6 | Complete |
| PFD-02 | Phase 6 | Complete |
| PFD-03 | Phase 6 | Complete |
| PFD-04 | Phase 6 | Complete |
| PFD-05 | Phase 6 | Complete |
| COST-01 | Phase 7 | Complete |
| COST-02 | Phase 7 | Complete |
| COST-03 | Phase 7 | Complete |
| VEND-01 | Phase 7 | Complete |
| VEND-02 | Phase 7 | Complete |
| VEND-03 | Phase 7 | Complete |
| VEND-04 | Phase 7 | Complete |
| OFFT-01 | Phase 8 | Complete |
| OFFT-02 | Phase 8 | Complete |
| OFFT-03 | Phase 8 | Complete |
| OFFT-04 | Phase 8 | Complete |
| MRV-01 | Phase 8 | Complete |
| MRV-02 | Phase 8 | Complete |
| MRV-03 | Phase 8 | Complete |
| MRV-04 | Phase 8 | Complete |
| RISK-01 | Phase 9 | Complete |
| RISK-02 | Phase 9 | Complete |
| RISK-03 | Phase 9 | Complete |
| RISK-04 | Phase 9 | Complete |
| PFDASH-01 | Phase 9 | Complete |
| PFDASH-02 | Phase 9 | Complete |
| PFDASH-03 | Phase 9 | Complete |
| PFDASH-04 | Phase 9 | Complete |
| PFDASH-05 | Phase 9 | Complete |
| ECAL-01 | Phase 10 | Complete |
| ECAL-02 | Phase 10 | Complete |
| ECAL-03 | Phase 10 | Complete |
| ECAL-04 | Phase 10 | Complete |
| ECAL-05 | Phase 10 | Complete |
| VALP-01 | Phase 11 | Complete |
| VALP-02 | Phase 11 | Complete |
| VALP-03 | Phase 11 | Complete |
| VALP-04 | Phase 11 | Complete |
| VALP-05 | Phase 11 | Complete |
| EVID-01 | Phase 12 | Complete |
| EVID-02 | Phase 12 | Complete |
| EVID-03 | Phase 12 | Complete |
| EVID-04 | Phase 12 | Complete |
| EVID-05 | Phase 12 | Complete |
| PDEC-01 | Phase 13 | Complete |
| PDEC-02 | Phase 13 | Complete |
| PDEC-03 | Phase 13 | Complete |
| PDEC-04 | Phase 13 | Complete |
| PDEC-05 | Phase 13 | Complete |
| UXA-01 | Phase 14 | Complete |
| UXA-02 | Phase 14 | Complete |
| UXA-03 | Phase 14 | Complete |
| UXA-04 | Phase 14 | Complete |
| UXA-05 | Phase 14 | Complete |

**Coverage:**
- v2.0 requirements: 29 total, complete
- v2.1 requirements: 5 total, complete
- v2.2 requirements: 5 total, complete
- v2.3 requirements: 5 total, complete
- v2.4 requirements: 5 total, complete
- v2.5 requirements: 5 total, complete
- Mapped to phases: 54
- Unmapped: 0

---
*Requirements defined: 2026-05-16*
*Last updated: 2026-05-17 after v2.5 Phase 14 audit*
