---
status: complete
completed: 2026-05-17
slug: curated-pltu-dataset
---

# Summary

Added a curated PLTU target dataset importer for the 26 requested sites.

## Completed

- Added `backend/app/import_target_pltu.py`.
- Added public source/confidence documentation in `docs/PLTU_CURATED_DATASET_SOURCES.md`.
- Added regression tests in `backend/tests/test_import_target_pltu.py`.
- Updated README with the curated importer command and data-validity warning.
- Ran the importer against the runtime SQLite database.
- Ran full backend tests, API smoke checks, and GSD state validation.

## Notes

- The importer intentionally clears old plant-linked data before seeding the 26 target sites.
- Public sources do not expose measured stack-test data for every site; pollutant fields are seeded as the Permen LHK P.15/2019 existing-coal PLTU regulatory benchmark.
- Ampana remains low-confidence because public sources confirm Desa Sabo/Ampana Tete but no public fence-line coordinate was found.
- Runtime verification: 26 plants, 26 scenarios, 26 simulations, 26 scoring records, and 26 map features.
