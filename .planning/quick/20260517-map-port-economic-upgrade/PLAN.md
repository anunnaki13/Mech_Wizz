---
status: in_progress
created: 2026-05-17
skill: gsd-quick
---

# Map Port Economic Upgrade

## Goal

Upgrade the map from a simple unit point/heatmap view into a port-aware screening map that can show economic concentration areas, Indonesian port readiness, and indicative export corridors to Singapore.

## Scope

- Use GEM PLTU scoring records already in the app as the unit potential base.
- Use NGA World Port Index as the public port dataset for Indonesia and Singapore.
- Calculate nearest-port distance and port readiness from WPI attributes.
- Generate three new GeoJSON layers:
  - Indonesian/Singapore ports.
  - Economic zones aggregated by nearest Indonesian port.
  - Indicative export corridors from highest-potential zones to Singapore.
- Add frontend map controls, styling, and popups for these layers.
- Document data validity tiers and screening assumptions.

## Validation

- Backend tests pass.
- Frontend production build passes.
- New API endpoints return GeoJSON.
- Local production frontend and backend serve the map page.
