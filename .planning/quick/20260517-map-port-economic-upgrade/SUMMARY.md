---
status: complete
completed: 2026-05-17
skill: gsd-quick
---

# Map Port Economic Upgrade Summary

## Completed

- Added a backend port-intelligence service using NGA World Port Index for Indonesia and Singapore.
- Enriched unit opportunity GeoJSON with nearest-port name, distance, readiness, proximity, and economic-value score.
- Added map endpoints for:
  - `/api/map/ports`
  - `/api/map/economic-zones`
  - `/api/map/export-corridors`
- Added frontend map layers, toggles, legend, and popups for WPI ports, economic zones, and Singapore export proxy corridors.
- Added `docs/MAP_PORT_INTELLIGENCE_VALIDITY.md` explaining source validity and screening-only assumptions.
- Added backend tests for WPI port normalization and nearest-port distance logic.

## Validation

- `cd backend && .venv/bin/pytest -q` -> 49 passed.
- `cd frontend && npm run build` -> passed.
- `gsd-sdk query state.validate` -> valid.
- API checks:
  - `/api/map/ports` -> 120 ports: 115 Indonesia and 5 Singapore.
  - `/api/map/economic-zones?scheme=align` -> 26 economic zones.
  - `/api/map/export-corridors?scheme=align` -> 6 Singapore export proxy corridors.
  - `/api/map/unit-opportunity?scheme=align` -> 97 unit features with nearest-port enrichment.
