---
type: quick-task-plan
status: complete
created: 2026-05-17
updated: 2026-05-17
---

# PLN PLTU Public Screening Import

## Goal

Populate MECH WIZ with a useful public screening dataset of PLN-related operating PLTU units, then run scenario simulations and scoring so the map heatmap is meaningful.

## Plan

- Use web/public data to identify a comprehensive source for Indonesian coal-fired units.
- Filter for operating Indonesia units related to PLN, PLN Indonesia Power, PLN Nusantara Power, legacy Indonesia Power/PJB, or PLN ownership participation.
- Add an idempotent backend import script that creates plant records, benchmark emissions, site readiness, hydrogen strategy, WIZ Align scenarios, and financial assumptions.
- Run simulations and scoring against the local backend database.
- Change map default filter to all scenarios so imported units render as a heatmap by default.
- Document source, assumptions, and rerun steps.

## Result

Implemented via `backend/app/import_pln_pltu.py`, map filter changes, and `docs/PLN_PLTU_PUBLIC_SCREENING_IMPORT.md`.
