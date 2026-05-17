# Milestones

## v1.0 MVP (Shipped: 2026-05-16)

**Delivered:** A usable pre-feasibility simulator for MECH WIZ with deterministic calculations, MapLibre site ranking, investor case, OpenRouter narratives, and document intelligence.

**Phases completed:** 5 phases, 15 plans, 35 tasks

**Key accomplishments:**

- Persistent WIZ business scenarios with editable financial assumptions and a working `/scenarios` management surface
- Deterministic backend services for stack CO2, e-methanol, H2/electrolyzer sizing, revenue, LCOM, NPV, IRR, and payback
- Persisted scenario simulations with backend-authored outputs and a frontend latest-result workflow
- Implemented backend scoring, ranking, GeoJSON, and selected unit profile APIs.
- Implemented `/dashboard/map` as a usable MapLibre strategy dashboard.
- Implemented sensitivity persistence/API/UI and completed Phase 3 verification.
- Implemented backend investor dashboard aggregation and API.
- Implemented `/investor` as a usable investor case dashboard.
- Implemented persisted data quality, editable settings, and final Phase 4 verification.
- Implemented backend LLM insight generation foundation with OpenRouter guardrails and persistence.
- Implemented investor-facing LLM insight generation and review UI.
- Implemented document upload, extraction, repository, and basic grounded Q&A.

**Stats:**

- 5 phases, 15 plans, 35 tasks
- 69/69 v1 requirements satisfied
- 37 backend tests passing plus frontend production build
- 14,274 backend/frontend source lines counted at archive time
- Git range: `60a04fb feat(01): scaffold mvp spine and plant data` -> `10ac73d feat(05-03): add document intelligence`

**Archives:**

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`

**Known deferred items at close:**

- Pre-FEED CAPEX/OPEX, vendor proposal comparison, offtake readiness, MRV, and detailed risk register.
- Operational digital twin scope: DCS/SCADA, real-time optimization, predictive maintenance, live MRV, and production optimization.
- Live OpenRouter validation after configuring `OPENROUTER_API_KEY`.
- OCR/vector retrieval for scanned or long documents.

**What's next:** Start the next milestone with `$gsd-new-milestone`.

---

## v2.0 Pre-FEED (Shipped: 2026-05-17)

**Delivered:** A Pre-FEED decision workspace for package management, cost/vendor comparison, offtake/MRV readiness, risk governance, and committee brief generation.

**Phases completed:** 4 phases, 12 plans

**Key accomplishments:**

- Pre-FEED package records linked to plants, scenarios, source metadata, confidence, and documents.
- CAPEX/OPEX line items, vendor proposal comparison, and active cost-basis selection.
- Offtake prospects, price decks, MRV assumptions, carbon-intensity indicators, and readiness gaps.
- Risk register, decision gates, blockers, next actions, and LLM committee brief workflow.
- Follow-up curated 26-site PLTU dataset, PDF report, and executive dashboard summary.

**Known deferred items at close:**

- Final PLN/site/vendor-confirmed economics and port handling costs.
- Production hardening and controlled map tiles.
- OCR/vector retrieval for scanned or long documents.

**What's next:** v2.1 Economic Calibration & Shortlist Validation.

---

## v2.1 Economic Calibration & Shortlist Validation (Shipped: 2026-05-17)

**Delivered:** A deterministic shortlist decision matrix and `/shortlist` page for Top 3/Top 5 validation.

**Phases completed:** 1 phase, 1 plan

**Key accomplishments:**

- Combines existing screening score, scenario economics, port readiness/proximity, confidence, and data gaps.
- Labels candidates as Top 3, Top 5, or watchlist.
- Shows rationale, next actions, method weights, warnings, and full decision matrix.

**What's next:** Validate Top 3 with PLN/site/port/vendor data or start a deployment/production-readiness milestone.

---
