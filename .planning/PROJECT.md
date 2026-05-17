# MECH WIZ AI Digital Twin

## What This Is

MECH WIZ AI Digital Twin is a web-based pre-feasibility simulation and decision-support engine for identifying PLN NP power generation units that are suitable candidates for e-methanol / carbon-to-fuel projects. It combines unit mapping, deterministic technical and financial calculations, scoring, ranking, sensitivity analysis, data confidence tracking, data gap analysis, investor-facing dashboards, OpenRouter-backed narrative insight, and lightweight document intelligence.

This is not a real-time operational digital twin connected to DCS/SCADA. The shipped v1.0 MVP is an assumption-driven simulator that works with incomplete early-stage data by using explicit assumptions, confidence levels, and visible data gaps.

## Core Value

Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.

## Current State

**Shipped version:** v2.0 Pre-FEED on 2026-05-17
**Audit:** v1.0 PASS, v2.0 implementation verified through phase tests and dashboards
**Current focus:** v2.1 Economic Calibration & Shortlist Validation

The current app includes:

- FastAPI backend, PostgreSQL/Docker Compose configuration, Alembic migrations, and Tenayan seed data.
- Next.js dashboard shell with routes for `/dashboard`, `/dashboard/map`, `/units`, `/scenarios`, `/investor`, `/sensitivity`, `/documents`, and `/settings`.
- Deterministic scenario simulation for CO2, captured CO2, e-methanol, H2, revenue, LCOM, NPV, IRR, payback, and stored scenario results.
- MapLibre strategy dashboard with GeoJSON opportunity map, heatmap/marker layers, ranking table, score breakdowns, and sensitivity view.
- Investor case dashboard backed by deterministic aggregate data, null-safe economics, CAPEX structure, revenue mix, risks, roadmap, and data gaps.
- Persisted settings and data quality workflows for default assumptions, scoring weights, confidence labels, and gap recommendations.
- OpenRouter insight workflows with backend-only API key configuration, stored prompt/response records, and prompt guardrails.
- Document upload, metadata, text extraction for supported formats, repository browsing, extracted text preview, and document Q&A.

Known runtime caveats:

- Live LLM generation requires `OPENROUTER_API_KEY`.
- Seeded Tenayan CAPEX remains intentionally incomplete, so IRR/NPV/LCOM/payback can be `null` until real assumptions are entered.
- PDF extraction is text-layer only; scanned PDFs need OCR in a later milestone.
- Public OSM raster tiles are acceptable for MVP but production should use a controlled tile provider.

## Current Milestone: v2.1 Economic Calibration & Shortlist Validation

**Goal:** Convert the 26-site PLTU screening dataset into a decision-oriented Top 3/Top 5 shortlist using deterministic economics, logistics, confidence, and data-gap scoring.

**Target features:**

- Shortlist decision matrix that combines existing ranking, simulation economics, port proximity/readiness, confidence, and data gaps.
- Top 3/Top 5/watchlist recommendations with clear rationale and next validation actions.
- Management-facing `/shortlist` page linked from the dashboard and navigation.
- Explicit caveats that the shortlist is still screening/pre-validation, not final investment approval.

## Requirements

### Validated

- [x] Provide a working web dashboard for strategy overview, unit mapping, ranking, KPI review, scoring, sensitivity, and insight - v1.0.
- [x] Store and manage power plant unit profile data, emission test data, site readiness data, hydrogen strategy data, financial assumptions, business scenarios, simulation results, sensitivity results, documents, and LLM insight records - v1.0.
- [x] Calculate CO2 flow, captured CO2, e-methanol potential, H2 requirement, electrolyzer size, revenue, LCOM, NPV, IRR, payback, opportunity score, readiness score, composite score, and sensitivity impacts through deterministic backend code - v1.0.
- [x] Track `data_status` for important inputs and `confidence_level` for important outputs - v1.0.
- [x] Run with incomplete data by applying editable default assumptions, marking low-confidence outputs, and surfacing data gaps with recommended follow-up actions - v1.0.
- [x] Compare WIZ Access, WIZ Align, and WIZ Augment business schemes - v1.0.
- [x] Present an investor-friendly dashboard with selected pilot site, indicative IRR, NPV, LCOM, payback, CAPEX structure, revenue mix, scenario comparison, risk mitigation, scale roadmap, and investment thesis - v1.0.
- [x] Use OpenRouter-backed LLM features only for explanation, summaries, investor memos, risk narratives, data gap explanation, sensitivity explanation, document Q&A, and document extraction support - v1.0.
- [x] Prevent the LLM from being the source of record for technical or financial calculations - v1.0.
- [x] Seed the MVP with the Tenayan sample data from the blueprint - v1.0.
- [x] Add Pre-FEED package, cost/vendor, offtake/MRV, risk/decision, and committee-brief workflows - v2.0.
- [x] Replace broad public screening with the 26 requested target PLTU dataset and dashboard report summary - v2.0 follow-up.

