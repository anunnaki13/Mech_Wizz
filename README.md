# MECH WIZ AI Digital Twin

MECH WIZ AI Digital Twin is a PLN NP pre-feasibility screening cockpit for carbon-to-fuel pilot selection. It includes a FastAPI backend, PostgreSQL-ready persistence, deterministic scenario calculations, persisted scoring/sensitivity/data-quality outputs, OpenRouter-backed narrative insights, document upload/extraction/Q&A, and a Next.js dashboard.

Detailed Indonesian implementation notes are available in [`docs/GSD_v2_PREFEED_DETAILED_EXPLANATION.md`](docs/GSD_v2_PREFEED_DETAILED_EXPLANATION.md).

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

Seed the initial Tenayan unit, WIZ Align base scenario, coordinates, and benchmark financial assumptions:

```bash
docker compose exec backend python -m app.seed
```

Open the web app at http://localhost:3000/dashboard, add or review units at http://localhost:3000/units, manage scenarios at http://localhost:3000/scenarios, use the map intelligence layer at http://localhost:3000/dashboard/map, review the investor case at http://localhost:3000/investor, manage Pre-FEED packages at http://localhost:3000/prefeed, edit settings at http://localhost:3000/settings, and check the API health endpoint at http://localhost:8000/api/health.

## Remote Preview / Production-Like Run

For a server/IP preview, run the frontend with a production build instead of `next dev`. The dev server shows the Next.js `N` indicator and compiles modules on first open, which makes navigation feel heavier.

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

