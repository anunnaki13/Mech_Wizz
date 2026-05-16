---
phase: 03-strategy-dashboard-ranking
plan: "02"
subsystem: frontend-map-dashboard
tags: [nextjs, maplibre, dashboard, ranking-ui]
requires:
  - phase: 03-strategy-dashboard-ranking
    plan: "01"
    provides: Backend ranking, GeoJSON, profile, and scoring recalculation APIs
provides:
  - /dashboard/map route
  - MapLibre opportunity heatmap and marker layer
  - Scenario/scheme/region/fuel/confidence/opportunity filters
  - Ranking table
  - Selected unit score/profile panel
affects: [phase-3-sensitivity, phase-4-investor-case]
tech-stack:
  added: [maplibre-gl]
  patterns: [client dashboard orchestration, typed backend API helpers, MapLibre GeoJSON source]
key-files:
  created:
    - frontend/app/dashboard/map/page.tsx
    - frontend/components/dashboard/MapDashboard.tsx
    - frontend/components/dashboard/OpportunityMap.tsx
    - frontend/components/dashboard/MapFilters.tsx
    - frontend/components/dashboard/RankingTable.tsx
    - frontend/components/dashboard/ScoreBreakdownPanel.tsx
    - frontend/types/scoring.ts
  modified:
    - frontend/lib/api.ts
    - frontend/app/globals.css
    - frontend/app/layout.tsx
    - frontend/components/layout/AppShell.tsx
    - frontend/package.json
    - frontend/package-lock.json
key-decisions:
  - "Map UI consumes backend ranking, GeoJSON, profile, and recalculate endpoints."
  - "MapLibre GL JS renders the heatmap, marker, and label layers."
  - "Dashboard displays null economics as Not calculated and exposes confidence/data-gap labels."
patterns-established:
  - "Map filters are centralized in DashboardFilters and converted to backend query params."
  - "Ranking row data drives KPI cards, selected profile, table selection, and map selection."
requirements-completed: [UNIT-07, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07]
duration: 10min
completed: 2026-05-16
---

# Phase 3 Plan 02: Map Dashboard Summary

**Implemented `/dashboard/map` as a usable MapLibre strategy dashboard.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-05-16T12:21:04+07:00
- **Completed:** 2026-05-16T12:30:56+07:00
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments

- Installed `maplibre-gl` and imported its CSS through the app layout.
- Added typed API helpers for scoring recalculation, ranking, GeoJSON, and selected unit profile.
- Added `/dashboard/map` route with KPI cards, filters, MapLibre heatmap/circle/label layers, ranking table, and selected unit profile/score breakdown.
- Added navigation link for the map page.
- Added null-safe display labels for CO2, captured CO2, E-Methanol, H2 required, IRR, LCOM, confidence, and data gaps.

## Verification

- `cd frontend && npm run build` - passed.
- `rg -n "maplibre|heatmap|RankingTable|MapDashboard|Composite Score" frontend` - expected matches found.
- Local smoke:
  - `GET /api/health` - 200.
  - `GET /dashboard/map` - 200.
  - `POST /api/scenarios/{scenario_id}/simulate` - 200.
  - `POST /api/scoring/recalculate` - 200, one scoring record created.
  - `GET /api/map/unit-opportunity` - 200, one GeoJSON feature at `[101.5567, 0.5123]`.
  - `GET /api/units/{plant_id}/profile` - 200.

## Notes

- The map basemap uses public OpenStreetMap raster tiles through MapLibre. Ranking and marker data remain backend-authored GeoJSON.
- `npm install maplibre-gl` reported two moderate vulnerabilities in the dependency tree; no forced audit fix was applied because it would allow breaking upgrades.

## Next Plan Readiness

Plan `03-03` can add sensitivity persistence/API and wire the tornado panel into the selected unit detail.

---
*Phase: 03-strategy-dashboard-ranking*
*Completed: 2026-05-16*
