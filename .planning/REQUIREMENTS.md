# Requirements: MECH WIZ AI Digital Twin

**Defined:** 2026-05-16
**Core Value:** Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.

## v1 Requirements

Requirements for the initial MVP. Each requirement maps to exactly one roadmap phase.

### Platform

- [ ] **PLAT-01**: Developer can run the full app locally with Docker Compose, including PostgreSQL, FastAPI backend, and Next.js frontend.
- [ ] **PLAT-02**: Developer can configure database, OpenRouter, frontend URL, backend URL, JWT secret, and upload directory through environment variables and `.env.example`.
- [ ] **PLAT-03**: Backend exposes a versioned REST/JSON API under `/api`.
- [ ] **PLAT-04**: Frontend redirects `/` to `/dashboard` and provides routes for dashboard, units, scenarios, investor, sensitivity, documents, and settings.

### Data Model

- [ ] **DATA-01**: System stores plant/unit records with location, capacity, fuel, operating profile, owner, `data_status`, and `confidence_level`.
- [ ] **DATA-02**: System stores emission test records with stack dimensions, gas velocity, temperature, CO2, O2, moisture, SO2, NOx, particulate, Hg, compliance status, `data_status`, and `confidence_level`.
- [ ] **DATA-03**: System stores site readiness records with land, port/logistics, road, water, power, utility, permit, social risk, `data_status`, and `confidence_level`.
- [ ] **DATA-04**: System stores hydrogen strategy records with existing H2 availability, strategy, cost case, H2 cost, readiness score, `data_status`, and `confidence_level`.
- [ ] **DATA-05**: System stores financial assumption records for methanol price, grey methanol price, hydrogen price, electricity price, carbon credit price, exchange rate, discount rate, tax rate, CAPEX fields, OPEX percentage, `data_status`, and `confidence_level`.
- [ ] **DATA-06**: System stores business scenarios for WIZ Access, WIZ Align, and WIZ Augment with ownership, CAPEX responsibility, revenue model, `data_status`, and `confidence_level`.
- [ ] **DATA-07**: System stores simulation results, sensitivity results, uploaded documents, and LLM insight records so outputs are reproducible and auditable.
- [ ] **DATA-08**: System seeds PLTU Tenayan with the blueprint sample plant and chimney data.
- [ ] **DATA-09**: System stores map/scoring output records with opportunity score, readiness score, confidence score, composite score, heatmap weight, rank position, data gap count, and scoring version.

### Unit Inputs

- [ ] **UNIT-01**: User can create, view, update, and delete plant/unit records.
- [ ] **UNIT-02**: User can create, view, update, and delete emission test records for a plant.
- [ ] **UNIT-03**: User can create, view, and update site readiness records for a plant.
- [ ] **UNIT-04**: User can create, view, and update hydrogen strategy records for a plant.
- [ ] **UNIT-05**: User can create, view, and update financial assumptions for a scenario.
- [ ] **UNIT-06**: User can create, view, update, and delete business scenarios.
- [ ] **UNIT-07**: User can view a unit profile that combines plant, emission, readiness, hydrogen, assumptions, simulation outputs, confidence, and data gaps.

### Calculation Engine

- [ ] **CALC-01**: Backend calculates stack area from stack diameter.
- [ ] **CALC-02**: Backend calculates normalized gas flow from velocity, stack area, and flue gas temperature.
- [ ] **CALC-03**: Backend calculates wet-basis CO2 fraction from dry CO2 percentage and moisture.
- [ ] **CALC-04**: Backend calculates CO2 kg/s, CO2 ton/day, and CO2 ton/year.
- [ ] **CALC-05**: Backend calculates captured CO2 and vented CO2 from total CO2 and capture rate.
- [ ] **CALC-06**: Backend calculates theoretical and actual e-methanol production from captured CO2 and process efficiency.
- [ ] **CALC-07**: Backend calculates H2 requirement and indicative electrolyzer size.
- [ ] **CALC-08**: Backend calculates gross revenue from methanol revenue, carbon credit revenue, and asset revenue.
- [ ] **CALC-09**: Backend calculates indicative LCOM, NPV, IRR, and payback period.
- [ ] **CALC-10**: Backend persists scenario results and can return them by scenario ID.

### Scoring And Ranking

- [ ] **SCORE-01**: Backend calculates opportunity score using weighted CO2 availability, methanol potential, market/logistics, land availability, utility advantage, carbon credit potential, and strategic value.
- [ ] **SCORE-02**: Backend calculates readiness score using weighted data completeness, emission data quality, land readiness, utility readiness, H2 strategy clarity, and permit/logistics readiness.
- [ ] **SCORE-03**: Backend calculates composite score as 45% opportunity score, 35% readiness score, and 20% confidence score.
- [ ] **SCORE-04**: User can request unit ranking with composite score, CO2 availability, H2 readiness, logistics, IRR potential, and development readiness.
- [ ] **SCORE-05**: Dashboard can consume heatmap-ready ranking data for map markers and opportunity coloring.
- [ ] **SCORE-06**: Backend calculates confidence score from required data field status using addendum weights for `actual`, `estimated`, `benchmark`, `user_assumption`, `partner_supplied`, and `unknown`.
- [ ] **SCORE-07**: Backend calculates normalized heatmap weight from opportunity, readiness, economic return, and confidence scores for map rendering.

