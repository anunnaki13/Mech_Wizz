# Phase 2 Discussion Log: Scenario Simulation Engine

## Mode

Inline GSD continuation. The user said "ok lanjut" after Phase 1 completion and heatmap map addendum import.

## Inputs Reviewed

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/01-mvp-spine-unit-data/01-VERIFICATION.md`
- `docs/blueprint.md`
- `docs/MECH_WIZ_Heatmap_Map_Addendum.md`
- Phase 1 backend/frontend code and migrations

## Decisions Captured

- Keep numeric authority in deterministic backend services.
- Build Phase 2 around current Phase 1 `plants` and `emission_tests` schema.
- Add business scenarios, financial assumptions, calculation services, scenario results, and `/scenarios` UI.
- Preserve Phase 3 map/scoring needs by including result fields useful for later GeoJSON/ranking, but do not implement heatmap/scoring in Phase 2.
- Handle missing CAPEX and financial inputs explicitly instead of fabricating final economics.

## Questions Deferred

None requiring immediate user input. Defaults are taken from the blueprint and addendum; ambiguous implementation details are left to research/planning.
