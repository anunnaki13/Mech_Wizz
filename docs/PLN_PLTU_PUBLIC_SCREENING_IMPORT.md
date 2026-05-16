# PLN PLTU Public Screening Import

Date: 2026-05-17

## Scope

The import loads operating Indonesian coal-fired units that are related to PLN, PLN Indonesia Power, PLN Nusantara Power, legacy Indonesia Power/PJB naming, or PLN ownership participation.

This is a public screening dataset, not a validated engineering data room. Fields that are not available publicly are populated as benchmark assumptions and explicitly marked with low confidence.

## Sources

- Global Energy Monitor Global Coal Plant Tracker, January 2026 map dataset:
  `https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/interim_maps/gcpt_map_2026-01.geojson`
- GEM tracker page:
  `https://globalenergymonitor.org/projects/global-coal-plant-tracker/`
- GEM data download/license page:
  `https://globalenergymonitor.org/projects/global-coal-plant-tracker/download-data/`
- PLN RUPTL 2025-2034 context:
  `https://web.pln.co.id/cms/media/siaran-pers/2025/05/tingkatkan-bauran-ebt-hingga-2034-pln-siap-jalankan-ruptl-terhijau-sepanjang-sejarah/`

## Import Result

- Indonesia coal units in GEM source: 526
- Indonesia operating coal units in GEM source: 287
- PLN-related operating units imported: 96
- Scenarios created/updated: 96
- Simulation failures: 0
- Latest scoring records visible in map after import: 97, including the original Tenayan seed scenario

## Assumptions

- Unit identity, capacity, province, coordinates, owner, and operating status are sourced from GEM.
- Fuel type is set to `coal`.
- Plant records use `data_status=estimated` and `confidence_level=medium`.
- Emission tests are generated as benchmark stack records calibrated to capacity using:
  - capacity factor: 0.80
  - operating days/year: 330
  - benchmark coal emission factor: 0.95 tCO2/MWh
  - dry CO2: 12%
  - moisture: 8%
  - gas velocity: 18 m/s
  - flue gas temperature: 120 C
- Site readiness, hydrogen strategy, and CAPEX are benchmark screening assumptions with `confidence_level=low`.
- Scenario is `WIZ Align Public PLTU Screening`.

## How To Re-run

```bash
cd backend
.venv/bin/python -m app.import_pln_pltu
```

The script is idempotent for plant, scenario, financial, emission, site-readiness, and hydrogen records. Each run creates a fresh simulation/scoring result so changes can be compared over time.

## UI Impact

The map now defaults to `All scenarios`, so `/dashboard/map` uses all imported scoring records immediately. Use the Scenario dropdown to narrow to a single unit scenario when needed.
