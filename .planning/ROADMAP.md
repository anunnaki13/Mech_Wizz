# Roadmap: MECH WIZ AI Digital Twin

## Overview

The v1.0 MVP builds a usable pre-feasibility simulator in five vertical slices. It starts with a runnable app and Tenayan unit data, adds deterministic scenario calculations, turns those outputs into a Map & Heatmap Intelligence Layer with ranking and score breakdowns, packages the investment case with confidence/data-gap controls, then finishes with OpenRouter insight and document intelligence.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: MVP Spine & Unit Data** - Runnable app, database schema, seed data, and unit input workflows.
- [x] **Phase 2: Scenario Simulation Engine** - Deterministic CO2, methanol, H2, revenue, and financial calculations.
- [x] **Phase 3: Strategy Dashboard & Ranking** - MapLibre opportunity heatmap, ranking, score breakdowns, KPI dashboard, and sensitivity visualization.
- [ ] **Phase 4: Investor Case & Data Quality** - Investor dashboard, assumptions, confidence labels, and data gap engine.
- [ ] **Phase 5: LLM & Document Intelligence** - OpenRouter insights, prompt persistence, document upload, extraction, and document Q&A.

## Phase Details

### Phase 1: MVP Spine & Unit Data
**Goal:** Create a runnable full-stack app that stores Tenayan and lets users manage core unit input data.
**Mode:** mvp
**Depends on:** Nothing (first phase)
**Requirements:** PLAT-01, PLAT-02, PLAT-03, PLAT-04, DATA-01, DATA-02, DATA-03, DATA-04, DATA-08, UNIT-01, UNIT-02, UNIT-03, UNIT-04
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. Developer can start PostgreSQL, FastAPI, and Next.js locally from Docker Compose.
  2. User can open `/dashboard` and navigate to the core MVP routes.
  3. User can view seeded PLTU Tenayan data and manage plant, emission, site readiness, and hydrogen strategy records.
  4. Backend persists all Phase 1 input tables with `data_status` and `confidence_level` fields available.
**Plans:** 3 plans

Plans:
- [x] 01-01: Full-stack project scaffold, Docker Compose, environment configuration, and API shell.
- [x] 01-02: PostgreSQL schema, models, migrations, and Tenayan seed data.
- [x] 01-03: Unit input APIs and first usable unit/profile frontend views.

### Phase 2: Scenario Simulation Engine
**Goal:** Make scenarios calculable and reproducible through deterministic backend services.
**Mode:** mvp
**Depends on:** Phase 1
**Requirements:** DATA-05, DATA-06, UNIT-05, UNIT-06, CALC-01, CALC-02, CALC-03, CALC-04, CALC-05, CALC-06, CALC-07, CALC-08, CALC-09, CALC-10
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can create WIZ Access, WIZ Align, and WIZ Augment scenarios with financial assumptions.
  2. Backend calculates CO2 flow, captured CO2, e-methanol potential, H2 requirement, electrolyzer size, revenue, LCOM, NPV, IRR, and payback from stored inputs.
  3. Scenario results are saved and can be reloaded by scenario ID without recalculating in the frontend.
  4. Frontend can trigger a simulation and display the returned scenario result for the selected plant.
**Plans:** 3 plans

Plans:
- [x] 02-01: Scenario and financial assumption APIs with frontend scenario management.
- [x] 02-02: CO2, methanol, H2, revenue, LCOM, NPV, IRR, and payback calculation services with tests.
- [x] 02-03: Simulation endpoint, scenario result persistence, and frontend simulation result view.

### Phase 3: Strategy Dashboard & Ranking
**Goal:** Turn calculation results into a Map & Heatmap Intelligence Layer for site selection, ranking, score breakdowns, KPIs, and sensitivity outputs.
**Mode:** mvp
**Depends on:** Phase 2
**Requirements:** UNIT-07, DATA-09, SCORE-01, SCORE-02, SCORE-03, SCORE-04, SCORE-05, SCORE-06, SCORE-07, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, SENS-01, SENS-02, SENS-03
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can view a combined unit profile with inputs, simulation outputs, confidence, and data gaps placeholders.
  2. Backend returns GeoJSON unit opportunity features and ranking rows with opportunity, readiness, confidence, composite, heatmap weight, CO2, H2, logistics, IRR, and development readiness fields.
  3. `/dashboard/map` uses MapLibre GL JS to show an Indonesia map with heatmap, circle markers, popup/profile behavior, filters, ranking table, and score breakdowns from backend data.
  4. User can run sensitivity analysis and view tornado chart data for the selected scenario and selected unit.
**Plans:** 3 plans

Plans:
- [x] 03-01: Opportunity, readiness, confidence, composite, heatmap weight scoring, and ranking APIs.
- [x] 03-02: `/dashboard/map` MapLibre heatmap, unit markers, filters, ranking table, selected profile, and score breakdown UI.
- [x] 03-03: Sensitivity engine, sensitivity result persistence, tornado chart visualization, and map detail integration.

### Phase 4: Investor Case & Data Quality
**Goal:** Package the simulation into an investor-ready case while making assumptions, confidence, and data gaps visible.
**Mode:** mvp
**Depends on:** Phase 3
**Requirements:** INV-01, INV-02, INV-03, INV-04, QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can open `/investor` for a selected plant/scenario and review investor KPIs, thesis flow, revenue mix, scenario comparison, risk mitigation, scale roadmap, and why-this-wins content.
  2. Important inputs expose allowed `data_status` values and important outputs expose allowed `confidence_level` values.
  3. Missing data uses editable default assumptions, marks low-confidence results where appropriate, and produces data gap recommendations.
  4. User can edit default assumptions and scoring weights from settings.
**Plans:** 3 plans

Plans:
- [ ] 04-01: Investor dashboard API and investor-facing data aggregation.
- [ ] 04-02: Investor dashboard UI with KPIs, thesis flow, revenue mix, scenario comparison, risks, roadmap, and win narrative.
- [ ] 04-03: Data status validation, confidence engine, data gap engine, and editable assumptions/settings.

### Phase 5: LLM & Document Intelligence
**Goal:** Add OpenRouter narrative insight and lightweight document intelligence while preserving deterministic numeric authority.
**Mode:** mvp
**Depends on:** Phase 4
**Requirements:** DATA-07, LLM-01, LLM-02, LLM-03, LLM-04, LLM-05, LLM-06, LLM-07, DOC-01, DOC-02, DOC-03, DOC-04, SENS-04
**UI hint:** yes
**Success Criteria** (what must be TRUE):
  1. User can generate executive summary, data gap explanation, investor memo, and sensitivity explanation through OpenRouter.
  2. Every LLM prompt and response is stored with insight type, model name, and scenario reference.
  3. LLM prompts separate actual data, assumptions, confidence, and gaps and instruct the model not to invent numbers.
  4. User can upload PDF/Excel documents, extract text, and ask basic document questions.
**Plans:** 3 plans

Plans:
- [ ] 05-01: OpenRouter service, prompt templates, response persistence, and LLM guardrails.
- [ ] 05-02: Executive summary, data gap explanation, investor memo, and sensitivity explanation workflows in the UI.
- [ ] 05-03: Document upload, extraction, repository view, and basic document Q&A.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. MVP Spine & Unit Data | 3/3 | Complete | 2026-05-16 |
| 2. Scenario Simulation Engine | 3/3 | Complete | 2026-05-16 |
| 3. Strategy Dashboard & Ranking | 3/3 | Complete | 2026-05-16 |
| 4. Investor Case & Data Quality | 0/3 | Not started | - |
| 5. LLM & Document Intelligence | 0/3 | Not started | - |
