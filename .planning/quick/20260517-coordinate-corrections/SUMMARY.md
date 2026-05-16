---
status: completed
completed: 2026-05-17
skill: gsd-quick
---

# Coordinate Corrections Summary

Corrected the local seed coordinate for `PLTU Tenayan / Unit 1-2` from the older approximate point to the verified Pekanbaru Tenayan site coordinate used by the GEM import.

## Changed

- `backend/app/seed.py`: updated Tenayan seed latitude/longitude to `0.56437, 101.52345`.
- `backend/tests/test_scoring.py`: updated coordinate regression test.
- Local SQLite runtime database was reseeded so the map API now uses the corrected coordinate.

## Verification

- Audited all current plant coordinates for Indonesia bounding-box issues.
- Confirmed imported GEM latitude/longitude values match their GeoJSON geometry.
- Ran targeted backend coordinate regression test.
- Ran whitespace diff check.
- Ran GSD state validation.