cd ../frontend
npm run build
npm run start -- --hostname 0.0.0.0 --port 3000
```

When `NEXT_PUBLIC_API_BASE_URL` is left at the local default, the browser client automatically switches API calls from `localhost:8000` to the same host that served the frontend. Set `CORS_ALLOWED_ORIGINS` to a comma-separated origin list for locked-down deployments, or keep `*` for a no-cookie demo preview.

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

## Phase 3 Map, Scoring, and Sensitivity

The map workflow is:

1. Run a scenario simulation from `/scenarios`.
2. Open `/dashboard/map`.
3. Recalculate scores for the selected scenario.
4. Review the heatmap, ranking, score breakdown, data gaps, and selected unit profile.
5. Run sensitivity from the selected unit panel.

Core API endpoints:

```text
POST /api/scoring/recalculate
GET /api/scoring/unit-ranking
GET /api/map/unit-opportunity
GET /api/units/{plant_id}/profile
POST /api/sensitivity/run
GET /api/scenarios/{scenario_id}/sensitivity
```

## Phase 4 Investor Case & Data Quality

The investor and quality workflow is:

1. Run scenario simulation, scoring, and sensitivity from `/scenarios` and `/dashboard/map`.
2. Open `/investor` to review KPIs, thesis flow, revenue mix, scenario comparison, risk mitigation, roadmap, why-this-wins content, CAPEX structure, and current data gaps.
3. Open `/settings` to edit default financial assumptions and scoring weights.
4. Review input `data_status`, output `confidence_level`, and persisted data gap recommendations.

Core API endpoints:

```text
GET /api/investor-case
GET /api/settings
GET /api/settings/{key}
PUT /api/settings/{key}
GET /api/data-quality/summary
```

## Phase 5 LLM & Document Intelligence

The insight and document workflow is:

1. Configure `OPENROUTER_API_KEY` in the backend environment when live generation is needed.
2. Open `/investor` and generate narrative outputs from stored backend facts: executive summary, investor memo, data gap explanation, or sensitivity explanation.
3. Open `/documents`, upload a PDF/XLSX/CSV/text-like file, extract text, and ask a document-grounded question.
4. Review stored insight records; every attempted generation stores prompt, response or error, model, status, and context references.

Core API endpoints:

```text
GET /api/llm/insights
POST /api/llm/summary/{scenario_id}
POST /api/llm/data-gap/{plant_id}
POST /api/llm/investor-memo/{scenario_id}
POST /api/llm/explain-sensitivity/{scenario_id}
POST /api/documents/upload
GET /api/documents
GET /api/documents/{document_id}
POST /api/documents/{document_id}/extract
POST /api/documents/{document_id}/ask
```

## Phase 6 Pre-FEED Package Foundation

The Pre-FEED package workflow is:

1. Open `/prefeed`.
2. Select a plant and optional scenario.
3. Create or update a package with owner, status, source organization, received date, version, `data_status`, and `confidence_level`.
4. Link existing uploaded documents to the package and classify each link as vendor proposal, EPC estimate, offtake document, MRV document, permit document, or internal note.
5. Review backend-generated package warnings for missing metadata, missing core document roles, and low or unknown confidence.

Core API endpoints:

```text
GET/POST /api/prefeed/packages
GET/PUT /api/prefeed/packages/{package_id}
POST /api/prefeed/packages/{package_id}/archive
GET/POST /api/prefeed/packages/{package_id}/documents
DELETE /api/prefeed/packages/{package_id}/documents/{link_id}
GET /api/prefeed/packages/{package_id}/gaps
```

## Phase 7 Cost & Vendor Proposal Engine

The cost and vendor workflow is:

1. Open `/prefeed` and select a plant, scenario, and Pre-FEED package.
2. Add detailed CAPEX and OPEX line items with source, currency, contingency/escalation, recurrence, `data_status`, and `confidence_level`.
3. Add vendor/EPC proposals with supporting document, scope coverage, commercial basis, delivery assumptions, exclusions, validity date, and confidence.
4. Review backend-generated cost totals, scenario-ready USD CAPEX patch fields, vendor comparison, and proposal gaps.
5. Select the active cost basis for the current scenario as either a blended package or a vendor proposal. The selection is stored separately and does not overwrite scenario simulation history.

Core API endpoints:

```text
GET/POST /api/prefeed/packages/{package_id}/cost-items
PUT/DELETE /api/prefeed/cost-items/{cost_item_id}
GET /api/prefeed/packages/{package_id}/cost-summary
GET/POST /api/prefeed/packages/{package_id}/vendor-proposals
PUT/DELETE /api/prefeed/vendor-proposals/{proposal_id}
GET /api/prefeed/packages/{package_id}/vendor-comparison
GET /api/prefeed/vendor-proposals/{proposal_id}/gaps
GET/POST /api/prefeed/scenarios/{scenario_id}/active-cost-basis
```

## Phase 8 Offtake & MRV Readiness

The offtake and MRV workflow is:

1. Open `/prefeed` and select a plant, scenario, and Pre-FEED package.
2. Add a market price deck for methanol, carbon credits, electricity, hydrogen, exchange rate, escalation, `data_status`, and `confidence_level`.
3. Add offtake prospects with counterparty, product, target volume, term, pricing basis, status, supporting document, and confidence.
4. Add MRV assumptions for baseline emissions, captured CO2 accounting, carbon intensity, electricity source, methodology, verification, and carbon credit eligibility.
5. Review backend-generated revenue, offtake readiness, carbon intensity, abatement, MRV readiness, and gap lists. The workflow does not overwrite scenario simulation history.

Core API endpoints:

```text
GET/POST /api/prefeed/packages/{package_id}/price-decks
PUT/DELETE /api/prefeed/price-decks/{deck_id}
POST /api/prefeed/price-decks/{deck_id}/activate
GET/POST /api/prefeed/packages/{package_id}/offtake-prospects
PUT/DELETE /api/prefeed/offtake-prospects/{prospect_id}
GET /api/prefeed/packages/{package_id}/offtake-summary
GET /api/prefeed/packages/{package_id}/offtake-gaps
GET/POST /api/prefeed/packages/{package_id}/mrv-assumptions
PUT/DELETE /api/prefeed/mrv-assumptions/{assumption_id}
GET /api/prefeed/packages/{package_id}/mrv-summary
GET /api/prefeed/packages/{package_id}/mrv-gaps
```

## Phase 9 Risk & Pre-FEED Decision Dashboard

The decision dashboard workflow is:

1. Open `/prefeed` and select a plant, scenario, and Pre-FEED package.
2. Review the backend-generated decision dashboard for package confidence, CAPEX/OPEX totals, active cost basis, vendor comparison, offtake/MRV readiness, blockers, and next actions.
3. Add risk register entries with category, likelihood, impact, mitigation, owner, due date, status, `data_status`, and `confidence_level`.
4. Add decision gate checklist items for technical, commercial, legal, land, grid, offtake, MRV, financing, and committee readiness.
5. Generate a Pre-FEED committee brief from stored package, cost, offtake, MRV, risk, gate, blocker, and deterministic scenario context.

Core API endpoints:

```text
GET/POST /api/prefeed/packages/{package_id}/risks
PUT/DELETE /api/prefeed/risks/{risk_id}
GET /api/prefeed/packages/{package_id}/risk-summary
GET/POST /api/prefeed/packages/{package_id}/decision-gates
PUT/DELETE /api/prefeed/decision-gates/{gate_id}
GET /api/prefeed/packages/{package_id}/decision-gate-summary
GET /api/prefeed/packages/{package_id}/decision-blockers
GET /api/prefeed/packages/{package_id}/decision-next-actions
GET /api/prefeed/packages/{package_id}/decision-dashboard
POST /api/prefeed/packages/{package_id}/committee-brief
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
DATABASE_URL=sqlite:////tmp/mechwiz_phase9_full.db .venv/bin/alembic upgrade head
```
