# Requirements: MECH WIZ AI Digital Twin

**Defined:** 2026-05-16
**Milestone:** v2.0 Pre-FEED
**Core Value:** Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.

## v2.0 Requirements

Requirements for the Pre-FEED milestone. Each requirement maps to exactly one roadmap phase.

### Pre-FEED Package Data

- [ ] **PFD-01**: User can create, view, update, and archive a Pre-FEED package linked to a plant and scenario.
- [ ] **PFD-02**: User can assign package owner, package status, source organization, received date, version, `data_status`, and `confidence_level`.
- [ ] **PFD-03**: User can link uploaded documents to a Pre-FEED package and classify them as vendor proposal, EPC estimate, offtake document, MRV document, permit document, or internal note.
- [ ] **PFD-04**: System keeps package history auditable without overwriting prior simulation or scoring results.
- [ ] **PFD-05**: System surfaces package-level missing data and confidence warnings for downstream dashboards and LLM prompts.

### CAPEX/OPEX And Vendor Proposals

- [ ] **COST-01**: User can store detailed CAPEX line items by package component, amount, currency, source, contingency, escalation, and confidence.
- [ ] **COST-02**: User can store detailed OPEX line items by cost category, amount, unit basis, recurrence, source, and confidence.
- [ ] **COST-03**: Backend can aggregate detailed CAPEX/OPEX into scenario-ready assumptions while preserving the source package and version.
- [ ] **VEND-01**: User can store EPC/vendor proposals with vendor name, scope coverage, commercial basis, delivery assumptions, exclusions, validity date, and supporting documents.
- [ ] **VEND-02**: User can compare vendor proposals by CAPEX, OPEX, scope completeness, missing sections, assumptions, and confidence.
- [ ] **VEND-03**: User can select a vendor proposal or blended package as the active Pre-FEED cost basis for a scenario.
- [ ] **VEND-04**: System flags proposal gaps such as missing electrolyzer scope, capture package, methanol plant, storage/port, grid power, land, or MRV scope.

### Offtake And Market Readiness

- [ ] **OFFT-01**: User can store offtake prospects, counterparties, product, target volume, term, pricing basis, status, and confidence.
- [ ] **OFFT-02**: User can manage market price decks for methanol, carbon credits, electricity, hydrogen, exchange rate, and escalation assumptions.
- [ ] **OFFT-03**: Backend can calculate scenario revenue using a selected price deck and offtake assumptions without using LLM calculations.
- [ ] **OFFT-04**: System calculates an offtake readiness score from counterparty status, volume coverage, term certainty, pricing clarity, and document confidence.

### MRV And Carbon Market Readiness

- [ ] **MRV-01**: User can store MRV assumptions for baseline emissions, captured CO2 accounting, methanol pathway, electricity source, carbon credit methodology, and verification status.
- [ ] **MRV-02**: Backend can calculate indicative carbon intensity and abatement values from stored MRV assumptions and deterministic scenario outputs.
- [ ] **MRV-03**: System identifies MRV data gaps and labels them by impact, priority, owner, and recommended follow-up.
- [ ] **MRV-04**: System tracks carbon credit eligibility assumptions and separates confirmed data from benchmark or user assumptions.

### Risk Register And Decision Gates

- [ ] **RISK-01**: User can create and manage a detailed risk register with category, risk statement, likelihood, impact, severity, mitigation, owner, due date, and status.
- [ ] **RISK-02**: Backend can summarize top risks and calculate risk severity distribution for the selected plant/scenario/package.
- [ ] **RISK-03**: User can manage Pre-FEED decision gate checklist items for technical, commercial, legal, land, grid, offtake, MRV, and financing readiness.
- [ ] **RISK-04**: System identifies decision blockers and required next actions before investment committee review.

### Pre-FEED Decision Dashboard

- [ ] **PFDASH-01**: User can open a Pre-FEED dashboard for a selected plant, scenario, and package.
- [ ] **PFDASH-02**: Dashboard shows CAPEX/OPEX breakdown, package confidence, missing cost items, and comparison against the v1.0 benchmark assumptions.
- [ ] **PFDASH-03**: Dashboard shows vendor comparison with proposal scope, cost, exclusions, confidence, and selected active package.
- [ ] **PFDASH-04**: Dashboard shows offtake readiness, MRV readiness, carbon intensity indicators, top risks, decision blockers, and next actions.
- [ ] **PFDASH-05**: User can generate a Pre-FEED committee brief through the existing LLM insight layer using only stored package, cost, offtake, MRV, risk, and deterministic scenario data.

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
| PFD-01 | Phase 6 | Pending |
| PFD-02 | Phase 6 | Pending |
| PFD-03 | Phase 6 | Pending |
| PFD-04 | Phase 6 | Pending |
| PFD-05 | Phase 6 | Pending |
| COST-01 | Phase 7 | Pending |
| COST-02 | Phase 7 | Pending |
| COST-03 | Phase 7 | Pending |
| VEND-01 | Phase 7 | Pending |
| VEND-02 | Phase 7 | Pending |
| VEND-03 | Phase 7 | Pending |
| VEND-04 | Phase 7 | Pending |
| OFFT-01 | Phase 8 | Pending |
| OFFT-02 | Phase 8 | Pending |
| OFFT-03 | Phase 8 | Pending |
| OFFT-04 | Phase 8 | Pending |
| MRV-01 | Phase 8 | Pending |
| MRV-02 | Phase 8 | Pending |
| MRV-03 | Phase 8 | Pending |
| MRV-04 | Phase 8 | Pending |
| RISK-01 | Phase 9 | Pending |
| RISK-02 | Phase 9 | Pending |
| RISK-03 | Phase 9 | Pending |
| RISK-04 | Phase 9 | Pending |
| PFDASH-01 | Phase 9 | Pending |
| PFDASH-02 | Phase 9 | Pending |
| PFDASH-03 | Phase 9 | Pending |
| PFDASH-04 | Phase 9 | Pending |
| PFDASH-05 | Phase 9 | Pending |

**Coverage:**
- v2.0 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0

---
*Requirements defined: 2026-05-16*
*Last updated: 2026-05-16 after v2.0 milestone initialization*
