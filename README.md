# MECH WIZ AI Digital Twin

Phase 2 builds the scenario simulation engine for PLN NP pre-feasibility screening. It includes a FastAPI backend, PostgreSQL database, deterministic scenario calculations, persisted simulation results, and a Next.js scenario workbench.

## Local Development

Copy the environment sample if you want local overrides:

```bash
cp .env.example .env
```

Start the full stack:

```bash
docker compose up --build
```

In a second terminal, apply the versioned schema migration:

```bash
docker compose exec backend alembic upgrade head
```

Seed the initial Tenayan unit, WIZ Align base scenario, and benchmark financial assumptions:

```bash
docker compose exec backend python -m app.seed
```

Open the web app at http://localhost:3000/dashboard, manage scenarios at http://localhost:3000/scenarios, and check the API health endpoint at http://localhost:8000/api/health.

## Phase 2 Scenario Simulation

The scenario workflow is:

1. Select a plant in `/scenarios`.
2. Create or edit a WIZ Access, WIZ Align, or WIZ Augment scenario.
3. Save financial assumptions for the scenario.
4. Run the simulation to persist a `ScenarioResult`.

Core API endpoints:

```text
GET/POST /api/plants/{plant_id}/scenarios
GET/PUT/DELETE /api/scenarios/{scenario_id}
GET/PUT /api/scenarios/{scenario_id}/financial-assumptions
POST /api/scenarios/{scenario_id}/simulate
GET /api/scenarios/{scenario_id}/results
GET /api/scenario-results/{result_id}
```

## Verification

```bash
docker compose config
cd backend && pytest -q
cd frontend && npm run build
```

For a local migration smoke test outside Docker:

```bash
cd backend
DATABASE_URL=sqlite:////tmp/mechwiz_phase2_full.db .venv/bin/alembic upgrade head
```
