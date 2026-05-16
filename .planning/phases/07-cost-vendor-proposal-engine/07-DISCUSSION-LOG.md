# Phase 7: Cost & Vendor Proposal Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16T15:08:00+07:00
**Phase:** 7-Cost & Vendor Proposal Engine
**Areas discussed:** cost item shape, aggregation behavior, vendor proposal scope, active cost basis, UI placement

---

## Cost Item Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Single cost item table | Use one table with `cost_type` for CAPEX/OPEX | ✓ |
| Separate CAPEX/OPEX tables | Split by cost class | |
| Let the agent decide | Use codebase fit | |

**User's choice:** Auto-selected recommended default.
**Notes:** Single table keeps package totals and API behavior compact for MVP.

---

## Aggregation Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Backend totals by currency | Deterministic totals, no silent FX conversion | ✓ |
| Convert all currencies automatically | Requires price deck/FX assumptions | |
| Let the agent decide | Use codebase fit | |

**User's choice:** Auto-selected recommended default.
**Notes:** FX conversion is deferred to Phase 8 price deck work.

---

## Vendor Proposal Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Structured scope booleans | Explicit fields for required Pre-FEED scopes | ✓ |
| Free-form scope notes only | Less implementation, weaker comparison | |
| Let the agent decide | Use codebase fit | |

**User's choice:** Auto-selected recommended default.
**Notes:** Structured scope enables deterministic comparison and gaps.

---

## Active Cost Basis

| Option | Description | Selected |
|--------|-------------|----------|
| Selection record | Store active selection separately with snapshot totals | ✓ |
| Write to financial assumptions | Directly mutate simulation assumptions | |
| Let the agent decide | Use codebase fit | |

**User's choice:** Auto-selected recommended default.
**Notes:** Selection records preserve scenario simulation history.

---

## UI Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `/prefeed` | Add cost/vendor panels to existing package workspace | ✓ |
| New `/costs` route | Separate cost workspace | |
| Let the agent decide | Use codebase fit | |

**User's choice:** Auto-selected recommended default.
**Notes:** Phase 7 is package-scoped, so `/prefeed` remains the right operational home.

## the agent's Discretion

- Exact endpoint names under `/api/prefeed`.
- Component split inside `/prefeed`.
- Whether vendor table and cost item table ship in one migration or multiple migrations.

## Deferred Ideas

- Currency conversion/FX assumptions.
- OCR/table extraction from vendor PDFs.
- Offtake/MRV readiness calculations.
