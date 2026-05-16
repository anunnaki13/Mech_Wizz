# Phase 1: MVP Spine & Unit Data - Research

**Researched:** 2026-05-16
**Domain:** Full-stack dashboard walking skeleton with FastAPI, PostgreSQL, Next.js, and shadcn/ui
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Use a monorepo layout with `backend/`, `frontend/`, `docs/`, `.planning/`, `docker-compose.yml`, `README.md`, and `.env.example`.
- Use FastAPI + Python for the backend, Next.js + React + TypeScript for the frontend, and PostgreSQL as the database.
- Docker Compose is the primary local run path.
- Backend API lives under `/api` and must include health/version checks.
- Phase 1 schema covers `plants`, `emission_tests`, `site_readiness`, and `hydrogen_strategies`.
- Include UUID primary keys, timestamp fields, `data_status`, and `confidence_level`.
- Seed PLTU Tenayan from `docs/blueprint.md` without inventing missing values.
- Phase 1 UI is a functional premium enterprise dashboard shell, not a landing page.
- Do not fake IRR, NPV, LCOM, scoring, heatmaps, or sensitivity numbers.

### the agent's Discretion
- Choose the ORM, migration, frontend data-fetching, and form libraries if they fit the chosen stack.
- Keep Phase 1 styling lean but visibly aligned with the blueprint.
- Choose safe local seed behavior that avoids uncontrolled duplicate records.

### Deferred Ideas (OUT OF SCOPE)
- Scenario calculations, CO2/methanol/H2 estimators, and financial KPIs belong to Phase 2.
- Ranking, heatmap, score radar, and tornado sensitivity chart belong to Phase 3.
- Investor dashboard, confidence engine, data gap engine, assumptions settings, and scoring weights belong to Phase 4.
- OpenRouter insight and document intelligence belong to Phase 5.
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Docker Compose local stack | Deployment/DevOps | Backend, Frontend, Database | Phase success starts with a reproducible local environment. |
| Plant/unit persistence | Database/Storage | API/Backend | PostgreSQL owns durable records; backend owns validation and API contracts. |
| Unit input forms | Browser/Client | API/Backend | User interaction happens in the frontend; backend validates and persists. |
| Seed Tenayan data | API/Backend | Database/Storage | Seed logic should be repeatable and use backend/database models, not manual SQL snippets only. |
| Dashboard shell | Browser/Client | API/Backend | Frontend owns layout and navigation; it must load real unit data from `/api`. |
| Data status/confidence fields | Database/Storage | API/Backend, Browser/Client | Fields must exist in storage, be validated by API, and be visible in UI. |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 1 should be planned as a walking skeleton, not as separate horizontal layers. The smallest meaningful user-visible capability is: a user opens `/dashboard`, sees seeded PLTU Tenayan data loaded from PostgreSQL through FastAPI, then can create or update one Phase 1 unit input record through the UI.

The standard approach is a monorepo with `backend/` FastAPI service, `frontend/` Next.js App Router app, a PostgreSQL container, Alembic migrations, SQLAlchemy 2.x models, Pydantic v2 schemas, and shadcn/ui components for the enterprise dashboard shell. The seed script should be idempotent and should preserve unknown values as null or explicit `unknown` statuses.

**Primary recommendation:** Build one end-to-end unit-data slice first, then broaden Phase 1 coverage to the remaining input records and dashboard/profile screens.
</research_summary>

<standard_stack>
## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | `next@latest` with Node.js >= 20.9 | Frontend App Router, routing, build, dev server | Official docs recommend `create next-app` and `next@latest react@latest react-dom@latest`; App Router fits dashboard routes. |
| React | `react@latest` | UI runtime | Required by Next.js; works with shadcn/ui and dashboard components. |
| Tailwind CSS | latest compatible with shadcn CLI | Utility styling | Blueprint and shadcn both fit Tailwind-driven dashboard UI. |
| shadcn/ui | `shadcn@latest` CLI | Local component scaffolding | Provides editable components; official CLI supports view/apply/migrate flows. |
| FastAPI | 0.136.1 observed on PyPI | Backend REST API | Strong fit for typed REST APIs, Pydantic validation, OpenAPI docs, and future calculation services. |
| Pydantic | 2.13.0 observed on PyPI | Request/response validation | Native FastAPI model validation; v2 is current major line. |
| SQLAlchemy | 2.0.49 observed in official docs | ORM and database access | Current SQLAlchemy 2.x line; supports explicit typed models and Postgres. |
| Alembic | 1.18.4 observed in official docs | Database migrations | Official SQLAlchemy migration tool; supports autogeneration and migration scripts. |
| PostgreSQL | 16 or 17 container | Relational database | Blueprint selects PostgreSQL; relational integrity fits unit/scenario data. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| psycopg | 3.x | PostgreSQL driver | Use with SQLAlchemy 2.x for Postgres connectivity. |
| uvicorn | current | ASGI server | FastAPI local/dev container runtime. |
| pytest | current | Backend tests | Use for health/API/model tests from Phase 1. |
| TanStack Query | latest v5 docs | Frontend server-state fetching | Use if executor wants caching/mutation ergonomics for CRUD. Direct fetch wrapper is also acceptable in Phase 1. |
| react-hook-form + zod | current compatible versions | Frontend form state and validation | Useful for Phase 1 forms; keep schemas aligned with backend fields. |
| lucide-react | current | Icons | Required by UI-SPEC for dashboard/actions. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SQLAlchemy + Alembic | SQLModel | SQLModel is convenient but can lag SQLAlchemy/Pydantic changes; SQLAlchemy + Pydantic is clearer for a calculation-heavy app. |
| Next.js App Router | Vite SPA | Vite is simpler, but blueprint route structure and production dashboard shell fit Next well. |
| TanStack Query | Direct fetch utilities | Direct fetch is enough for Phase 1, but TanStack Query scales better for CRUD mutations and cached lists. |
| shadcn/ui | Hand-built components | shadcn gives accessible primitives and consistent local ownership; hand-building every control adds design debt. |

