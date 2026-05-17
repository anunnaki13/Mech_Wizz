---
gsd_state_version: 1.0
milestone: v2.3
milestone_name: Evidence Collection Workspace
status: completed
last_updated: "2026-05-17T16:45:00+07:00"
last_activity: 2026-05-17
progress:
  total_phases: 1
  completed_phases: 1
  total_plans: 1
  completed_plans: 1
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-17)

**Core value:** Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.
**Current focus:** v2.3 Evidence Collection Workspace complete

## Current Position

Phase: 12
Plan: 1 of 1 complete
Status: Milestone complete
Last activity: 2026-05-17 — Phase 12 evidence collection workspace shipped

## Performance Metrics

**Velocity:**

- Total plans completed: 30
- Average duration: ~20 min for Phase 9
- Total execution time: 59 min for Phase 9

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. MVP Spine & Unit Data | 3/3 | n/a | n/a |
| 2. Scenario Simulation Engine | 3/3 | n/a | n/a |
| 3. Strategy Dashboard & Ranking | 3/3 | n/a | n/a |
| 4. Investor Case & Data Quality | 3/3 | n/a | n/a |
| 5. LLM & Document Intelligence | 3/3 | n/a | n/a |
| 6. Pre-FEED Package Foundation | 3/3 | 22 min | ~7 min |
| 7. Cost & Vendor Proposal Engine | 3/3 | 28 min | ~9 min |
| 8. Offtake & MRV Readiness | 3/3 | 37 min | ~12 min |
| 9. Risk & Pre-FEED Decision Dashboard | 3/3 | 59 min | ~20 min |
| 10. Economic Calibration & Shortlist Validation | 1/1 | n/a | n/a |
| 11. Top 3 Validation Pack & Committee Memo | 1/1 | n/a | n/a |
| 12. Evidence Collection Workspace | 1/1 | n/a | n/a |

**Recent Trend:**

- Last 5 completed plans: 09-02, 09-03, 10-01, 11-01, 12-01
- Trend: v2.3 evidence workspace complete; Phase 12 executed and verified

