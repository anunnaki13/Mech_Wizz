# Phase 3 Context: Strategy Dashboard & Ranking

## Phase Goal

Turn persisted Phase 2 scenario results into a Map & Heatmap Intelligence Layer for site selection, ranking, score breakdowns, KPIs, and sensitivity outputs.

## Boundary

In scope:

- Backend scoring, ranking, GeoJSON, and selected unit profile APIs.
- Persisted scoring output records for `DATA-09`.
- `/dashboard/map` using MapLibre GL JS with heatmap, markers, filters, ranking table, KPI cards, and selected unit detail.
- Sensitivity analysis persistence and tornado chart data/UI.

Out of scope:

- LLM investor summary generation. This remains Phase 5.
- Full data gap engine persistence and editable recommendations. Phase 3 can expose score-derived bottlenecks and missing-input labels; full data gap workflow remains Phase 4.
- Rewriting Phase 1 `plants` into addendum `plant_sites` / `plant_units`.
- FEED-grade financial assumptions or partner CAPEX defaults.

<decisions>
## Implementation Decisions

### Data Lineage

- **D-01:** Phase 3 consumes persisted `ScenarioResult` records as the numeric source of truth.
- **D-02:** Frontend must not recalculate CO2, methanol, H2, LCOM, NPV, IRR, payback, or scores.
- **D-03:** Continue using Phase 1 `plants` as unit/site identity; do not introduce `plant_sites` or `plant_units` in Phase 3.
- **D-04:** Tenayan map display may update seed latitude/longitude from the addendum coordinates if missing.
- **D-05:** `ScenarioResult.missing_inputs`, `assumption_snapshot`, `calculation_version`, and `confidence_level` must be propagated into map/ranking/profile responses.

### Scoring

- **D-06:** Add persisted `UnitScoringResult` records tied to `plant_id`, `scenario_id`, and latest `scenario_result_id`.
- **D-07:** Recalculation may create a new scoring run per plant/scenario and mark rank positions from the latest scoring set.
- **D-08:** Opportunity score uses addendum weights: CO2 availability 30%, methanol potential 20%, market/logistics 15%, land availability 10%, utility advantage 10%, carbon credit potential 5%, strategic value 10%.
- **D-09:** Readiness score uses addendum weights: data completeness 20%, emission data quality 20%, land readiness 15%, utility readiness 15%, H2 strategy clarity 15%, permit/logistic readiness 15%.
- **D-10:** Confidence score uses addendum data-status mapping: actual 1.00, estimated 0.70, benchmark 0.55, user_assumption 0.50, partner_supplied 0.60, unknown 0.00.
- **D-11:** Composite score formula is 45% opportunity, 35% readiness, and 20% confidence.
- **D-12:** Heatmap weight must include opportunity, readiness, economic return, and confidence, normalized to 0..1.
- **D-13:** Scoring formulas must live in backend services and be covered by tests.
- **D-14:** Ranking rows must include rank, unit/site, province, composite, opportunity, readiness, confidence, CO2, methanol, estimated IRR, recommended scheme, and key bottleneck.

### APIs

- **D-15:** Use `/api/scoring/unit-ranking`, `/api/scoring/recalculate`, `/api/map/unit-opportunity`, and `/api/units/{plant_id}/profile` style APIs while keeping `plant_id` as the identifier.
- **D-16:** GeoJSON must be generated from backend scoring/scenario data and include feature properties required by MapLibre heatmap, marker, popup, and profile behavior.
- **D-17:** Unit profile API combines plant, emission, readiness, hydrogen, scenario, latest simulation result, scoring result, confidence labels, and score-derived bottlenecks.
- **D-18:** Score/ranking recalculation must respond to selected scenario and scheme filters.

### UI

- **D-19:** `/dashboard/map` is the first usable strategy dashboard screen, not a marketing page.
- **D-20:** Use MapLibre GL JS for map rendering unless the package is technically blocked during implementation.
- **D-21:** Map UI must consume backend GeoJSON/ranking/profile APIs rather than hard-coded dummy data.
- **D-22:** If plant coordinates are missing, UI/backend should surface that as a data-quality issue; Tenayan seed may provide addendum coordinates.
- **D-23:** Filters include scenario, business scheme, region, fuel type, data confidence, opportunity level, and visible layer toggles.
- **D-24:** UI must visibly label data status/confidence and avoid presenting benchmark/null economics as final.
- **D-25:** Investor summary button/generation is deferred; do not add OpenRouter work in Phase 3.

### Sensitivity

- **D-26:** Add sensitivity persistence in Phase 3 for scenario/plant variables: H2 price, electricity price, methanol price, CAPEX, capture rate, plant availability, carbon credit price, and exchange rate.
- **D-27:** Sensitivity uses backend calculation services and stored scenario assumptions; frontend displays returned results only.
- **D-28:** If financial assumptions are incomplete, sensitivity returns null/low-confidence outputs with warning metadata instead of inventing CAPEX.
- **D-29:** Tornado chart can be implemented with HTML/CSS bars; no chart library is required for MVP.

### Completion

- **D-30:** Phase 3 completion requires backend tests, frontend build, Docker Compose config, Alembic temp upgrade, and GSD verification/review artifacts.
</decisions>

## Acceptance Notes

- Phase 3 should keep one usable vertical flow: seed/run scenario, recalculate scoring, view `/dashboard/map`, select Tenayan, see profile, run sensitivity.
- Tenayan is acceptable as the primary pilot record, but code must be multi-plant capable for later expansion.
