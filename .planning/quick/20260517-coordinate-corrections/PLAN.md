---
status: in_progress
created: 2026-05-17
skill: gsd-quick
---

# Coordinate Corrections

## Goal

Fix map unit coordinates that are not aligned with verified public map/source coordinates.

## Scope

- Audit current `plants.latitude` and `plants.longitude` values.
- Check public web sources for suspicious units.
- Correct durable seed/import behavior where coordinates are wrong.
- Update local runtime database so the current map reflects the correction.
- Validate backend tests and GSD state.

## Finding

The imported PLN-related operating units use GEM coordinates and their GeoJSON properties match the source geometry. The local seed row `PLTU Tenayan / Unit 1-2` was the clear outlier: it used older coordinates several kilometers away from the GEM exact project coordinate and a geotagged coal-yard photo.