### Active

- [ ] Build a shortlist decision matrix for Top 3/Top 5 validation.
- [ ] Expose economics/logistics/confidence score breakdowns for every shortlisted site.
- [ ] Show next validation actions per candidate before deeper PLN/vendor work.

### Candidate Next Requirements

- [ ] Add OCR and retrieval for scanned or long documents.
- [ ] Harden deployment for VPS/Nginx/HTTPS, backup, observability, and controlled map tiles.
- [ ] Validate live OpenRouter generation with production credentials and usage limits.

### Out of Scope

- Real-time DCS/SCADA/historian integration - this belongs to a later operational digital twin phase.
- Detailed FEED-grade CAPEX/OPEX modelling - deferred beyond v1.0 because MVP is pre-feasibility and labels indicative results clearly.
- Reactor methanol, hydrogen plant, EPC vendor, partner proposal, offtake contract, and final financing data as mandatory inputs - the v1.0 MVP must operate before those are available.
- LLM-generated numerical calculations - deterministic backend calculations remain the authoritative source.
- Native mobile application - dashboard web app is the first delivery target.
- Full MRV, predictive maintenance, and production optimization - deferred to future v2/v3 roadmap.

## Context

The source blueprint is `MECH_WIZ_AI_Digital_Twin_Blueprint.md` from `https://github.com/anunnaki13/Mech_Wizz`, version v1.0 MVP / Pre-Feasibility Mode. The map/scoring source addendum is `MECH_WIZ_Heatmap_Map_Addendum.md`, imported locally at `docs/MECH_WIZ_Heatmap_Map_Addendum.md`. The target users are Business Development, MMRK, Engineering, PLN NP management, potential partners, and investors.

The two main product outputs are:

1. Unit Mapping & Economic Site Selection: map, opportunity heatmap, unit scoring, ranking, opportunity score, readiness score, composite score, CO2 potential, H2 gap estimator, e-methanol potential, sensitivity analysis, data confidence, and data gap analysis.
2. Investor-Friendly Dashboard: investment thesis, selected pilot site, indicative IRR, indicative NPV, indicative LCOM, indicative payback, CAPEX structure, revenue mix, WIZ Access / WIZ Align / WIZ Augment scenario comparison, key risks and mitigation, roadmap to scale, why the project wins, and AI-generated investor summary.

The product is positioned as a combination of:

- Calculation engine for CO2, H2, e-methanol, LCOM, IRR, NPV, payback, scoring, and sensitivity.
- Decision-support engine for choosing the strongest unit and business scenario.
- Assumption-driven simulator for incomplete data conditions.
- LLM insight layer for explanation and narrative output.
- Document intelligence layer for PDF, Excel, proposal, market report, emission report, and internal document handling.

Current architecture:

- Frontend: Next.js, React, TypeScript, MapLibre GL JS, CSS modules/global CSS patterns, and dashboard components.
- Backend: FastAPI, Python, SQLAlchemy, Alembic, deterministic calculation services, and direct OpenRouter HTTP integration.
- Database: PostgreSQL for Docker Compose, SQLite-compatible tests/migrations for local verification.
- Storage: local upload directory for MVP document files.
- Deployment target: VPS with Docker Compose, Nginx reverse proxy, HTTPS via Certbot, PostgreSQL, FastAPI container, Next.js container, and optional worker container.

