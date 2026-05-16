# Imported Blueprint Addendum: Heatmap Map

## Source

- Repository: `https://github.com/anunnaki13/Mech_Wizz`
- File: `MECH_WIZ_Heatmap_Map_Addendum.md`
- Commit observed: `eb95a3e05780ac0cfe1ae42ac0595afcb1b61629`
- Imported to: `docs/MECH_WIZ_Heatmap_Map_Addendum.md`
- SHA256: `5077ed367826af898b6bb3962000e5ab8b4d95f9fbdca150dd93d113d11b1ba4`
- Imported at: `2026-05-16T11:16:35+07:00`

## Summary

The addendum defines a dedicated **Map & Heatmap Intelligence Layer** for MECH WIZ. It expands the original strategy dashboard into a concrete map-centric module with:

- MapLibre GL JS as preferred map engine.
- GeoJSON API for unit opportunity features.
- Heatmap layer, circle marker layer, and popup/profile behavior.
- Ranking table synchronized with map selection and filters.
- Separate opportunity, readiness, and confidence scores.
- Composite score and heatmap weight formulas.
- Data gap rules and visible confidence warnings.
- Selected unit profile panel with technical, business, risk, and bottleneck details.
- Investor-friendly map summary generated only from structured calculation data.

## Key Requirements Extracted

- Use `GET /api/map/unit-opportunity` to return GeoJSON `FeatureCollection` data for MapLibre.
- Use score properties in GeoJSON: `opportunity_score`, `readiness_score`, `confidence_score`, `composite_score`, `heatmap_weight`, `rank_position`, and calculated scenario metrics.
- Use heatmap formula:

```text
heatmap_weight =
  (0.45 * opportunity_score)
+ (0.25 * readiness_score)
+ (0.20 * economic_return_score)
+ (0.10 * confidence_score)
```

- Use composite score formula:

```text
composite_score =
  (0.45 * opportunity_score)
+ (0.35 * readiness_score)
+ (0.20 * confidence_score)
```

- Confidence score maps `data_status` values as:

| Data Status | Score |
|---|---:|
| actual | 1.00 |
| estimated | 0.70 |
| benchmark | 0.55 |
| user_assumption | 0.50 |
| partner_supplied | 0.60 |
| unknown | 0.00 |

- Required map filters: scenario, business scheme, region, fuel type, data confidence, opportunity level, and visible layers.
- Required dashboard route from addendum: `/dashboard/map`.

## Conflict Detection

### Schema Split vs Current Phase 1 Schema

The addendum proposes `plant_sites` and `plant_units`, while Phase 1 already implemented a compact `plants` table with `unit_name` and plant/unit fields together.

Resolution:

- Keep the Phase 1 `plants` table as the v1 source for site/unit records.
- Treat addendum `plant_sites` and `plant_units` as conceptual names unless Phase 3 planning finds a strong need for a split migration.
- Add Phase 3 requirements for map/scoring outputs without forcing a Phase 1 schema rewrite.

### Emission Column Naming

The addendum uses `co2_percent` and `gas_velocity_ms`; Phase 1 uses `co2_percent_dry` and `gas_velocity_m_s`.

Resolution:

- Preserve Phase 1 names because they are more explicit and already match the original blueprint.
- Map addendum formulas to existing schema fields during Phase 2 calculation planning.

### Composite Score Formula Change

Current requirements used `60% opportunity + 40% readiness`; the addendum changes this to `45% opportunity + 35% readiness + 20% confidence`.

Resolution:

- Update v1 requirements and Phase 3 roadmap to the addendum formula.
- Keep UI obligation to show all three component scores, preventing confidence from being hidden inside a single score.

### Frontend Stack Specificity

The initial roadmap allowed map/heatmap generally; the addendum recommends MapLibre GL JS.

Resolution:

- Adopt MapLibre GL JS for Phase 3 map implementation.
- Leaflet remains a fallback only if MapLibre is technically blocked.

## Roadmap Impact

- Phase 2 remains focused on deterministic scenario calculations because map scoring depends on scenario outputs.
- Phase 3 becomes the primary home for the Map & Heatmap Intelligence Layer:
  - map GeoJSON endpoint,
  - score calculation,
  - ranking API,
  - `/dashboard/map`,
  - MapLibre heatmap and marker layers,
  - filter synchronization,
  - score breakdown,
  - selected unit profile.
- Phase 4 remains responsible for broader data quality and editable assumptions, but Phase 3 must expose map-level data gaps and confidence labels enough to satisfy the addendum dashboard.
- Phase 5 remains responsible for OpenRouter investor summaries; Phase 3 can prepare structured map insight payloads but should not call LLM unless Phase 5 is active.

## Planning Updates Made

- Stored original addendum in `docs/MECH_WIZ_Heatmap_Map_Addendum.md`.
- Updated `PROJECT.md` context and decisions.
- Updated `REQUIREMENTS.md` with addendum-specific Phase 3 requirements.
- Updated `ROADMAP.md` Phase 3 goal, success criteria, and plan names.
- Updated `STATE.md` accumulated context to record the imported addendum.