*Updated after each plan completion*
| Phase 6 P06-01 | 6min | 3 tasks | 4 files |
| Phase 6 P06-03 | 9min | 3 tasks | 9 files |
| Phase 6 P06-02 | 7min | 3 tasks | 4 files |
| Phase 7 P07-01 | 8min | 3 tasks | 8 files |
| Phase 7 P07-02 | 8min | 3 tasks | 5 files |
| Phase 7 P07-03 | 12min | 3 tasks | 9 files |
| Phase 8 P08-01 | 12min | 3 tasks | 8 files |
| Phase 8 P08-02 | 11min | 3 tasks | 6 files |
| Phase 8 P08-03 | 14min | 3 tasks | 9 files |
| Phase 9 P09-01 | 18min | 3 tasks | 9 files |
| Phase 9 P09-02 | 22min | 3 tasks | 7 files |
| Phase 9 P09-03 | 19min | 3 tasks | 10 files |
| Phase 10 P10-01 | n/a | 3 tasks | 15 files |
| Phase 11 P11-01 | n/a | 3 tasks | 16 files |
| Phase 12 P12-01 | n/a | 3 tasks | 18 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Initialization: Use default GSD settings with YOLO mode, coarse granularity, parallel execution, committed planning docs, balanced agents, and workflow research/plan-check/verifier enabled.
- Initialization: Skip project-level research and use the provided MECH WIZ blueprint as the source of truth.
- Initialization: Use Vertical MVP roadmap structure.
- Initialization: Preserve deterministic backend calculations as numeric source of truth; use LLM only for narratives and document support.
- Addendum import: Treat `docs/MECH_WIZ_Heatmap_Map_Addendum.md` as the source for the Map & Heatmap Intelligence Layer.
- Addendum import: Use MapLibre GL JS for Phase 3 map rendering unless technically blocked.
- Addendum import: Use opportunity, readiness, and confidence scores as separate visible scores; composite score is 45/35/20 and heatmap weight includes economic return.
- Addendum import: Keep Phase 1 `plants` table for v1 and adapt addendum `plant_sites` / `plant_units` concepts during Phase 3 planning rather than rewriting shipped Phase 1 schema.
- Phase 02-01: Business scenarios remain tied directly to Phase 1 `plants`; one financial assumption record is upserted per scenario.
- Phase 02-01: CAPEX fields remain nullable and assumption records carry `data_status` plus `confidence_level`.
- Phase 02-02: Calculation services are pure backend functions; missing calculability returns `None`, invalid physical inputs raise `ValueError`.
- Phase 02-02: IRR uses a local deterministic bisection implementation rather than adding `numpy_financial`.
- Phase 02-03: Scenario simulation results persist backend-authored outputs with missing input metadata, assumption snapshot, calculation version, and confidence level.
- Phase 02-03: Frontend displays stored result values and does not recalculate simulation outputs.
- Phase 03-01: `UnitScoringResult` persists opportunity, readiness, confidence, composite, heatmap weight, rank, scoring version, data gap count, recommended scheme, and key bottleneck.
- Phase 03-01: Ranking, GeoJSON, and selected unit profile APIs consume persisted backend results and expose `plant_id` as the v1 site/unit identifier.
- Phase 03-02: `/dashboard/map` consumes backend GeoJSON/ranking/profile APIs with MapLibre heatmap, markers, labels, filters, ranking, and score breakdown UI.
- Phase 03-03: Sensitivity analysis persists one row per variable and exposes null-safe warning metadata when financial assumptions are incomplete.
- Phase 04 planning: Investor dashboard must consume backend aggregates only; OpenRouter/LLM investor memos remain Phase 5.
- Phase 04 planning: Data gaps and editable defaults/settings are persisted backend data in Phase 4, not frontend-only state.
- Phase 04-01: `GET /api/investor-case` aggregates plant, scenario, latest result/scoring/sensitivity, KPIs, CAPEX structure, revenue mix, scenario comparison, deterministic thesis/risk/roadmap, data gaps, and warnings.
- Phase 04-02: `/investor` consumes backend investor aggregate with KPI, thesis, revenue mix, scenario comparison, risk, roadmap, why-this-wins, CAPEX, and data gap panels.
- Phase 04-03: `ApplicationSetting` persists editable default assumptions and scoring weights with validation.
- Phase 04-03: `DataGap` persists current gap recommendations synchronized from deterministic scoring gap derivation.
- Phase 04-03: Scoring recalculation consumes persisted scoring weights and falls back to Phase 3 defaults when no setting is available.
- Phase 04-03: `/settings` exposes editable default assumptions, scoring weights, input status, output confidence, and data gap recommendations.
- Phase 05 planning: Use direct OpenRouter Chat Completions HTTP integration rather than a heavier AI framework for MVP single-call narrative workflows.
- Phase 05 planning: Keep OpenRouter API keys backend-only and return clear unavailable errors when not configured.
- Phase 05 planning: Prompts must separate actual data, assumptions, confidence, and gaps and must forbid invented numbers or LLM recalculation.
- Phase 05 planning: Document Q&A uses extracted text as bounded context for MVP; vector retrieval is deferred.
- Phase 05-01: `LlmInsight` persists prompt, response, model, status, error, usage, and plant/scenario/document references.
- Phase 05-01: OpenRouter calls are direct HTTP Chat Completions calls with mockable transport and backend-only API key configuration.
- Phase 05-01: Missing OpenRouter key creates a failed insight record and returns an explicit unavailable error.
- Phase 05-02: `/investor` includes a stored insight panel for executive summary, investor memo, data gap explanation, and sensitivity explanation.
- Phase 05-02: Frontend API helpers surface backend error details so OpenRouter configuration failures are visible.
- Phase 05-03: `/documents` supports upload, repository browsing, text extraction, extracted text preview, and document Q&A.
- Phase 05-03: Document upload paths are sanitized and stored under `UPLOAD_DIR`.
- Phase 05-03: Document Q&A uses extracted text as bounded context and persists `document_qa` insight attempts.
- Milestone v2.0: Scope is Pre-FEED Digital Twin rather than operational DCS/SCADA integration.
- Milestone v2.0: Phase numbering continues from v1.0, so the first new phase is Phase 6.
- Milestone v2.0: Requirements focus on Pre-FEED packages, detailed CAPEX/OPEX, vendor proposals, offtake readiness, MRV assumptions, risk register, decision gates, and a Pre-FEED dashboard.
- Milestone v2.1: Scope is Economic Calibration & Shortlist Validation, focused on Top 3/Top 5 decision support from the curated 26-site PLTU dataset.
- Phase 10: Shortlist score combines screening score, economics, logistics, and confidence with weights 35/25/20/20.
- Phase 10: Port selection for shortlist filters toward commercial port/terminal entries to avoid offshore oil-field records being treated as export ports.
- Milestone v2.2: Scope is Top 3 Validation Pack & Committee Memo, focused on management discussion and evidence collection before single-pilot selection.
- Phase 11: Committee memo PDF is generated deterministically from backend validation pack data; no LLM calculation or frontend recalculation is used.
- Milestone v2.3: Scope is Evidence Collection Workspace, focused on persisted validation evidence before single-pilot selection.
- Phase 12: Evidence records are stored separately from shortlist ranking so validation readiness can improve without silently changing screening scores.
- Phase 12: Evidence readiness is calculated deterministically from status lifecycle values, with verified evidence scoring highest and rejected/missing scoring zero.