### Strategy Dashboard

- [ ] **DASH-01**: User can view a strategy overview dashboard with header, sidebar, scenario selector, KPI cards, Indonesia map/heatmap panel, ranking table, score breakdown, sensitivity panel, and insight panel.
- [ ] **DASH-02**: Dashboard KPI cards show best selected site, estimated IRR, LCOM, captured CO2, e-methanol potential, and CAPEX model from backend data.
- [ ] **DASH-03**: Dashboard map shows plant markers and opportunity intensity, with the top-ranked unit visually highlighted.
- [ ] **DASH-04**: Dashboard ranking table shows rank, unit/site, composite score, CO2 availability, H2 readiness, logistics, IRR potential, and development readiness.
- [ ] **DASH-05**: Dashboard shows score breakdown across CO2 availability, H2 readiness, logistics, IRR potential, development readiness, and infrastructure readiness.
- [ ] **DASH-06**: `/dashboard/map` renders a MapLibre GL JS Indonesia map from a GeoJSON unit opportunity endpoint with heatmap, circle marker, and popup/profile layers.
- [ ] **DASH-07**: Map controls filter scenario, business scheme, region, fuel type, data confidence, opportunity level, and visible layers while keeping the map and ranking table synchronized.

### Investor Dashboard

- [ ] **INV-01**: User can view an investor dashboard for a selected plant and scenario.
- [ ] **INV-02**: Investor dashboard shows project IRR, estimated NPV, LCOM, payback period, e-methanol capacity, CO2 abatement, and CAPEX structure.
- [ ] **INV-03**: Investor dashboard shows an investment thesis flow from assets and advantages to partner solution, market access, and output/value.
- [ ] **INV-04**: Investor dashboard shows revenue mix, WIZ Access / WIZ Align / WIZ Augment scenario comparison, risk and mitigation, roadmap to scale, and why this project wins.

### Sensitivity Analysis

- [ ] **SENS-01**: Backend runs sensitivity analysis for H2 price, electricity price, methanol price, CAPEX, capture rate, plant availability, carbon credit price, and exchange rate.
- [ ] **SENS-02**: Backend stores IRR low/high, NPV low/high, LCOM low/high, and impact score for each sensitivity variable.
- [ ] **SENS-03**: User can view tornado chart data and identify the dominant sensitivity driver for a scenario.
- [ ] **SENS-04**: User can view sensitivity explanations tied only to stored sensitivity values.

### Data Quality And Assumptions

- [ ] **QUAL-01**: Every important input exposes a `data_status` field with allowed values `actual`, `estimated`, `benchmark`, `user_assumption`, `unknown`, or `partner_supplied`.
- [ ] **QUAL-02**: Every important output exposes a `confidence_level` field with allowed values `high`, `medium`, `low`, or `unknown`.
- [ ] **QUAL-03**: System applies editable default assumptions when required data is missing.
- [ ] **QUAL-04**: System marks outputs as low confidence when they rely mostly on benchmark or assumption data.
- [ ] **QUAL-05**: System generates data gaps with missing data name, impact, priority, and recommendation for unit profiles, investor dashboard, and LLM summaries.
- [ ] **QUAL-06**: User can edit default assumptions and scoring weights from settings.

### LLM Insight

- [ ] **LLM-01**: Backend integrates with OpenRouter using configurable API key and model.
- [ ] **LLM-02**: User can generate an executive summary for a scenario using stored simulation result, data gaps, and scenario data.
- [ ] **LLM-03**: User can generate a data gap explanation for a plant using stored unit and simulation data.
- [ ] **LLM-04**: User can generate an investor memo for a scenario using stored dashboard data.
- [ ] **LLM-05**: User can generate a sensitivity explanation using stored sensitivity results.
- [ ] **LLM-06**: System stores every LLM prompt, response, model name, insight type, and scenario reference.
- [ ] **LLM-07**: LLM prompts instruct the model not to invent numbers and to separate actual data, assumptions, confidence, and gaps.

### Documents

- [ ] **DOC-01**: User can upload PDF and Excel documents and associate them with a plant when relevant.
- [ ] **DOC-02**: System stores document metadata, storage path, category, upload status, and extracted text.
- [ ] **DOC-03**: User can trigger text extraction for an uploaded document.
- [ ] **DOC-04**: User can ask basic questions about an uploaded document through the document intelligence layer.

