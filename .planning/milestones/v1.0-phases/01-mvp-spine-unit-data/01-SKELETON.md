# Walking Skeleton — MECH WIZ AI Digital Twin

**Phase:** 1
**Generated:** 2026-05-16

## Capability Proven End-to-End

A user can open `/dashboard`, see database-backed PLTU Tenayan unit data loaded through FastAPI, and manage Phase 1 unit input records through the web UI.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend framework | Next.js App Router + React + TypeScript | Matches blueprint routes and supports dashboard-first app structure. |
| Backend framework | FastAPI + Pydantic v2 | Fits typed REST APIs and future deterministic calculation services. |
| Data layer | PostgreSQL + SQLAlchemy 2.x + Alembic | Provides relational integrity, migrations, and a path for later scenario/result tables. |
| UI system | Tailwind CSS + shadcn/ui + lucide-react | Matches premium enterprise dashboard direction and gives accessible local components. |
| Deployment target | Docker Compose on VPS/local dev | Blueprint targets VPS deployment with Nginx later; Compose is the first local execution contract. |
| Directory layout | Root monorepo with `backend/`, `frontend/`, `docs/`, `.planning/` | Keeps backend/frontend independent but easy to run together. |
| Auth | None in Phase 1 | Blueprint does not require authentication for the initial pre-feasibility simulator. |

## Stack Touched in Phase 1

- [ ] Project scaffold (framework, build, lint, test runner)
- [ ] Routing — at least `/`, `/dashboard`, `/units`, `/units/:id`, `/scenarios`, `/investor`, `/sensitivity`, `/documents`, `/settings`
- [ ] Database — real read and write for plant/unit records, emission tests, site readiness, and hydrogen strategy
- [ ] UI — interactive unit data surfaces wired to the API
- [ ] Deployment — documented local full-stack Docker Compose run command

## Out of Scope (Deferred to Later Slices)

- CO2, captured CO2, e-methanol, H2, financial, ranking, scoring, and sensitivity calculations
- Investor KPI economics and scenario comparison
- Data gap engine and editable assumption/scoring settings
- OpenRouter LLM insight
- Document upload, extraction, and document Q&A
- Authentication and authorization
- Real-time DCS/SCADA integration

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: Scenario Simulation Engine adds deterministic calculation and scenario result persistence.
- Phase 3: Strategy Dashboard & Ranking adds scoring, map-ready ranking data, and sensitivity analysis.
- Phase 4: Investor Case & Data Quality adds investor dashboard, confidence engine, data gaps, and editable assumptions.
- Phase 5: LLM & Document Intelligence adds OpenRouter insight and document workflows.
