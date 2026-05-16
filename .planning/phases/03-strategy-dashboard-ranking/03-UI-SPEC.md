# Phase 3 UI Spec: Strategy Dashboard & Ranking

## Page

`/dashboard/map`

## Intent

Provide a usable site-selection cockpit: map, ranking, score breakdown, selected unit profile, and sensitivity access in one operational screen.

## Layout

- AppShell sidebar/topbar remains.
- Page header: "Map & Heatmap Intelligence".
- KPI strip:
  - Best Candidate Site
  - Total CO2 Available
  - Total E-Methanol Potential
  - Highest Opportunity Score
  - Average Confidence Score
  - Recommended Business Scheme
- Compact filter toolbar below KPI strip.
- Main area:
  - Left: MapLibre map panel.
  - Middle/bottom: ranking table.
  - Right: selected unit profile and score breakdown.
- Sensitivity panel appears for selected unit in plan 03-03.

## Controls

- Scenario selector from real backend scenarios.
- Scheme segmented/select control: Access, Align, Augment, Compare All.
- Region select.
- Fuel type select.
- Data confidence select.
- Opportunity level select.
- Layer toggles: Heatmap, Marker, Label.

## Map Behavior

- Heatmap layer uses `heatmap_weight`.
- Circle markers use `composite_score` category color.
- Click marker selects unit and updates profile/ranking selection.
- Popup/profile shows rank, composite, opportunity, readiness, confidence, CO2, captured CO2, methanol, H2, recommended scheme, and key bottleneck.
- Empty coordinate records are excluded from map and surfaced in data warnings.

## Ranking Table

Required columns:

- Rank
- Unit/Site
- Province
- Composite Score
- Opportunity
- Readiness
- Confidence
- CO2 Available
- E-Methanol Potential
- Estimated IRR
- Recommended Scheme
- Key Bottleneck

## Visual Contract

- Dark operational palette, not a landing page.
- Use existing cyan/teal/amber colors and add red/orange status colors only where needed.
- Cards stay at 8px radius to match current app.
- No nested decorative cards.
- Text must fit on desktop and mobile.
- Map panel must have stable height and not collapse during loading.

## Data Labels

- Result and score panels must show confidence labels.
- Null economics display "Not calculated".
- Benchmark/user-assumption data must remain visibly labeled.
