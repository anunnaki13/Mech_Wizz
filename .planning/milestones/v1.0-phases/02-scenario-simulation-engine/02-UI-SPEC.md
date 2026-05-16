# Phase 2 UI Spec: Scenario Simulation Engine

## Goal

Turn `/scenarios` from a placeholder into a compact operational workbench for scenario creation, financial assumptions, simulation execution, and persisted result review.

## Target User

PLN NP business development, engineering, and management users validating a pre-feasibility scenario before map/ranking and investor packaging.

## Screen Contract

### `/scenarios`

Must include:

- Plant selector or selected plant summary.
- Scenario list for the selected plant.
- Create/edit scenario controls for:
  - scenario name,
  - scheme: WIZ Access, WIZ Align, WIZ Augment,
  - PLN ownership percent,
  - partner CAPEX responsibility percent,
  - PLN CAPEX responsibility percent,
  - revenue model,
  - capture rate.
- Financial assumptions panel for:
  - methanol price,
  - grey methanol price,
  - hydrogen price,
  - electricity price,
  - carbon credit price,
  - exchange rate,
  - discount rate,
  - tax rate,
  - CAPEX fields,
  - OPEX percentage,
  - data status and confidence.
- `Run Simulation` action.
- Latest result panel showing:
  - total CO2,
  - captured CO2,
  - vented CO2,
  - methanol output,
  - H2 required,
  - electrolyzer MW,
  - gross revenue,
  - LCOM,
  - NPV,
  - IRR,
  - payback,
  - confidence level,
  - missing/benchmark warning.

## UX Rules

- No fake economics. If a value is null because assumptions are incomplete, display `Pending assumptions` or equivalent.
- Show `data_status` and `confidence_level` chips near assumptions and results.
- Keep result cards compact; Phase 2 is a workbench, not the final investor dashboard.
- Do not add map, ranking, tornado chart, or investor summary UI here.

## Styling

Follow Phase 1 dark enterprise shell:

- Background: `#07111f`
- Panels: dark navy, 8px radius
- Accents: cyan/teal, restrained amber for warnings
- Typography: compact, readable, dashboard-like

## Acceptance

- `/scenarios` builds in Next.js.
- UI contains `Run Simulation`.
- UI contains `WIZ Access`, `WIZ Align`, and `WIZ Augment`.
- UI shows result labels for `Captured CO2`, `E-Methanol`, `H2 Required`, `LCOM`, `NPV`, `IRR`, and `Payback`.
- UI shows data quality labels and does not hardcode final numeric financial outputs.
