---
phase: 02-scenario-simulation-engine
plan: "02"
subsystem: calculation-engine
tags: [python, deterministic-calculations, co2, methanol, financial]
requires:
  - phase: 02-scenario-simulation-engine
    provides: Scenario and financial assumption records from plan 02-01
provides:
  - Pure CO2 stack calculation functions
  - Methanol, captured CO2, H2, and electrolyzer sizing functions
  - Gross revenue, LCOM, NPV, IRR, and payback functions
affects: [scenario-simulation, ranking, investor-dashboard, llm-summaries]
tech-stack:
  added: []
  patterns: [pure calculation modules, None for incomplete calculability, ValueError for invalid numeric inputs]
key-files:
  created:
    - backend/app/services/calculations/co2.py
    - backend/app/services/calculations/methanol.py
    - backend/app/services/calculations/hydrogen.py
    - backend/app/services/calculations/financial.py
  modified: []
key-decisions:
  - "Do not add numpy_financial; IRR uses local deterministic bisection."
  - "Missing required assumptions return None rather than fabricated financial outputs."
  - "Project life default is centralized in calculation defaults."
patterns-established:
  - "Backend calculations are unit-bearing and explicit in function names."
  - "Tests verify simple formula cases and a complete CALC-09 financial case."
requirements-completed: [CALC-01, CALC-02, CALC-03, CALC-04, CALC-05, CALC-06, CALC-07, CALC-08, CALC-09]
duration: 6min
completed: 2026-05-16
---

# Phase 2 Plan 02: Calculation Services Summary

**Deterministic backend services for stack CO2, e-methanol, H2/electrolyzer sizing, revenue, LCOM, NPV, IRR, and payback**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-16T11:43:21+07:00
- **Completed:** 2026-05-16T11:49:03+07:00
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added CO2 stack formulas for area, normalized gas flow, wet fraction, kg/s, ton/day, ton/year, and multi-stack aggregation.
- Added captured/vented CO2, theoretical/actual methanol, H2 requirement, and electrolyzer MW calculations using blueprint defaults.
- Added financial formulas for carbon credit conversion, gross revenue, annualized CAPEX, OPEX, H2/electricity cost, LCOM, NPV, IRR, and payback.

## Task Commits

1. **Tasks 1-3: Calculation services and tests** - `c534db6`

## Files Created/Modified

- `backend/app/services/calculations/defaults.py` - Blueprint constants and project-life default.
- `backend/app/services/calculations/co2.py` - Stack and aggregate CO2 functions.
- `backend/app/services/calculations/methanol.py` - Capture and methanol output functions.
- `backend/app/services/calculations/hydrogen.py` - H2 requirement and electrolyzer size functions.
- `backend/app/services/calculations/financial.py` - Revenue and financial metrics.
- `backend/tests/test_calculations.py` - Formula and invalid/missing-input tests.

## Decisions Made

- Invalid physical inputs raise `ValueError`; incomplete data returns `None` where outputs cannot be calculated.
- IRR takes explicit cashflows, with `calculate_project_irr` as the helper for equal annual cashflow projects.
- Electricity cost uses electrolyzer MW, 24 hours/day, operating days/year, and USD/kWh price.

## Deviations from Plan

None - plan scope executed as written.

## Issues Encountered

- One test expectation for annual cashflow was corrected after formula verification.

## Verification

- `cd backend && pytest -q tests/test_calculations.py` - 6 passed.
- `cd backend && pytest -q` - 16 passed.
- `rg -n "calculate_stack_area_m2|calculate_methanol_actual_ton_year|calculate_irr|calculate_payback_years" backend/app/services backend/tests` - expected matches found.

## User Setup Required

None.

## Next Phase Readiness

Plan 02-03 can now orchestrate persisted simulations by loading plant, emission, scenario, and financial assumption records and calling these pure services.

---
*Phase: 02-scenario-simulation-engine*
*Completed: 2026-05-16*
