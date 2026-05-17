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

## v2.2 Top 3 Validation Pack & Committee Memo (Shipped: 2026-05-17)

**Delivered:** A management-ready validation pack for the current Top 3 shortlist.

**Phases completed:** 1 phase, 1 plan

**Key accomplishments:**

- Top 3 validation pack JSON API derived from deterministic shortlist outputs.
- Evidence checklist across technical, economics, logistics, power/H2, commercial, and MRV categories.
- Candidate comparison axes, decision questions, no-go triggers, caveats, and deterministic committee memo.
- Committee memo PDF endpoint.
- `/validation-pack` UI linked from navigation, dashboard, and shortlist.

**What's next:** Use the pack to collect PLN/site/vendor/port/offtake/MRV evidence, or start production deployment hardening.

---

## v2.3 Evidence Collection Workspace (Shipped: 2026-05-17)

**Delivered:** A persisted evidence tracking workspace for the Top 3 validation pack.

**Phases completed:** 1 phase, 1 plan

**Key accomplishments:**

- Validation evidence records persisted by plant, scenario, category, and evidence key.
- Status lifecycle for `missing`, `requested`, `received`, `verified`, and `rejected`.
- Evidence workspace API that merges Phase 11 checklist defaults with saved records.
- Evidence readiness score, status mix, verified item count, and high-priority open gap rollups.
- `/evidence` UI linked from navigation and validation pack.

**What's next:** Production deployment hardening, OCR/retrieval expansion, or evidence-driven shortlist recalibration after real PLN/site/vendor data is entered.

---

## v2.4 Pilot Decision Dashboard (Shipped: 2026-05-17)

**Delivered:** A management-facing pilot recommendation dashboard derived from deterministic shortlist and evidence readiness data.

**Phases completed:** 1 phase, 1 plan

**Key accomplishments:**

- Pilot decision API combining shortlist score and evidence readiness.
- Evidence-adjusted score with transparent penalties for rejected evidence and high-priority open gaps.
- Gate labels for `committee_ready`, `needs_evidence`, and `blocked`.
- Candidate blockers, next actions, portfolio action plan, methodology, and warnings.
- `/pilot-decision` UI linked from navigation and the evidence workspace.

**What's next:** Export/report generation for pilot decision meetings, deployment hardening, or OCR/retrieval expansion.

---

## v2.5 Workflow UX Audit & Simplification Plan (Completed: 2026-05-17)

**Delivered:** A GSD audit of route health, API health, button/function complexity, operator workflow friction, and simplification priorities.

**Phases completed:** 1 phase, 1 audit plan

**Key findings:**

- All 13 primary frontend pages returned HTTP 200.
- 11 key backend APIs returned HTTP 200.
- Runtime is healthy, but operator simplicity is not.
- Sidebar is too flat with 13 equal-weight modules.
- `/scenarios`, `/evidence`, `/prefeed`, `/dashboard/map`, and `/sensitivity` carry the most interaction burden.
- Destructive actions lack consistent confirmation.
- The business workflow should be centered around Dashboard -> Pilot Decision -> Evidence -> Validation Pack.

**What's next:** Phase 15 Guided Workflow & Simplified Navigation.

---
