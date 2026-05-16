# Phase 4 UI Spec: Investor Case & Data Quality

## Pages

- `/investor`
- `/settings`

## Investor Page Intent

Convert stored simulation and scoring outputs into an investor-friendly case view without inventing unsupported numbers.

## Investor Layout

- AppShell remains.
- Page header: "Investor Case".
- Top controls:
  - Plant selector.
  - Scenario selector.
  - Refresh.
- KPI strip:
  - Project IRR
  - Estimated NPV
  - LCOM
  - Payback Period
  - E-Methanol Capacity
  - CO2 Abatement
  - CAPEX Structure
- Main sections:
  - Investment thesis flow: Assets & Advantages -> Partner Solution -> Market Access -> Output & Value.
  - Revenue mix panel.
  - Scenario comparison table: Access / Align / Augment.
  - Risk and mitigation panel.
  - Roadmap to scale.
  - Why this project wins.
  - Data quality and data gaps panel.

## Investor Controls

- Selects must use real backend plants/scenarios.
- Refresh must reload backend aggregate.
- No generate-investor-summary action until Phase 5.

## Settings Page Intent

Let users edit default assumptions and scoring weights used for missing-data and scoring workflows.

## Settings Layout

- Page header: "Data Quality & Assumptions".
- Sections:
  - Default financial assumptions.
  - Scoring weights.
  - Data status and confidence rules reference.
- Each setting shows:
  - key/category
  - editable JSON/value
  - data status
  - confidence level
  - save state

## Visual Contract

- Dense operational dashboard, not a landing page.
- Cards at 8px radius.
- Text must fit mobile/desktop.
- Null economics display "Not calculated".
- Warnings/data gaps use existing amber notice style.
- Avoid LLM/AI language in Phase 4 UI except noting Phase 5 is separate.
