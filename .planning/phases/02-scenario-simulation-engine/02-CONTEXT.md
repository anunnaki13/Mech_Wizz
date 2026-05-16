# Phase 2: Scenario Simulation Engine - Context

**Gathered:** 2026-05-16T11:22:08+07:00  
**Status:** Ready for research and planning  
**Source:** GSD continuation from completed Phase 1 plus blueprint/addendum review

<domain>
## Phase Boundary

Phase 2 makes scenarios calculable and reproducible through deterministic backend services.

In scope:
- Business scenarios for `WIZ Access`, `WIZ Align`, and `WIZ Augment`.
- Financial assumption records tied to scenarios.
- Deterministic CO2, captured CO2, methanol, H2, electrolyzer, revenue, LCOM, NPV, IRR, and payback calculations.
- Scenario result persistence and reload by result/scenario ID.
- Frontend scenario management and simulation result display.

Out of scope:
- MapLibre heatmap, GeoJSON map endpoint, ranking, scoring, and confidence-score heatmap formulas. Those are Phase 3.
- Sensitivity analysis and tornado charts. Those are Phase 3.
- OpenRouter/LLM summaries. Those are Phase 5.
- Investor dashboard packaging. That is Phase 4.
</domain>

<decisions>
## Implementation Decisions

### Numeric Authority
- **D-01:** All Phase 2 numeric outputs must come from deterministic backend code.
- **D-02:** The frontend may display results but must not recalculate CO2, methanol, H2, revenue, LCOM, NPV, IRR, or payback.
- **D-03:** LLM must not be introduced in Phase 2.

### Existing Schema Compatibility
- **D-04:** Use the Phase 1 `plants` table as the source for plant/unit identity.
- **D-05:** Use existing `emission_tests.co2_percent_dry`, `gas_velocity_m_s`, `stack_diameter_m`, `flue_gas_temperature_c`, `moisture_percent`, and plant `operating_days_per_year`.
- **D-06:** Do not split into addendum `plant_sites` / `plant_units` during Phase 2.

### Scenario Shape
- **D-07:** Add `BusinessScenario` records tied to `plant_id`.
- **D-08:** `scheme` allowed values are `access`, `align`, and `augment`.
- **D-09:** The seed/demo should include at least a Tenayan `WIZ Align Base Case` scenario matching the blueprint direction.
- **D-10:** Scenario CRUD must support create/list/read/update/delete.

### Financial Assumption Shape
- **D-11:** Add one financial assumption record per scenario for the Phase 2 MVP.
- **D-12:** Required requirement fields: methanol price, grey methanol price, hydrogen price, electricity price, carbon credit price, exchange rate, discount rate, tax rate, CAPEX fields, OPEX percentage, `data_status`, and `confidence_level`.
- **D-13:** CAPEX fields may be null for real early-stage data. Simulation must not fabricate CAPEX-driven outputs as final values.

### Missing Financial Inputs
- **D-14:** Technical outputs must still calculate when emission and plant operating data exist.
- **D-15:** Financial outputs may be null when required financial assumptions are missing.
- **D-16:** When financial outputs are null or benchmark-driven, results must be low-confidence and expose missing/assumption context through result fields or response metadata.
- **D-17:** Tests should include a complete-assumptions case proving CALC-09 works end-to-end.

### Formula Defaults
- **D-18:** Use blueprint defaults:
  - `process_efficiency = 0.60`
  - `h2_utilization_factor = 0.90`
  - `h2_productivity_kg_day_per_mw = 480`
  - `co2_density_kg_per_nm3 = 1.964`
- **D-19:** Capture rate should be stored on the scenario or simulation request, not hardcoded only in the service. Default may be `0.85` for a base case if no user value is provided and must be labeled as assumption/benchmark.
- **D-20:** Project life for NPV/IRR/payback may be a service default if not exposed in the model, but the service must keep it centralized and documented.

### Scenario Results
- **D-21:** Add persisted `ScenarioResult` records linked to a scenario.
- **D-22:** Store technical and financial outputs needed by Phase 3: total CO2, captured CO2, vented CO2, methanol, H2 required, electrolyzer size, gross revenue, LCOM, NPV, IRR, payback, `confidence_level`, and calculation version.
- **D-23:** Store enough assumption snapshot fields or metadata so a reloaded result is reproducible without silently changing when assumptions change later.

### UI
- **D-24:** `/scenarios` becomes a real work page in Phase 2.
- **D-25:** The user must be able to select a plant, create/read scenarios, edit financial assumptions, run simulation, and see persisted results.
- **D-26:** UI remains operational/dashboard-like, not a marketing page.
- **D-27:** Scenario result labels must show whether outputs are actual/estimated/benchmark/user assumption driven.
</decisions>

<canonical_refs>
## Canonical References

Downstream planning and implementation must read:

- `.planning/ROADMAP.md` — Phase 2 boundary and success criteria.
- `.planning/REQUIREMENTS.md` — Phase 2 requirement IDs: `DATA-05`, `DATA-06`, `UNIT-05`, `UNIT-06`, `CALC-01` through `CALC-10`.
- `.planning/phases/01-mvp-spine-unit-data/01-VERIFICATION.md` — Phase 1 verified app shape.
- `docs/blueprint.md` — main blueprint formulas, data models, scenario/financial assumptions.
- `docs/MECH_WIZ_Heatmap_Map_Addendum.md` — Phase 3 downstream data needs that Phase 2 result fields must support.
- `backend/alembic/versions/0001_phase1_schema.py` — current migration style.
- `backend/app/models/plant.py`, `backend/app/models/emission_test.py` — Phase 2 calculation input sources.
- `frontend/app/scenarios/page.tsx`, `frontend/lib/api.ts` — current frontend placeholder and API helper pattern.
</canonical_refs>

<specifics>
## Specific Ideas

- Use service modules such as `backend/app/services/calculations/co2.py`, `methanol.py`, `hydrogen.py`, and `financial.py` or equivalent cohesive structure.
- Add focused pure-function tests for formula services before integration endpoint tests.
- Add endpoint similar to `POST /api/scenarios/{scenario_id}/simulate` and `GET /api/scenarios/{scenario_id}/results`.
- Seed Tenayan scenario/assumptions idempotently so the app demonstrates a result path after Phase 2.
</specifics>

<deferred>
## Deferred Ideas

- MapLibre rendering, heatmap layers, and GeoJSON endpoint: Phase 3.
- Opportunity/readiness/confidence scoring and ranking: Phase 3.
- Sensitivity engine and tornado chart: Phase 3.
- Investor summary via OpenRouter: Phase 5.
- Detailed FEED-grade CAPEX/OPEX model: v2.
</deferred>

---

*Phase: 02-scenario-simulation-engine*  
*Context gathered: 2026-05-16 via GSD continuation*
