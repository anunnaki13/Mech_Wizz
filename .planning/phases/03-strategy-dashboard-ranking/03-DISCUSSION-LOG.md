# Phase 3 Discussion Log

## Source Inputs

- User instruction: continue with GSD after Phase 2 completion.
- Imported addendum: `docs/MECH_WIZ_Heatmap_Map_Addendum.md`.
- Phase 2 outputs: persisted `ScenarioResult`, deterministic calculation services, `/scenarios` workflow.

## Discussion Outcome

No new user questions were required. The heatmap addendum and prior project decisions already lock the major gray areas:

- MapLibre GL JS is the map renderer.
- Phase 1 `plants` remain the identity model for v1.
- Scores are separate opportunity, readiness, confidence, composite, and heatmap weight fields.
- LLM investor summaries remain deferred to Phase 5.
- Full data gap engine remains deferred to Phase 4, while Phase 3 can expose score-derived bottlenecks and missing-input labels.

## Planning Direction

Phase 3 will be split into three executable plans:

1. Backend scoring, ranking, GeoJSON, and selected profile APIs.
2. `/dashboard/map` MapLibre dashboard UI.
3. Sensitivity engine, persistence, tornado UI, and final verification.