**Installation direction:**
```bash
# frontend
pnpm create next-app frontend
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button card input select dialog table tabs badge tooltip skeleton
pnpm add lucide-react @tanstack/react-query react-hook-form zod @hookform/resolvers

# backend
pip install fastapi==0.136.1 "uvicorn[standard]" sqlalchemy==2.0.49 alembic psycopg pydantic==2.13.0 pydantic-settings pytest httpx
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### System Architecture Diagram

```text
Browser
  |
  | GET /dashboard, /units, /units/:id
  v
Next.js App Router
  |
  | fetch /api/plants and nested resource endpoints
  v
FastAPI Routers
  |
  | Pydantic schemas validate requests/responses
  v
Service/Repository Layer
  |
  | SQLAlchemy session
  v
PostgreSQL
  |
  | Alembic migrations define durable schema
  v
Seed Script
```

### Recommended Project Structure

```text
backend/
├── alembic/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── seed.py
├── tests/
├── requirements.txt
└── Dockerfile
frontend/
├── app/
│   ├── dashboard/
│   ├── units/
│   ├── scenarios/
│   ├── investor/
│   ├── sensitivity/
│   ├── documents/
│   └── settings/
├── components/
│   ├── layout/
│   ├── ui/
│   └── units/
├── lib/
├── types/
├── package.json
└── Dockerfile
```

### Pattern 1: API-owned Validation
**What:** Backend Pydantic schemas define allowed values and required fields for Phase 1 resources.
**When to use:** Every create/update endpoint.
**Example target:** `PlantCreate`, `PlantRead`, `EmissionTestCreate`, `SiteReadinessCreate`, `HydrogenStrategyCreate`.

### Pattern 2: Idempotent Seed
**What:** Seed script upserts Tenayan by a stable natural key such as `plant_name='PLTU Tenayan'` and `unit_name='Unit 1-2'`.
**When to use:** Local development and demo setup.
**Example target:** `python -m app.seed` can be run repeatedly and leaves exactly one Tenayan plant record.

### Pattern 3: Frontend API Client Wrapper
**What:** Centralize `BACKEND_URL` handling and JSON error parsing in `frontend/lib/api.ts`.
**When to use:** All frontend pages that call the backend.
**Example target:** `getPlants()`, `getPlant(id)`, `createPlant(payload)`, `createEmissionTest(plantId, payload)`.

### Anti-Patterns to Avoid
- **Fake economics in Phase 1:** Do not show fabricated IRR/NPV/LCOM/scoring values.
- **Frontend-only enums:** `data_status` and `confidence_level` must be persisted and API-validated.
- **Manual schema without migrations:** Avoid relying only on `metadata.create_all` for project evolution.
- **Layer-cake plan execution:** Do not build all schema first, then all API, then all UI with no user-visible slice until the end.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form controls and dialogs | Custom accessibility primitives | shadcn/ui components | Saves accessibility and consistency work. |
| Database migrations | Manual SQL snippets only | Alembic migrations | Later phases need safe schema evolution. |
| Request validation | Custom if/else validators scattered in endpoints | Pydantic schemas | Produces consistent errors and OpenAPI docs. |
| API docs | Hand-maintained endpoint list only | FastAPI OpenAPI plus README summary | Reduces drift. |
| Server-state cache | Ad hoc global state | TanStack Query or centralized fetch wrapper | Prevents inconsistent CRUD refresh behavior. |

**Key insight:** Phase 1 is the architecture backbone. Reusing standard framework primitives is more valuable than clever custom abstractions.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Schema Drift Between Backend and Frontend
**What goes wrong:** Frontend forms accept fields or enum values the backend rejects.
**Why it happens:** UI schemas are invented separately from backend Pydantic schemas.
**How to avoid:** Keep allowed values in one documented set and add tests/API checks for enum values.
**Warning signs:** `data_status` labels differ across forms, API responses, and database records.

### Pitfall 2: Seed Script Creates Duplicate Demo Data
**What goes wrong:** Every setup run creates another Tenayan plant and duplicate chimneys.
**Why it happens:** Seed script blindly inserts without a stable lookup.
**How to avoid:** Upsert by stable plant/unit fields or use a fixed seed UUID only in local/dev.
**Warning signs:** `/api/plants` shows multiple identical Tenayan rows after repeated setup.

### Pitfall 3: Dashboard Shell Pretends Later Phases Are Done
**What goes wrong:** Phase 1 UI displays fake investor KPIs or scoring values to fill space.
**Why it happens:** The dashboard visual target is confused with later calculation scope.
**How to avoid:** Show real Phase 1 facts and clearly mark simulation/scoring insights as future.
**Warning signs:** Static hardcoded IRR/NPV/LCOM values appear in frontend code.

### Pitfall 4: Docker Compose Works Only On One Machine
**What goes wrong:** Services depend on local host paths, undeclared env vars, or manual commands.
**Why it happens:** Setup is tested from an already-configured shell instead of clean env.
**How to avoid:** `.env.example`, container healthchecks, migrations, seed command, and README run steps must be explicit.
**Warning signs:** Backend logs fail with missing `DATABASE_URL` or frontend cannot reach API.
</common_pitfalls>

<code_examples>
## Code Examples

Concrete code will be written during execution. Planning should require:

```python
# backend/app/main.py target shape
app = FastAPI(title="MECH WIZ AI Digital Twin API")
app.include_router(api_router, prefix="/api")
```

```python
# backend/app/schemas/common.py target enum values
DATA_STATUS_VALUES = ("actual", "estimated", "benchmark", "user_assumption", "unknown", "partner_supplied")
CONFIDENCE_LEVEL_VALUES = ("high", "medium", "low", "unknown")
```

```ts
// frontend/lib/api.ts target shape
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  // joins NEXT_PUBLIC_API_BASE_URL and parses JSON/errors consistently
}
```
</code_examples>

<sota_updates>
## State of the Art (2024-2026)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pages Router by default | App Router and recommended Next defaults | Current Next docs, updated 2026 | Use `frontend/app/` route structure. |
| SQLAlchemy 1.x style | SQLAlchemy 2.x docs/current release | Current official SQLAlchemy docs | Prefer 2.x session/model patterns. |
| Pydantic v1 schemas | Pydantic v2 current line | Current PyPI release history | Use v2 model config and validators. |
| Copying registry code blindly | Use `shadcn view` before third-party registry blocks | Current shadcn CLI docs | UI-SPEC registry safety gate should be enforced. |
</sota_updates>

<open_questions>
## Open Questions

1. **Package manager**
   - What we know: Next docs support pnpm/npm/yarn/bun; shadcn examples include pnpm/npm/yarn/bun.
   - What's unclear: User has not specified a JavaScript package manager.
   - Recommendation: Use `pnpm` if available; fall back to `npm` if install constraints appear during execution.

2. **Frontend query library**
   - What we know: TanStack Query is a good fit for CRUD state, but direct fetch is enough for a small skeleton.
   - What's unclear: Whether the executor should optimize for fewer dependencies or future CRUD ergonomics.
   - Recommendation: Use a small `apiFetch` wrapper first; add TanStack Query only if the forms/lists become repetitive during execution.
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- Next.js official docs — installation and system requirements: https://nextjs.org/docs/pages/getting-started/installation
- FastAPI PyPI release page — current package release observed: https://pypi.org/project/fastapi/
- SQLAlchemy official docs — 2.0 current release observed: https://docs.sqlalchemy.org/en/20/core/
- Alembic official docs — migration/autogeneration documentation: https://alembic.sqlalchemy.org/en/latest/index.html
- shadcn/ui official CLI docs — component registry/view/apply/migrate commands: https://ui.shadcn.com/docs/cli
- TanStack Query official React docs: https://tanstack.com/query/latest/docs/framework/react/
- Pydantic PyPI release page — v2 release history observed: https://pypi.org/project/pydantic/

### Project Sources (HIGH confidence)
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/01-mvp-spine-unit-data/01-CONTEXT.md`
- `.planning/phases/01-mvp-spine-unit-data/01-UI-SPEC.md`
- `docs/blueprint.md`
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Next.js, shadcn/ui.
- Ecosystem: backend validation, migrations, Docker Compose, dashboard shell, CRUD forms.
- Patterns: walking skeleton, API-owned validation, idempotent seeding, frontend API client wrapper.
- Pitfalls: schema drift, duplicate seed data, fake dashboard metrics, fragile compose setup.

**Confidence breakdown:**
- Standard stack: HIGH - verified against project blueprint and official package/docs pages.
- Architecture: HIGH - greenfield monorepo matches blueprint and Phase 1 scope.
- Pitfalls: HIGH - derived from common full-stack failure modes and Phase 1 constraints.
- Code examples: MEDIUM - examples are target shapes, not copied from framework docs.
</metadata>
