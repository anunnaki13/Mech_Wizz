# MECH WIZ AI Digital Twin

## What This Is

MECH WIZ AI Digital Twin is a web-based pre-feasibility simulation and decision-support engine for identifying PLN NP power generation units that are suitable candidates for e-methanol / carbon-to-fuel projects. It combines unit mapping, deterministic technical and financial calculations, scoring, ranking, sensitivity analysis, data confidence tracking, data gap analysis, investor-facing dashboards, and LLM-generated narrative insight.

This is not a real-time operational digital twin connected to DCS/SCADA. The MVP is an assumption-driven simulator that works with incomplete early-stage data by using explicit assumptions, confidence levels, and visible data gaps.

## Core Value

Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.

## Requirements

### Validated

(None yet - ship to validate)

### Active

- [ ] Provide a working web dashboard for strategy overview, unit mapping, ranking, KPI review, scoring, sensitivity, and insight.
- [ ] Store and manage power plant unit profile data, emission test data, site readiness data, hydrogen strategy data, financial assumptions, business scenarios, simulation results, sensitivity results, documents, and LLM insight records.
- [ ] Calculate CO2 flow, captured CO2, e-methanol potential, H2 requirement, electrolyzer size, revenue, LCOM, NPV, IRR, payback, opportunity score, readiness score, composite score, and sensitivity impacts through deterministic backend code.
- [ ] Track `data_status` for important inputs and `confidence_level` for important outputs.
- [ ] Run with incomplete data by applying editable default assumptions, marking low-confidence outputs, and surfacing data gaps with recommended follow-up actions.
- [ ] Compare WIZ Access, WIZ Align, and WIZ Augment business schemes.
- [ ] Present an investor-friendly dashboard with selected pilot site, indicative IRR, NPV, LCOM, payback, CAPEX structure, revenue mix, scenario comparison, risk mitigation, scale roadmap, and investment thesis.
- [ ] Use OpenRouter-backed LLM features only for explanation, summaries, investor memos, risk narratives, data gap explanation, sensitivity explanation, document Q&A, and document extraction support.
- [ ] Prevent the LLM from being the source of record for technical or financial calculations.
- [ ] Seed the MVP with the Tenayan sample data from the blueprint.

### Out of Scope

- Real-time DCS/SCADA/historian integration - this belongs to a later operational digital twin phase.
- Detailed FEED-grade CAPEX/OPEX modelling - MVP is pre-feasibility and must label indicative results clearly.
- Reactor methanol, hydrogen plant, EPC vendor, partner proposal, offtake contract, and final financing data as mandatory inputs - MVP must operate before those are available.
- LLM-generated numerical calculations - deterministic backend calculations are the authoritative source.
- Mobile native application - dashboard web app is the first delivery target.
- Full MRV, predictive maintenance, and production optimization - deferred to future v2/v3 roadmap.

## Context

The source blueprint is `MECH_WIZ_AI_Digital_Twin_Blueprint.md` from `https://github.com/anunnaki13/Mech_Wizz`, version v1.0 MVP / Pre-Feasibility Mode. The target users are Business Development, MMRK, Engineering, PLN NP management, potential partners, and investors.

The two main outputs are:

1. Unit Mapping & Economic Site Selection: map, opportunity heatmap, unit scoring, ranking, opportunity score, readiness score, composite score, CO2 potential, H2 gap estimator, e-methanol potential, sensitivity analysis, data confidence, and data gap analysis.
2. Investor-Friendly Dashboard: investment thesis, selected pilot site, indicative IRR, indicative NPV, indicative LCOM, indicative payback, CAPEX structure, revenue mix, WIZ Access / WIZ Align / WIZ Augment scenario comparison, key risks and mitigation, roadmap to scale, why the project wins, and AI-generated investor summary.

The product is positioned as a combination of:

- Calculation engine for CO2, H2, e-methanol, LCOM, IRR, NPV, payback, scoring, and sensitivity.
- Decision-support engine for choosing the strongest unit and business scenario.
- Assumption-driven simulator for incomplete data conditions.
- LLM insight layer for explanation and narrative output.
- Document intelligence layer for PDF, Excel, proposal, market report, emission report, and internal document handling.

Recommended architecture from the blueprint:

- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Mapbox GL JS or Leaflet, Framer Motion, Lucide Icons.
- Backend: FastAPI and Python for calculation-heavy services.
- Database: PostgreSQL for MVP, with optional TimescaleDB later.
- Document/vector layer: pgvector in PostgreSQL or Qdrant later if a separate vector database is needed.
- Object storage: local VPS storage for MVP, MinIO or S3-compatible storage for production.
- LLM: OpenRouter for executive summaries, data gap explanation, scenario explanation, risk explanation, document Q&A, and investor memo generation.
- Deployment: Docker Compose on VPS, Nginx reverse proxy, HTTPS via Certbot, PostgreSQL, FastAPI container, Next.js container, and optional worker container.

The MVP data model includes these core tables:

- `plants`
- `emission_tests`
- `site_readiness`
- `hydrogen_strategies`
- `financial_assumptions`
- `business_scenarios`
- `scenario_results`
- `sensitivity_results`
- `documents`
- `llm_insights`

The MVP route structure should include:

- `/dashboard`
- `/units`
- `/units/:id`
- `/scenarios`
- `/scenarios/:id`
- `/investor`
- `/sensitivity`
- `/documents`
- `/settings`

The UI direction from the blueprint is a premium enterprise dashboard: dark navy background, cyan/teal accents, clean typography, compact KPI cards, map heatmap, ranking table, radar chart, tornado sensitivity chart, investor dashboard panels, and professional high-tech styling.

## Constraints

- **Calculation Authority**: Deterministic backend code must calculate all technical and financial outputs - LLM must not invent or calculate source-of-record numbers.
- **Data Status**: Important inputs must carry `data_status` values: `actual`, `estimated`, `benchmark`, `user_assumption`, `unknown`, or `partner_supplied`.
- **Confidence**: Important outputs must carry `confidence_level` values: `high`, `medium`, `low`, or `unknown`.
- **Incomplete Data**: Missing inputs must trigger default assumptions, low-confidence output labels, data gaps, and recommended collection actions.
- **Backend Stack**: FastAPI/Python is preferred because calculation services are central to the product.
- **Frontend Stack**: Next.js/React/TypeScript is preferred for dashboard delivery and VPS deployment.
- **Deployment**: The target runtime is VPS with Docker Compose and Nginx.
- **LLM Provider**: LLM integration should use OpenRouter.
- **Seed Data**: The initial MVP should include PLTU Tenayan sample data from the blueprint.
- **Language**: Investor and management narratives should support concise professional Indonesian.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use GSD default workflow settings | User approved default GSD setup: YOLO, coarse granularity, parallel execution, planning docs committed, balanced agents, and research/plan-check/verifier enabled for later phase work | - Pending |
| Skip project-level research during initialization | User chose to treat the provided blueprint as the authoritative source for initial requirements and roadmap | - Pending |
| Use Vertical MVP roadmap structure | User chose phase slices that deliver usable end-to-end capabilities rather than pure horizontal layers | - Pending |
| Use FastAPI backend for calculation services | Blueprint recommends Python for scientific, financial, and deterministic calculation logic | - Pending |
| Use Next.js frontend for dashboards | Blueprint recommends Next.js/React/TypeScript for rich dashboard UI and VPS deployment | - Pending |
| Keep LLM out of numeric authority | The blueprint explicitly requires deterministic calculations and restricts LLM to explanation, summaries, document support, and narrative insight | - Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-16 after initialization*
