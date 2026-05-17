---
status: complete
created: 2026-05-17
completed: 2026-05-17
slug: curated-pltu-dataset
---

# Curated PLTU Target Dataset

Replace the broad public PLN PLTU import with the 26 user-requested target PLTU sites.

## Scope

- Research public sources for capacity, coordinates, and regulatory emission limits.
- Add a deterministic importer that clears old plant-linked data and seeds exactly the target list.
- Preserve documents by unlinking stale plant/scenario references rather than deleting uploaded files.
- Seed screening inputs needed by the app: plant, emission benchmark, site readiness, H2 strategy, scenario, financial assumptions.
- Run simulations and scoring so the map/dashboard works immediately after import.
- Document source confidence and known reconciliation gaps.

## Verification

- Backend importer tests cover exact plant count, total capacity, coordinates, regulatory BME baseline, simulation creation, and scoring creation.
- Runtime DB import must leave 26 plants, 26 simulations, and 26 current scoring rows.
