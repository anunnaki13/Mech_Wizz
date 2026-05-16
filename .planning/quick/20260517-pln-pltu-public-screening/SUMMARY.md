---
type: quick-task-summary
status: complete
created: 2026-05-17
updated: 2026-05-17
---

# Summary

Imported a public screening dataset for PLN-related operating PLTU units and made the map default to all scenarios.

## Source

- Global Energy Monitor Global Coal Plant Tracker January 2026 map GeoJSON.
- PLN RUPTL 2025-2034 public context.

## Results

- Indonesia coal units in source: 526
- Indonesia operating coal units in source: 287
- PLN-related operating units imported: 96
- Simulations run: 96
- Simulation failures: 0
- Latest map/scoring records visible with all-scenario filter: 97

## Verification

- `python -m app.import_pln_pltu` completed successfully.
- `GET /api/plants/` returned 97 plants.
- `GET /api/scoring/unit-ranking?scheme=align` returned 97 rows.
- `GET /api/map/unit-opportunity?scheme=align` returned 97 features.
- `npm run build` passed.
- `/dashboard/map` returned HTTP 200 after production server restart.
