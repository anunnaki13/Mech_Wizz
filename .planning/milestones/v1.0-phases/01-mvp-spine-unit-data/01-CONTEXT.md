# Phase 1: MVP Spine & Unit Data - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the walking skeleton for MECH WIZ AI Digital Twin: a runnable Docker Compose stack with PostgreSQL, FastAPI, and Next.js; the core database model for unit input data; seeded PLTU Tenayan data; REST APIs for plant, emission, site readiness, and hydrogen strategy records; and the first usable dashboard/unit-profile frontend surfaces.

This phase must not implement scenario calculations, scoring, ranking, investor economics, sensitivity analysis, LLM insight, or document intelligence. Those belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### App Spine And Repository Shape
- **D-01:** Use a monorepo layout with `backend/`, `frontend/`, `docs/`, `.planning/`, `docker-compose.yml`, `README.md`, and `.env.example` at the repository root.
- **D-02:** Use FastAPI + Python for the backend, Next.js + React + TypeScript for the frontend, and PostgreSQL as the only database in Phase 1.
- **D-03:** Docker Compose is the primary local run path. It must start PostgreSQL, backend API, and frontend web services together.
- **D-04:** Keep the backend API under `/api` and include a lightweight health/version endpoint so the frontend and developer can verify the stack is connected.

### Data Model And Persistence
- **D-05:** Implement the Phase 1 schema around `plants`, `emission_tests`, `site_readiness`, and `hydrogen_strategies` first, while preparing the project structure for later scenario and result tables.
- **D-06:** Use UUID primary keys, timestamp fields, and explicit `data_status` / `confidence_level` fields on the relevant tables from the beginning.
- **D-07:** Store `data_status` and `confidence_level` as constrained strings in the application layer and, where practical, database-level constraints. Do not hide these fields behind frontend-only labels.
- **D-08:** Prefer Alembic-style migrations over ad hoc schema creation so future phases can evolve the database safely.

### Seed Data And Defaults
- **D-09:** Seed PLTU Tenayan exactly from `docs/blueprint.md` as the initial demonstration unit, including the two chimney emission test entries.
- **D-10:** Keep the seed path repeatable and safe for local development. Re-running the seed should not create uncontrolled duplicate Tenayan records.
- **D-11:** Do not invent missing Tenayan values in Phase 1. Missing values should remain null or explicitly marked as `unknown` / low confidence.

### First UI Surface
- **D-12:** Phase 1 UI should be a functional enterprise dashboard shell, not a marketing page.
- **D-13:** Use the blueprint visual direction: dark navy background, cyan/teal accents, compact KPI cards, clean typography, professional high-tech look, and navigation for the planned routes.
- **D-14:** The `/dashboard` route should show the application frame and enough seeded Tenayan/unit summary data to prove backend-to-frontend integration.
- **D-15:** Unit/profile UI in Phase 1 should prioritize readable forms and detail sections for plant, emission, site readiness, and hydrogen strategy data. Advanced charts can be placeholders or omitted until later phases.

### API And Validation
- **D-16:** Use REST/JSON APIs matching the blueprint endpoint direction for plants, emission tests, site readiness, and hydrogen strategy.
- **D-17:** Return structured validation errors from the backend and keep frontend forms aligned with the backend schemas.
- **D-18:** Keep calculations out of Phase 1 except trivial derived display helpers. CO2, methanol, H2, financial, ranking, and sensitivity calculations start in later phases.

### the agent's Discretion
- The implementation agent may choose specific Python ORM and frontend data-fetching libraries if they fit the chosen stack and do not conflict with the blueprint. Preference should go to common, maintainable choices that work cleanly in Docker Compose.
- The implementation agent may decide whether the first UI uses direct fetch calls, a small API client wrapper, or a lightweight query library, as long as the pattern is easy to extend in later phases.
- The implementation agent may keep Phase 1 styling lean, but it must visibly follow the premium dark enterprise direction so future UI phases have a real base to extend.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Product framing, core value, constraints, stack direction, and key decisions.
- `.planning/REQUIREMENTS.md` — Phase 1 requirement IDs and full v1 traceability.
- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, dependencies, and plan outline.
- `.planning/STATE.md` — Current project state and workspace git constraint.

### Source Blueprint
- `docs/blueprint.md` — Original MECH WIZ AI Digital Twin blueprint.
- `docs/blueprint.md` §5 — Recommended frontend/backend/database/deployment stack.
- `docs/blueprint.md` §8 — MVP input JSON examples.
- `docs/blueprint.md` §9.1-9.4 — Phase 1 database tables for plants, emission tests, site readiness, and hydrogen strategies.
- `docs/blueprint.md` §14-15 — Dashboard visual direction and frontend route structure.
- `docs/blueprint.md` §16.1-16.4 — Phase 1 API endpoint direction.
- `docs/blueprint.md` §19-22 — Recommended folder structure, environment variables, design tokens, and Tenayan seed data.
- `docs/blueprint.md` §23-24 — MVP acceptance criteria and important developer notes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No application code exists yet. The reusable assets are planning artifacts and the local source blueprint.

### Established Patterns
- GSD planning docs are committed through an alternate gitdir because the workspace `.git` directory is a read-only empty tmpfs mount.
- Use `GIT_DIR=.git-real GIT_WORK_TREE=.` for git-aware commands in this workspace unless the environment is repaired.

### Integration Points
- New application code should be created under `backend/` and `frontend/`.
- Root-level `docker-compose.yml`, `.env.example`, and `README.md` should become the local developer entry points.
- Frontend `/dashboard` should prove the backend and database integration by loading seeded Tenayan/unit data through the API.

</code_context>

<specifics>
## Specific Ideas

- The product should feel like a premium technical-financial decision dashboard for PLN NP management, business development, partners, and investors.
- Phase 1 should establish the visual shell and data management foundation without pretending later economics/scoring features are complete.
- Tenayan is the first demonstration site and should be visible early.

</specifics>

<deferred>
## Deferred Ideas

- Scenario calculations, CO2/methanol/H2 estimators, and financial KPIs belong to Phase 2.
- Ranking, heatmap, score radar, and tornado sensitivity chart belong to Phase 3.
- Investor dashboard, confidence engine, data gap engine, assumptions settings, and scoring weights belong to Phase 4.
- OpenRouter insight and document intelligence belong to Phase 5.

</deferred>

---

*Phase: 1-MVP Spine & Unit Data*
*Context gathered: 2026-05-16*