### Pending Todos

None.

### Blockers/Concerns

- Workspace `.git` is a read-only empty tmpfs mount, so normal `git status` fails. GSD commits are written using separate gitdir `.git-real` with `GIT_DIR=.git-real GIT_WORK_TREE=.`.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Pre-FEED | Detailed CAPEX/OPEX, vendor proposal comparison, offtake readiness, MRV, detailed risk register | Promoted to active v2.0 scope | 2026-05-16 |
| Operational Digital Twin | DCS/SCADA, real-time optimization, predictive maintenance, live MRV, production optimization | Deferred to v3 | Initialization |

## Quick Tasks Completed

| Date | Task | Summary |
|------|------|---------|
| 2026-05-16 | Add Unit UI | Added `/units` New Unit form wired to `POST /api/plants/`; build and API create/delete verification passed. |
| 2026-05-17 | PLN PLTU public screening import | Imported 96 PLN-related operating PLTU units from public GEM data, ran 96 simulations, created 97 scoring/map records, and defaulted map to all scenarios. |
| 2026-05-17 | Port-aware map intelligence | Added NGA World Port Index ports, nearest-port scoring, economic zones, and Singapore export proxy corridors to the map; backend tests, frontend build, API checks, and state validation passed. |
| 2026-05-17 | Sensitivity and OpenRouter settings | Replaced the placeholder sensitivity page with a runnable workspace and added masked OpenRouter API key management in Settings; backend tests, frontend build, API checks, and state validation passed. |
| 2026-05-17 | README module guide | Expanded README into a detailed Indonesian guide explaining each module, required inputs, backend calculations, outputs, interpretation, data confidence, APIs, and limitations. |
| 2026-05-17 | Coordinate corrections | Audited plant map coordinates against public web/GEM sources, corrected the local Tenayan seed coordinate, updated the runtime database, and added a regression test. |
| 2026-05-17 | Curated PLTU target dataset | Replaced the broad public PLTU dataset with the 26 requested target sites, documented public source confidence, seeded regulatory BME benchmarks, ran simulations/scoring, and updated runtime DB. |
| 2026-05-17 | PLTU screening PDF report | Generated the 26-site PLTU screening PDF report, fixed electrolyzer CAPEX unit basis, reran import/simulation/scoring, and pushed the report to GitHub main. |
| 2026-05-17 | Dashboard summary report | Rebuilt `/dashboard` as a live executive summary with screening KPIs, calculation explanation, Top 10 candidates, confidence notes, next-phase guidance, and lightweight ranking aggregates. |
| 2026-05-17 | Evidence collection workspace | Added persisted Top 3 evidence records, readiness rollup API, `/evidence` UI, tests, build, migration, and runtime smoke checks. |

## Session Continuity

Last session: 2026-05-16T12:55:35.880Z
Stopped at: Completed Phase 9 Risk & Pre-FEED Decision Dashboard
Resume file: None

## Operator Next Steps

- Validate real Top 3 evidence in `/evidence`, start evidence-driven shortlist recalibration, or begin deployment/production-readiness hardening.
