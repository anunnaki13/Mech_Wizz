# MECH WIZ AI Digital Twin

Phase 1 builds the MVP spine for PLN NP pre-feasibility unit data management. It includes a FastAPI backend, PostgreSQL database, and Next.js dashboard shell.

## Local Development

Copy the environment sample if you want local overrides:

```bash
cp .env.example .env
```

Start the full stack:

```bash
docker compose up --build
```

Seed the initial Tenayan unit:

```bash
docker compose exec backend python -m app.seed
```

Open the web app at http://localhost:3000/dashboard and the API health endpoint at http://localhost:8000/api/health.

## Phase 1 Verification

```bash
docker compose config
cd backend && pytest -q
cd frontend && npm run build
```