## Constraints

- **Calculation Authority**: Deterministic backend code must calculate all technical and financial outputs. LLM must not invent or calculate source-of-record numbers.
- **Data Status**: Important inputs must carry `data_status` values: `actual`, `estimated`, `benchmark`, `user_assumption`, `unknown`, or `partner_supplied`.
- **Confidence**: Important outputs must carry `confidence_level` values: `high`, `medium`, `low`, or `unknown`.
- **Incomplete Data**: Missing inputs must trigger default assumptions, low-confidence output labels, data gaps, and recommended collection actions.
- **Backend Stack**: FastAPI/Python remains preferred because calculation services are central to the product.
- **Frontend Stack**: Next.js/React/TypeScript remains preferred for dashboard delivery and VPS deployment.
- **Deployment**: The target runtime is VPS with Docker Compose and Nginx.
- **LLM Provider**: LLM integration uses OpenRouter.
- **Seed Data**: The initial MVP includes PLTU Tenayan sample data from the blueprint.
- **Map Scoring**: Opportunity score, readiness score, confidence score, composite score, and heatmap weight must remain separately visible.
- **Language**: Investor and management narratives should support concise professional Indonesian.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use GSD default workflow settings | User approved default GSD setup: YOLO, coarse granularity, parallel execution, planning docs committed, balanced agents, and research/plan-check/verifier enabled for later phase work | Good - v1.0 completed with full planning and verification trail |
| Skip project-level research during initialization | User chose to treat the provided blueprint as the authoritative source for initial requirements and roadmap | Good - blueprint stayed sufficient for MVP scope |
| Use Vertical MVP roadmap structure | User chose phase slices that deliver usable end-to-end capabilities rather than pure horizontal layers | Good - each phase added visible functionality |
| Use FastAPI backend for calculation services | Blueprint recommends Python for scientific, financial, and deterministic calculation logic | Good - tests cover deterministic calculation services |
| Use Next.js frontend for dashboards | Blueprint recommends Next.js/React/TypeScript for rich dashboard UI and VPS deployment | Good - routes build and smoke successfully |
| Keep LLM out of numeric authority | The blueprint explicitly requires deterministic calculations and restricts LLM to explanation, summaries, document support, and narrative insight | Good - prompts and API design enforce guardrails |
| Adopt MapLibre for map heatmap implementation | Heatmap addendum explicitly recommends MapLibre GL JS for WebGL, GeoJSON, heatmap layers, and premium dashboard visuals | Good - `/dashboard/map` ships with MapLibre layers |
| Use three-part scoring for map ranking | Heatmap addendum requires opportunity, readiness, and confidence scores to remain visible and uses composite score = 45% opportunity + 35% readiness + 20% confidence | Good - scores are persisted and shown separately |
| Adapt addendum schema to Phase 1 `plants` table for v1 | Phase 1 already shipped a compact `plants` model; splitting into `plant_sites` and `plant_units` was not required for v1 | Good for MVP; revisit only if multi-site/multi-unit scope expands |

## Milestone History

- **v1.0 MVP** - Shipped 2026-05-16. Archive: `.planning/milestones/v1.0-ROADMAP.md`, `.planning/milestones/v1.0-REQUIREMENTS.md`, `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.
- **v2.0 Pre-FEED** - Shipped 2026-05-17. Scope: cost packages, vendor comparison, offtake readiness, MRV assumptions, risk register, and Pre-FEED decision dashboard.
- **v2.1 Economic Calibration & Shortlist Validation** - Started 2026-05-17. Scope: deterministic shortlist decision matrix and Top 3/Top 5 validation workspace.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? Move to Out of Scope with reason.
2. Requirements validated? Move to Validated with phase reference.
3. New requirements emerged? Add to Active or Candidate Next Requirements.
4. Decisions to log? Add to Key Decisions.
5. "What This Is" still accurate? Update if drifted.

**After each milestone:**
1. Full review of all sections.
2. Core Value check.
3. Audit Out of Scope.
4. Update Context with current state.

---
*Last updated: 2026-05-17 after v2.1 Phase 10 start*
