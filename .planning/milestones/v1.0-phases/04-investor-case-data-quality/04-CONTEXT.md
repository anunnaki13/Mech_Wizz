# Phase 4 Context: Investor Case & Data Quality

## Phase Goal

Package persisted simulation, scoring, sensitivity, and profile data into an investor-ready case while making assumptions, confidence, defaults, and data gaps visible and editable where Phase 4 requires it.

## Boundary

In scope:

- Investor-facing backend aggregation API for selected plant/scenario.
- `/investor` dashboard with investor KPIs, thesis flow, revenue mix, scenario comparison, risks, roadmap, and why-this-wins sections.
- Data quality validation, confidence summary, data gap recommendations, and editable default assumptions/scoring weights.

Out of scope:

- OpenRouter / LLM investor memo generation. This remains Phase 5.
- FEED-grade CAPEX/OPEX modelling, partner proposal import, offtake contracts, and financing-grade diligence.
- Replacing deterministic backend calculations with frontend or LLM calculations.

<decisions>
## Implementation Decisions

### Investor Data Authority

- **D-01:** Investor dashboard consumes backend API aggregates; frontend must not calculate IRR, NPV, LCOM, payback, scores, sensitivity, or confidence.
- **D-02:** Backend investor API uses latest persisted `ScenarioResult`, `UnitScoringResult`, `SensitivityResult`, plant profile, scenario, and financial assumptions.
- **D-03:** Investor KPIs are indicative pre-feasibility values and must preserve `None` for unavailable financial outputs.
- **D-04:** CAPEX structure is derived from stored financial assumption CAPEX fields and scenario CAPEX responsibility percentages, with null-safe labels when CAPEX is missing.
- **D-05:** Revenue mix is derived from stored scenario result and financial assumptions; if inputs are missing, revenue segments return null/zero plus warnings rather than invented values.
- **D-06:** Scenario comparison uses existing WIZ Access, WIZ Align, and WIZ Augment scenarios/results for the same plant when available; missing schemes are shown as missing, not fabricated.

### Investor Narrative Without LLM

- **D-07:** Phase 4 investor thesis, risks, roadmap, and why-this-wins content is deterministic template content assembled from stored facts and gap/confidence metadata.
- **D-08:** No OpenRouter, prompt persistence, or AI-generated investor memo is introduced in Phase 4.
- **D-09:** Investor copy should be concise and professional, suitable for PLN NP management/investor context.

### Data Quality

- **D-10:** Allowed `data_status` values remain centralized as `actual`, `estimated`, `benchmark`, `user_assumption`, `unknown`, and `partner_supplied`.
- **D-11:** Allowed `confidence_level` values remain `high`, `medium`, `low`, and `unknown`.
- **D-12:** Important inputs must expose their data status in API/UI: plant, emission tests, site readiness, hydrogen strategy, scenario, and financial assumptions.
- **D-13:** Important outputs must expose confidence in API/UI: scenario result, scoring result, sensitivity result, investor aggregate, and data quality summary.
- **D-14:** Data gaps should include missing data name, impact, priority, recommendation, source module, and status.
- **D-15:** Full data gap persistence belongs to Phase 4 plan 03; plans 01/02 may consume derived gaps from Phase 3 profile/scoring services.
- **D-16:** Default assumptions are stored as editable settings with explicit data status and confidence impact.
- **D-17:** Scoring weights are stored as editable settings but scoring formulas remain backend-owned; settings values must be validated before use.

### Settings

- **D-18:** Settings are backend persisted application settings, not localStorage or frontend-only state.
- **D-19:** MVP settings may use key/value JSON records for default assumptions and scoring weights rather than many narrow settings tables.
- **D-20:** Settings UI must clearly distinguish default assumptions from actual user scenario assumptions.

### Completion

- **D-21:** Phase 4 completion requires backend tests, frontend build, Docker Compose config, Alembic temp upgrade, investor/settings route smoke checks, and GSD verification/review artifacts.
</decisions>

## Acceptance Notes

- The primary happy path is: choose Tenayan/base scenario, view investor dashboard, see null CAPEX warnings/data gaps, compare any available scenarios, and edit defaults/scoring weights in settings.
- Existing CAPEX nulls are expected; Phase 4 should make that explicit instead of treating it as a failure.
