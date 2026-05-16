# Plan 02 Summary: Emission Test Slice

## Status

Complete.

## Delivered

- Added `EmissionTest` SQLAlchemy model with persisted `data_status` and `confidence_level`.
- Added emission test Pydantic schemas and REST endpoints:
  - `GET /api/plants/{plant_id}/emission-tests`
  - `POST /api/plants/{plant_id}/emission-tests`
  - `PUT /api/emission-tests/{emission_test_id}`
  - `DELETE /api/emission-tests/{emission_test_id}`
- Extended Tenayan seed with exactly two idempotent chimney records from the blueprint.
- Added backend tests for emission CRUD and seed idempotency.
- Added frontend emission test type, API helpers, unit detail route, and `EmissionTestsSection` with `Add Emission Test`.

## Verification

- `cd backend && .venv/bin/pytest -q tests/test_emission_tests.py` passed with 2 tests.
- `cd backend && .venv/bin/pytest -q` passed with 5 tests.
- `cd frontend && npm run build` passed.
- Acceptance markers for `Chimney #1`, `Chimney #2`, `EmissionTestsSection`, and `getEmissionTests` are present.

## Notes

- Emission records are stored as input facts only; no CO2 conversion, methanol output, hydrogen, financial, ranking, or sensitivity calculations were added in this phase.