## v2 Requirements

Deferred to later releases. Tracked but not in the initial MVP roadmap.

### Pre-FEED Digital Twin

- **PFEED-01**: System supports detailed CAPEX/OPEX from partner proposals and pre-FEED studies.
- **PFEED-02**: System compares vendor EPC proposals and offtake readiness.
- **PFEED-03**: System manages a detailed risk register and mitigation tracking.
- **PFEED-04**: System supports MRV module requirements for carbon intensity and carbon markets.

### Operational Digital Twin

- **OPS-01**: System connects to DCS/SCADA or plant historian data.
- **OPS-02**: System supports real-time process optimization.
- **OPS-03**: System supports predictive maintenance workflows.
- **OPS-04**: System supports live MRV and production optimization.

## Out of Scope

Explicitly excluded from the MVP to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time DCS/SCADA integration | MVP is pre-feasibility, not operational digital twin |
| FEED-grade financial model | MVP is indicative screening and must label assumptions clearly |
| Mandatory reactor, hydrogen plant, EPC, FEED, CAPEX, or offtake data | Product must work before those data sources exist |
| LLM as calculator | Backend calculation engine is the numeric source of truth |
| Native mobile app | First target is web dashboard |
| Full MRV and predictive maintenance | Future v2/v3 scope |

## Traceability

Each v1 requirement maps to exactly one roadmap phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PLAT-01 | Phase 1 | Pending |
| PLAT-02 | Phase 1 | Pending |
| PLAT-03 | Phase 1 | Pending |
| PLAT-04 | Phase 1 | Pending |
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 2 | Pending |
| DATA-06 | Phase 2 | Pending |
| DATA-07 | Phase 5 | Pending |
| DATA-08 | Phase 1 | Pending |
| DATA-09 | Phase 3 | Pending |
| UNIT-01 | Phase 1 | Pending |
| UNIT-02 | Phase 1 | Pending |
| UNIT-03 | Phase 1 | Pending |
| UNIT-04 | Phase 1 | Pending |
| UNIT-05 | Phase 2 | Pending |
| UNIT-06 | Phase 2 | Pending |
| UNIT-07 | Phase 3 | Pending |
| CALC-01 | Phase 2 | Pending |
| CALC-02 | Phase 2 | Pending |
| CALC-03 | Phase 2 | Pending |
| CALC-04 | Phase 2 | Pending |
| CALC-05 | Phase 2 | Pending |
| CALC-06 | Phase 2 | Pending |
| CALC-07 | Phase 2 | Pending |
| CALC-08 | Phase 2 | Pending |
| CALC-09 | Phase 2 | Pending |
| CALC-10 | Phase 2 | Pending |
| SCORE-01 | Phase 3 | Pending |
| SCORE-02 | Phase 3 | Pending |
| SCORE-03 | Phase 3 | Pending |
| SCORE-04 | Phase 3 | Pending |
| SCORE-05 | Phase 3 | Pending |
| SCORE-06 | Phase 3 | Pending |
| SCORE-07 | Phase 3 | Pending |
| DASH-01 | Phase 3 | Pending |
| DASH-02 | Phase 3 | Pending |
| DASH-03 | Phase 3 | Pending |
| DASH-04 | Phase 3 | Pending |
| DASH-05 | Phase 3 | Pending |
| DASH-06 | Phase 3 | Pending |
| DASH-07 | Phase 3 | Pending |
| INV-01 | Phase 4 | Pending |
| INV-02 | Phase 4 | Pending |
| INV-03 | Phase 4 | Pending |
| INV-04 | Phase 4 | Pending |
| SENS-01 | Phase 3 | Pending |
| SENS-02 | Phase 3 | Pending |
| SENS-03 | Phase 3 | Pending |
| SENS-04 | Phase 5 | Pending |
| QUAL-01 | Phase 4 | Pending |
| QUAL-02 | Phase 4 | Pending |
| QUAL-03 | Phase 4 | Pending |
| QUAL-04 | Phase 4 | Pending |
| QUAL-05 | Phase 4 | Pending |
| QUAL-06 | Phase 4 | Pending |
| LLM-01 | Phase 5 | Pending |
| LLM-02 | Phase 5 | Pending |
| LLM-03 | Phase 5 | Pending |
| LLM-04 | Phase 5 | Pending |
| LLM-05 | Phase 5 | Pending |
| LLM-06 | Phase 5 | Pending |
| LLM-07 | Phase 5 | Pending |
| DOC-01 | Phase 5 | Pending |
| DOC-02 | Phase 5 | Pending |
| DOC-03 | Phase 5 | Pending |
| DOC-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 69 total
- Mapped to phases: 69
- Unmapped: 0

---
*Requirements defined: 2026-05-16*
*Last updated: 2026-05-16 after heatmap map addendum import*
