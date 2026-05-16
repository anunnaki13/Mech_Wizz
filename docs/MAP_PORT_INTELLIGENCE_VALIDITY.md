# Map Port Intelligence Validity

Date: 2026-05-17

## What Is Valid Public Data

- PLTU unit identity, public coordinates, capacity, owner/status fields, and public tracker context come from Global Energy Monitor Global Coal Plant Tracker:
  - `https://globalenergymonitor.org/projects/global-coal-plant-tracker/`
  - `https://globalenergymonitor.org/projects/global-coal-plant-tracker/download-data/`
- Port coordinates and maritime facility attributes come from NGA World Port Index:
  - `https://msi.nga.mil/Publications/WPI`
  - Runtime API pattern used by the app: `https://msi.nga.mil/api/publications/world-port-index?countryName=Indonesia&output=json`
- Singapore methanol-bunkering market context is sourced from Maritime and Port Authority of Singapore:
  - `https://www.mpa.gov.sg/media-centre/details/singapore-gears-up-to-meet-net-zero-needs-of-shipping`
  - `https://www.mpa.gov.sg/media-centre/details/singapore-to-award-licences-for-methanol-bunkering`

## What Is Screening Logic, Not Final Validation

- Emission rates, captured CO2, e-methanol output, hydrogen requirement, LCOM, IRR, and CAPEX are deterministic screening assumptions unless the user replaces them with site-specific data.
- Port readiness is a proxy score derived from WPI fields such as harbor size, depth, wharf/cargo facilities, first-port-of-entry flag, tugs, and communications. It is not a terminal capacity study.
- Nearest-port distance is calculated with haversine distance from unit coordinates to WPI port coordinates. It is not road distance, pipeline routing, jetty ownership validation, or nautical routing.
- Economic zones are aggregated around the nearest port using unit methanol potential, CO2 volume, unit score, port readiness, and average distance. They are intended to show concentration areas for prioritization.
- Singapore export corridors are straight-line screening proxies from high-potential Indonesian port zones to the WPI Jurong Island port target. They are not navigational routes, AIS-derived shipping lanes, chartering quotes, or customs/logistics advice.

## UI Meaning

- Unit markers show individual PLTU conversion potential.
- Heatmap shows unit opportunity density.
- Economic-area bubbles show where multiple units plus nearby port readiness create stronger commercial concentration.
- Port markers show WPI ports and readiness tier.
- SG route lines show indicative export paths to Singapore for commercial screening only.

## Required Before Investment Decisions

- PLN or plant-owner confirmation of unit status, retirement plan, available flue gas, tie-in feasibility, land, water, grid, and operating profile.
- Port authority or terminal operator confirmation of berth, draft, hazardous/liquid cargo handling, tankage, methanol compatibility, and expansion rights.
- Engineering pre-FEED for capture, H2 supply, synthesis, storage, and terminal integration.
- Market/offtake validation with Singapore buyers, bunker license holders, or traders.
