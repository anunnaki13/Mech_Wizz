# ADDENDUM BLUEPRINT — Modul Map, Heatmap, Scoring & Unit Selection  
## MECH WIZ AI Digital Twin — Simulation & Decision-Support Engine

**Status dokumen:** Addendum terpisah untuk blueprint utama  
**Tujuan:** Melengkapi blueprint sebelumnya dengan spesifikasi teknis eksplisit untuk fitur **map/heatmap**, **unit scoring**, **site selection**, **ranking unit**, dan **investor-friendly map insight** seperti mockup dashboard.  
**Instruksi untuk Codex/Claude Code:** Jangan mengganti blueprint utama. Terapkan dokumen ini sebagai tambahan modul `Map & Heatmap Intelligence Layer`.

---

## 1. Konteks Addendum

Blueprint utama sudah menjelaskan konsep aplikasi MECH WIZ AI Digital Twin sebagai:

> Pre-Feasibility Simulation & Decision-Support Engine untuk memilih unit pembangkit terbaik berdasarkan potensi CO₂, kesiapan H₂, keekonomian, kesiapan site, logistik, dan skema bisnis.

Addendum ini fokus pada implementasi tampilan seperti mockup:

1. **Peta unit pembangkit Indonesia**
2. **Heatmap peluang ekonomi**
3. **Marker unit pembangkit**
4. **Ranking unit berdasarkan scoring**
5. **Score breakdown per unit**
6. **Sensitivity analysis per unit**
7. **Investor-friendly insight**
8. **Data confidence dan data gap layer**

---

## 2. Tujuan Modul Map & Heatmap

Modul ini harus menjawab pertanyaan utama:

> “Unit pembangkit mana yang paling menarik untuk dijadikan pilot project MECH WIZ berdasarkan potensi ekonomi, ketersediaan CO₂, kesiapan site, logistik, dan risiko data?”

Output utama:

- peta interaktif unit pembangkit,
- heatmap economic opportunity,
- ranking unit,
- detail score per unit,
- opportunity score,
- readiness score,
- confidence score,
- data gap list,
- investor narrative,
- rekomendasi skema bisnis Access / Align / Augment.

---

## 3. Prinsip Desain

### 3.1 Jangan menunggu data sempurna

Aplikasi harus tetap berjalan meskipun sebagian data belum tersedia.

Setiap data wajib punya status:

| Status | Arti |
|---|---|
| `actual` | data aktual/resmi dari unit/lab/laporan |
| `estimated` | estimasi dari rumus sederhana |
| `benchmark` | asumsi industri/default aplikasi |
| `user_assumption` | input manual user |
| `unknown` | belum tersedia |
| `partner_supplied` | diasumsikan disediakan partner |

### 3.2 Pisahkan opportunity dan readiness

Jangan hanya memakai satu skor tunggal.

Gunakan tiga skor utama:

1. **Opportunity Score**  
   Mengukur seberapa besar potensi ekonomi/proyek jika asumsi terpenuhi.

2. **Readiness Score**  
   Mengukur seberapa siap unit dieksekusi sekarang.

3. **Confidence Score**  
   Mengukur seberapa kuat/valid data yang digunakan.

Composite score boleh digunakan untuk ranking, tetapi UI tetap harus menampilkan ketiga skor tersebut.

---

## 4. Rekomendasi Teknologi Frontend Map

### Opsi utama: MapLibre GL JS

Gunakan **MapLibre GL JS** untuk peta interaktif karena:

- mendukung WebGL,
- bisa menampilkan GeoJSON source,
- bisa membuat heatmap layer,
- cocok untuk dashboard modern,
- open-source,
- lebih fleksibel untuk visual high-tech.

### Alternatif: Leaflet + leaflet.heat

Gunakan Leaflet jika ingin implementasi lebih ringan dan sederhana. Namun untuk tampilan premium seperti mockup, MapLibre lebih direkomendasikan.

### Package yang disarankan

```bash
npm install maplibre-gl
npm install @turf/turf
npm install recharts
npm install lucide-react
```

Jika menggunakan Next.js/React:

```bash
npm install maplibre-gl @turf/turf recharts lucide-react
```

---

## 5. Struktur Modul Frontend

Buat modul:

```text
src/
  app/
    dashboard/
      map/
        page.tsx
  components/
    map/
      UnitOpportunityMap.tsx
      UnitMarker.tsx
      HeatmapLayer.tsx
      MapLegend.tsx
      UnitPopup.tsx
      UnitFilterPanel.tsx
    scoring/
      UnitRankingTable.tsx
      ScoreBreakdownRadar.tsx
      ScoreBadge.tsx
      DataConfidenceBadge.tsx
    sensitivity/
      SensitivityTornadoChart.tsx
    investor/
      InvestorInsightPanel.tsx
      InvestmentThesisCard.tsx
  lib/
    map/
      mapStyle.ts
      geojson.ts
    scoring/
      scoringEngine.ts
      scoreWeights.ts
      scoreNormalizer.ts
    calculations/
      co2Calculator.ts
      methanolCalculator.ts
      hydrogenCalculator.ts
      financialCalculator.ts
      sensitivityEngine.ts
  types/
    unit.ts
    scoring.ts
    scenario.ts
```

---

## 6. Data Model Tambahan untuk Map/Heatmap

### 6.1 Tabel `plant_sites`

```sql
CREATE TABLE plant_sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_code VARCHAR(50) UNIQUE NOT NULL,
  site_name VARCHAR(255) NOT NULL,
  province VARCHAR(100),
  city VARCHAR(100),
  latitude DECIMAL(10, 7),
  longitude DECIMAL(10, 7),
  installed_capacity_mw DECIMAL(12, 2),
  fuel_type VARCHAR(50),
  operator_name VARCHAR(255),
  status VARCHAR(50) DEFAULT 'active',
  data_maturity_level VARCHAR(50) DEFAULT 'screening',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Tabel `plant_units`

```sql
CREATE TABLE plant_units (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID REFERENCES plant_sites(id),
  unit_code VARCHAR(50),
  unit_name VARCHAR(255),
  capacity_mw DECIMAL(12, 2),
  cod_year INT,
  operating_status VARCHAR(50),
  capacity_factor DECIMAL(5, 2),
  operating_days_per_year INT DEFAULT 330,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.3 Tabel `geo_assets`

Untuk lokasi cerobong, lahan kosong, pelabuhan, jetty, substation, water source.

```sql
CREATE TABLE geo_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID REFERENCES plant_sites(id),
  asset_type VARCHAR(50) NOT NULL,
  asset_name VARCHAR(255),
  latitude DECIMAL(10, 7),
  longitude DECIMAL(10, 7),
  distance_to_main_stack_km DECIMAL(12, 3),
  distance_to_port_km DECIMAL(12, 3),
  area_ha DECIMAL(12, 2),
  capacity_value DECIMAL(14, 2),
  capacity_unit VARCHAR(50),
  status VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

`asset_type` dapat berisi:

```text
stack
available_land
port
jetty
substation
water_source
road_access
storage_area
residential_area
```

### 6.4 Tabel `emission_tests`

```sql
CREATE TABLE emission_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID REFERENCES plant_sites(id),
  unit_id UUID REFERENCES plant_units(id),
  stack_id VARCHAR(50),
  test_date DATE,
  laboratory_name VARCHAR(255),
  stack_diameter_m DECIMAL(12, 4),
  gas_velocity_ms DECIMAL(12, 4),
  flue_gas_temperature_c DECIMAL(12, 4),
  co2_percent DECIMAL(8, 4),
  o2_percent DECIMAL(8, 4),
  moisture_percent DECIMAL(8, 4),
  so2_mg_nm3 DECIMAL(12, 4),
  nox_mg_nm3 DECIMAL(12, 4),
  particulate_mg_nm3 DECIMAL(12, 4),
  hg_mg_nm3 DECIMAL(12, 6),
  basis VARCHAR(50),
  compliance_status VARCHAR(50),
  data_source_status VARCHAR(50) DEFAULT 'actual',
  confidence_level VARCHAR(50) DEFAULT 'high',
  source_document_id UUID,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.5 Tabel `site_readiness`

```sql
CREATE TABLE site_readiness (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID REFERENCES plant_sites(id),
  land_available BOOLEAN,
  available_land_ha DECIMAL(12, 2),
  port_available BOOLEAN,
  nearest_port_distance_km DECIMAL(12, 3),
  jetty_available BOOLEAN,
  road_access_score DECIMAL(5, 3),
  water_availability_score DECIMAL(5, 3),
  electricity_availability_score DECIMAL(5, 3),
  utility_readiness_score DECIMAL(5, 3),
  permit_risk_level VARCHAR(50),
  social_risk_level VARCHAR(50),
  infrastructure_notes TEXT,
  confidence_level VARCHAR(50) DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.6 Tabel `unit_scoring_results`

```sql
CREATE TABLE unit_scoring_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID REFERENCES plant_sites(id),
  scenario_id UUID,
  opportunity_score DECIMAL(6, 4),
  readiness_score DECIMAL(6, 4),
  confidence_score DECIMAL(6, 4),
  composite_score DECIMAL(6, 4),
  co2_availability_score DECIMAL(6, 4),
  methanol_potential_score DECIMAL(6, 4),
  h2_readiness_score DECIMAL(6, 4),
  economic_return_score DECIMAL(6, 4),
  infrastructure_score DECIMAL(6, 4),
  land_port_score DECIMAL(6, 4),
  market_access_score DECIMAL(6, 4),
  risk_permit_score DECIMAL(6, 4),
  data_gap_count INT DEFAULT 0,
  rank_position INT,
  scoring_version VARCHAR(50) DEFAULT 'v1.0',
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.7 Tabel `data_gaps`

```sql
CREATE TABLE data_gaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID REFERENCES plant_sites(id),
  module_name VARCHAR(100),
  missing_data_name VARCHAR(255),
  impact_level VARCHAR(50),
  priority_level VARCHAR(50),
  recommended_action TEXT,
  status VARCHAR(50) DEFAULT 'open',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. Format GeoJSON untuk Map

Endpoint map harus mengirim data dalam format GeoJSON agar mudah dipakai MapLibre.

### 7.1 Endpoint

```http
GET /api/map/unit-opportunity?scenario=base&scheme=align
```

### 7.2 Response

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "tenayan",
      "geometry": {
        "type": "Point",
        "coordinates": [101.5567, 0.5123]
      },
      "properties": {
        "site_id": "uuid",
        "site_code": "TENAYAN",
        "site_name": "PLTU Tenayan",
        "province": "Riau",
        "capacity_mw": 220,
        "fuel_type": "Coal",
        "opportunity_score": 0.82,
        "readiness_score": 0.61,
        "confidence_score": 0.72,
        "composite_score": 0.74,
        "co2_tpy": 439500,
        "captured_co2_tpy": 374000,
        "methanol_tpy": 163000,
        "h2_strategy": "partner_supplied_electrolyzer",
        "estimated_irr": 0.153,
        "estimated_lcom_usd_ton": 620,
        "rank_position": 1,
        "data_confidence_label": "Medium",
        "heatmap_weight": 0.74,
        "status": "pilot_candidate"
      }
    }
  ]
}
```

---

## 8. Heatmap Logic

### 8.1 Heatmap Weight

Heatmap tidak memakai CO₂ saja. Gunakan `heatmap_weight`.

Formula awal:

```text
heatmap_weight =
  (0.45 * opportunity_score)
+ (0.25 * readiness_score)
+ (0.20 * economic_return_score)
+ (0.10 * confidence_score)
```

Normalisasi hasil ke rentang 0–1.

### 8.2 Kategori Warna

| Score | Kategori | Warna UI |
|---:|---|---|
| 0.00–0.40 | Low Opportunity | Blue |
| 0.40–0.60 | Moderate Opportunity | Cyan/Teal |
| 0.60–0.75 | High Potential | Yellow/Amber |
| 0.75–1.00 | Priority Candidate | Orange/Red |

### 8.3 Layer Visual

Map harus punya 3 layer utama:

1. **Heatmap Layer**  
   Menampilkan intensitas peluang ekonomi.

2. **Circle Marker Layer**  
   Menampilkan marker unit individual.

3. **Label/Popup Layer**  
   Menampilkan nama unit, rank, score, dan key metric.

---

## 9. Pseudocode MapLibre Heatmap

```tsx
import maplibregl from "maplibre-gl";

map.on("load", () => {
  map.addSource("unit-opportunity", {
    type: "geojson",
    data: "/api/map/unit-opportunity?scenario=base&scheme=align"
  });

  map.addLayer({
    id: "unit-opportunity-heatmap",
    type: "heatmap",
    source: "unit-opportunity",
    maxzoom: 9,
    paint: {
      "heatmap-weight": [
        "interpolate",
        ["linear"],
        ["get", "heatmap_weight"],
        0, 0,
        1, 1
      ],
      "heatmap-intensity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        3, 0.7,
        7, 1.8
      ],
      "heatmap-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        3, 18,
        7, 45
      ],
      "heatmap-opacity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        6, 0.85,
        9, 0.35
      ],
      "heatmap-color": [
        "interpolate",
        ["linear"],
        ["heatmap-density"],
        0, "rgba(0, 24, 64, 0)",
        0.2, "rgba(0, 180, 216, 0.45)",
        0.4, "rgba(0, 255, 200, 0.55)",
        0.6, "rgba(255, 214, 10, 0.65)",
        0.8, "rgba(255, 128, 0, 0.75)",
        1.0, "rgba(255, 61, 87, 0.9)"
      ]
    }
  });

  map.addLayer({
    id: "unit-opportunity-circles",
    type: "circle",
    source: "unit-opportunity",
    minzoom: 4,
    paint: {
      "circle-radius": [
        "interpolate",
        ["linear"],
        ["get", "composite_score"],
        0.2, 5,
        1.0, 14
      ],
      "circle-color": [
        "interpolate",
        ["linear"],
        ["get", "composite_score"],
        0.0, "#1d4ed8",
        0.4, "#06b6d4",
        0.6, "#facc15",
        0.75, "#fb923c",
        1.0, "#f43f5e"
      ],
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 1.5,
      "circle-opacity": 0.95
    }
  });
});
```

---

## 10. Unit Marker Behavior

Saat marker diklik, tampilkan popup:

```text
PLTU Tenayan
Rank: #1
Composite Score: 0.74
Opportunity: 0.82
Readiness: 0.61
Confidence: 0.72

CO₂ Available: 439.5 kt/year
Captured CO₂: 374 kt/year
E-Methanol Potential: 163 kt/year
H₂ Strategy: Partner-supplied electrolyzer
Recommended Scheme: WIZ Align

Key Risk:
- H₂ cost is not validated
- CAPEX capture still benchmark
- Offtake not yet binding

Action:
View Site Profile
Run Sensitivity
Generate Investor Summary
```

---

## 11. Scoring Engine

### 11.1 Opportunity Score

```text
opportunity_score =
  (0.30 * co2_availability_score)
+ (0.20 * methanol_potential_score)
+ (0.15 * market_access_score)
+ (0.10 * land_availability_score)
+ (0.10 * utility_advantage_score)
+ (0.05 * carbon_credit_potential_score)
+ (0.10 * strategic_value_score)
```

### 11.2 Readiness Score

```text
readiness_score =
  (0.20 * data_completeness_score)
+ (0.20 * emission_data_quality_score)
+ (0.15 * land_readiness_score)
+ (0.15 * utility_readiness_score)
+ (0.15 * h2_strategy_clarity_score)
+ (0.15 * permit_logistic_readiness_score)
```

### 11.3 Confidence Score

```text
confidence_score =
  average(weighted confidence of required data fields)
```

Confidence mapping:

| Data Status | Score |
|---|---:|
| actual | 1.00 |
| estimated | 0.70 |
| benchmark | 0.55 |
| user_assumption | 0.50 |
| partner_supplied | 0.60 |
| unknown | 0.00 |

### 11.4 Composite Score

```text
composite_score =
  (0.45 * opportunity_score)
+ (0.35 * readiness_score)
+ (0.20 * confidence_score)
```

Catatan:

- `Opportunity Score` boleh tinggi walau data belum lengkap.
- `Readiness Score` dan `Confidence Score` harus turun jika banyak data belum tersedia.
- UI harus menampilkan ketiganya agar tidak misleading.

---

## 12. Normalisasi Score

Gunakan normalisasi min-max untuk metrik kuantitatif.

```ts
function normalize(value: number, min: number, max: number): number {
  if (value === null || value === undefined) return 0;
  if (max === min) return 0.5;
  return Math.max(0, Math.min(1, (value - min) / (max - min)));
}
```

Contoh:

```ts
co2_availability_score = normalize(co2_tpy, 0, 1_000_000);
methanol_potential_score = normalize(methanol_tpy, 0, 300_000);
economic_return_score = normalize(estimated_irr, 0.05, 0.20);
```

---

## 13. Data Gap Engine

Jika data penting kosong atau masih benchmark, sistem harus membuat data gap otomatis.

### 13.1 Aturan Data Gap

```ts
if (!site.latitude || !site.longitude) {
  createDataGap("geo_location", "Unit coordinate is missing", "high", "urgent");
}

if (!emissionTest || emissionTest.confidence_level === "low") {
  createDataGap("emission", "Official stack emission test is missing or low confidence", "high", "urgent");
}

if (h2Strategy === "unknown") {
  createDataGap("hydrogen", "Hydrogen supply strategy is not defined", "very_high", "urgent");
}

if (!siteReadiness.available_land_ha) {
  createDataGap("land", "Available land area is not confirmed", "medium", "medium");
}

if (!financialAssumption.methanol_price_usd_ton) {
  createDataGap("market", "Methanol price assumption is missing", "high", "urgent");
}
```

### 13.2 Output Data Gap Panel

| Missing Data | Impact | Priority | Recommended Action |
|---|---|---|---|
| H₂ cost | Very High | Urgent | Request indicative quote from electrolyzer/H₂ partner |
| CAPEX capture | High | Urgent | Use benchmark until partner proposal is received |
| Offtake status | High | Urgent | Build buyer pipeline and request LOI |
| Land layout | Medium | Medium | Validate available land with O&M/as-built |
| Port capacity | Medium | Medium | Confirm jetty draft and loading capacity |

---

## 14. Ranking Table Specification

Kolom wajib:

| Column | Description |
|---|---|
| Rank | posisi ranking |
| Unit/Site | nama site |
| Province | provinsi |
| Composite Score | skor akhir |
| Opportunity Score | potensi peluang |
| Readiness Score | kesiapan |
| Confidence Score | kualitas data |
| CO₂ Available | ton/tahun |
| E-Methanol Potential | ton/tahun |
| Estimated IRR | indikatif |
| Recommended Scheme | Access/Align/Augment |
| Key Bottleneck | hambatan utama |

Contoh:

```json
[
  {
    "rank": 1,
    "site_name": "PLTU Tenayan",
    "province": "Riau",
    "composite_score": 0.74,
    "opportunity_score": 0.82,
    "readiness_score": 0.61,
    "confidence_score": 0.72,
    "co2_tpy": 439500,
    "methanol_tpy": 163000,
    "estimated_irr": 0.153,
    "recommended_scheme": "WIZ Align",
    "key_bottleneck": "Hydrogen supply"
  }
]
```

---

## 15. Dashboard Page Layout

### 15.1 Page: `/dashboard/map`

Judul:

```text
MECH WIZ AI Digital Twin
Unit Mapping & Opportunity Heatmap
```

### 15.2 Layout

```text
┌─────────────────────────────────────────────────────────────┐
│ Header: Scenario, Scheme, Region, Data Confidence Filter     │
├───────────────────────────────────────┬─────────────────────┤
│                                       │ Unit Ranking Table  │
│         Interactive Map               │                     │
│       + Heatmap Layer                 │ Score Breakdown     │
│       + Unit Marker                   │                     │
│                                       │ Key Insights        │
├───────────────────────────────────────┴─────────────────────┤
│ Sensitivity Tornado Chart + Data Gap Panel                   │
└─────────────────────────────────────────────────────────────┘
```

### 15.3 Top KPI Cards

- Best Candidate Site
- Total CO₂ Available
- Total E-Methanol Potential
- Highest Opportunity Score
- Average Confidence Score
- Recommended Business Scheme

---

## 16. Filter/Control UI

Filter wajib:

| Filter | Options |
|---|---|
| Scenario | Conservative / Base / Optimistic |
| Business Scheme | Access / Align / Augment / Compare All |
| Region | All / Sumatra / Java / Kalimantan / Sulawesi / Nusa Tenggara |
| Fuel Type | Coal / Gas / Biomass / Other |
| Data Confidence | All / High / Medium / Low |
| Opportunity Level | Low / Medium / High / Priority |
| Show Layer | Heatmap / Marker / Label / Infrastructure |

---

## 17. Selected Unit Profile Panel

Saat user memilih unit, tampilkan panel kanan:

```text
PLTU Tenayan
Riau, Indonesia

Composite Score: 0.74
Opportunity Score: 0.82
Readiness Score: 0.61
Confidence Score: 0.72

Technical Potential:
- CO₂ Available: 439.5 kt/year
- Captured CO₂: 374 kt/year
- E-Methanol Potential: 163 kt/year
- Indicative H₂ Required: calculated by engine

Business Case:
- Recommended Scheme: WIZ Align
- Estimated IRR: calculated by scenario
- Indicative LCOM: calculated by scenario
- CAPEX Role: Partner-financed assumption

Data Confidence:
- CO₂: High
- H₂: Low
- CAPEX: Low
- Land: Medium
- Offtake: Low

Key Bottleneck:
- H₂ supply strategy
- CAPEX validation
- Offtake certainty
```

---

## 18. Investor-Friendly Map Insight

Tambahkan tombol:

```text
Generate Investor Summary
```

Ketika diklik, backend mengirim hasil kalkulasi ke LLM via OpenRouter.

### 18.1 Input Prompt ke LLM

```text
You are an investment analyst for MECH WIZ AI Digital Twin.
Generate a concise investor-friendly summary based only on the provided structured data.
Do not invent data. If a value is benchmark or low confidence, explicitly mention it.

Structured data:
{unit_summary_json}

Output format:
1. Investment thesis
2. Why this site ranks high
3. Key economic potential
4. Main risks and mitigations
5. Data confidence warning
6. Recommended next actions
```

### 18.2 Output yang diharapkan

```text
PLTU Tenayan is currently ranked as the top pilot candidate due to strong CO₂ availability, existing power plant infrastructure, and plausible conversion potential into e-methanol. However, the investment case remains dependent on hydrogen supply strategy, partner-provided CAPEX, and offtake validation. The recommended route is WIZ Align, where PLN NP contributes assets while the partner provides technology and financing.
```

---

## 19. Sensitivity Analysis untuk Map Detail

Setiap unit harus bisa menjalankan sensitivity analysis.

### 19.1 Variabel

| Variable | Default Range |
|---|---:|
| H₂ price | ±20% |
| Electricity price | ±20% |
| E-Methanol price | ±20% |
| CAPEX | ±20% |
| Capture rate | ±10% |
| Plant availability | ±10% |
| Carbon credit price | ±50% |
| Exchange rate | ±10% |

### 19.2 Output Chart

Gunakan tornado chart.

Data output:

```json
[
  {
    "variable": "H2 Price",
    "downside_impact_irr_pp": -5.8,
    "upside_impact_irr_pp": 6.2
  },
  {
    "variable": "E-Methanol Price",
    "downside_impact_irr_pp": -4.3,
    "upside_impact_irr_pp": 4.8
  }
]
```

### 19.3 UI Text

```text
Dominant sensitivity driver: H₂ Price
Interpretation: Project IRR is highly exposed to hydrogen cost. Prioritize partner negotiation, long-term power supply, or hybrid H₂ bridge strategy.
```

---

## 20. API Endpoint Tambahan

### 20.1 Map GeoJSON

```http
GET /api/map/unit-opportunity
```

Query params:

```text
scenario=base
scheme=align
region=sumatra
confidence=all
```

### 20.2 Ranking

```http
GET /api/scoring/unit-ranking?scenario=base&scheme=align
```

### 20.3 Selected Unit Profile

```http
GET /api/sites/:siteId/profile?scenario=base&scheme=align
```

### 20.4 Recalculate Scores

```http
POST /api/scoring/recalculate
```

Body:

```json
{
  "scenario_id": "uuid",
  "scheme": "align",
  "region": "all"
}
```

### 20.5 Sensitivity

```http
POST /api/sensitivity/run
```

Body:

```json
{
  "site_id": "uuid",
  "scenario_id": "uuid",
  "variables": [
    {"name": "h2_price", "range": 0.2},
    {"name": "methanol_price", "range": 0.2},
    {"name": "capex", "range": 0.2}
  ]
}
```

### 20.6 Generate Investor Summary

```http
POST /api/llm/investor-summary
```

Body:

```json
{
  "site_id": "uuid",
  "scenario_id": "uuid",
  "scheme": "align"
}
```

---

## 21. Backend Calculation Flow

```text
1. Load plant/unit data
2. Load emission test data
3. Calculate CO₂ availability
4. Apply capture scenario
5. Calculate methanol potential
6. Estimate H₂ required
7. Estimate financial output
8. Calculate opportunity score
9. Calculate readiness score
10. Calculate confidence score
11. Calculate composite score
12. Generate GeoJSON
13. Render heatmap + ranking
```

---

## 22. CO₂ Calculation Reminder

Jika data stack lengkap:

```text
A = π * (diameter / 2)^2

Q_actual = velocity * A

Q_normal = Q_actual * (273.15 / (273.15 + flue_gas_temperature_c))

CO2_wet_fraction = (CO2_dry_percent / 100) * (1 - moisture_percent / 100)

CO2_kg_s = Q_normal * CO2_wet_fraction * 1.964

CO2_ton_hour = CO2_kg_s * 3600 / 1000

CO2_ton_day = CO2_ton_hour * 24

CO2_ton_year = CO2_ton_day * operating_days_per_year
```

Jika data stack belum tersedia:

```text
CO2_ton_year = installed_capacity_mw * capacity_factor * operating_hours_per_year * emission_factor_tco2_mwh
```

---

## 23. Methanol Potential Reminder

Stoikiometri dasar:

```text
CO2 + 3H2 → CH3OH + H2O
```

Teoritis:

```text
1 ton CO2 → 0.727 ton methanol
1 ton methanol membutuhkan ±1.375 ton CO2
1 ton methanol membutuhkan ±0.1875 ton H2
```

Dengan efisiensi proses:

```text
methanol_tpy = captured_co2_tpy * 0.727 * process_efficiency
```

Kebutuhan H₂ indikatif:

```text
h2_required_tpy = methanol_tpy * 0.1875 / h2_utilization_efficiency
```

---

## 24. UI Style Guide untuk Map Dashboard

Gunakan visual sesuai mockup:

### 24.1 Warna

```text
Background: #020617 / #07111f
Panel: rgba(15, 23, 42, 0.78)
Border: rgba(56, 189, 248, 0.25)
Primary Cyan: #22d3ee
Teal: #14b8a6
Blue: #3b82f6
Amber: #facc15
Orange: #fb923c
Red/Pink: #f43f5e
Success Green: #22c55e
Muted Text: #94a3b8
White Text: #f8fafc
```

### 24.2 Komponen

- Card rounded `2xl`
- Glassmorphism
- Subtle glow
- Thin grid lines
- Dark premium background
- High-contrast KPI
- Compact table
- Neon-accent marker
- Smooth hover transitions

### 24.3 UX

- Map tidak boleh terlalu ramai.
- Ranking table harus bisa scroll.
- Detail panel muncul saat unit dipilih.
- Tooltip harus singkat dan jelas.
- Confidence badge wajib tampil.
- Data gap harus terlihat, bukan disembunyikan.

---

## 25. Acceptance Criteria untuk Codex

Modul dianggap selesai jika:

1. Dashboard map dapat menampilkan seluruh unit dalam database.
2. Heatmap berubah sesuai `composite_score` atau `heatmap_weight`.
3. Marker warna berubah sesuai kategori peluang.
4. Klik marker membuka popup/site profile.
5. Ranking table tersinkron dengan map.
6. Filter scenario/scheme mengubah heatmap dan ranking.
7. Unit selected menampilkan score breakdown.
8. Sensitivity chart dapat dijalankan untuk unit selected.
9. Investor summary dapat dibuat oleh LLM dari structured data.
10. Data confidence dan data gap ditampilkan jelas.
11. Tidak ada hasil yang ditampilkan tanpa label `actual/estimated/benchmark/unknown`.
12. UI mengikuti gaya modern, high-tech, clean, premium, dan profesional seperti mockup.

---

## 26. Development Sequence

Urutan kerja yang disarankan:

### Phase 1 — Static Prototype

- Buat map page.
- Tambahkan dummy GeoJSON unit.
- Tampilkan marker dan heatmap.
- Buat ranking table dummy.
- Buat selected unit profile dummy.

### Phase 2 — Database Integration

- Buat tabel `plant_sites`, `plant_units`, `emission_tests`, `site_readiness`.
- Buat endpoint GeoJSON.
- Ambil data dari database.

### Phase 3 — Scoring Engine

- Implement scoring engine.
- Generate opportunity/readiness/confidence/composite score.
- Update heatmap berdasarkan score.

### Phase 4 — Sensitivity

- Implement simple financial model.
- Implement tornado chart.
- Hubungkan dengan selected unit.

### Phase 5 — LLM Investor Summary

- Buat endpoint OpenRouter.
- Kirim structured unit data.
- Generate investor summary.
- Tambahkan warning jika data confidence rendah.

### Phase 6 — Polish UI

- Sesuaikan style dengan mockup.
- Tambahkan animations, loading state, empty state, dan error state.

---

## 27. Dummy Data untuk Awal

Gunakan dummy data ini untuk testing awal:

```json
[
  {
    "site_code": "TENAYAN",
    "site_name": "PLTU Tenayan",
    "province": "Riau",
    "latitude": 0.5123,
    "longitude": 101.5567,
    "capacity_mw": 220,
    "co2_tpy": 439500,
    "captured_co2_tpy": 374000,
    "methanol_tpy": 163000,
    "opportunity_score": 0.82,
    "readiness_score": 0.61,
    "confidence_score": 0.72,
    "composite_score": 0.74,
    "recommended_scheme": "WIZ Align",
    "key_bottleneck": "Hydrogen supply"
  },
  {
    "site_code": "UNIT_B",
    "site_name": "PLTU Unit B",
    "province": "Banten",
    "latitude": -5.92,
    "longitude": 106.02,
    "capacity_mw": 600,
    "co2_tpy": 900000,
    "captured_co2_tpy": 630000,
    "methanol_tpy": 220000,
    "opportunity_score": 0.79,
    "readiness_score": 0.55,
    "confidence_score": 0.45,
    "composite_score": 0.65,
    "recommended_scheme": "WIZ Access",
    "key_bottleneck": "Data confidence"
  },
  {
    "site_code": "UNIT_C",
    "site_name": "PLTU Unit C",
    "province": "East Java",
    "latitude": -7.72,
    "longitude": 113.58,
    "capacity_mw": 800,
    "co2_tpy": 1100000,
    "captured_co2_tpy": 770000,
    "methanol_tpy": 280000,
    "opportunity_score": 0.86,
    "readiness_score": 0.48,
    "confidence_score": 0.40,
    "composite_score": 0.64,
    "recommended_scheme": "WIZ Access",
    "key_bottleneck": "H₂ strategy and permit"
  }
]
```

---

## 28. Notes Penting

1. Jangan menampilkan angka seolah-olah final jika statusnya benchmark.
2. Jangan biarkan LLM menghitung angka teknis/finansial secara bebas.
3. LLM hanya boleh menjelaskan hasil structured calculation.
4. Heatmap harus merepresentasikan skor, bukan sekadar CO₂.
5. Data confidence wajib terlihat di dashboard.
6. Ranking unit harus bisa berubah ketika scenario/scheme berubah.
7. Tenayan dapat digunakan sebagai pilot dummy/default site.
8. Semua formula harus tersentral di backend/lib calculations, bukan tersebar di UI.

---

## 29. Ringkasan untuk Developer

Bangun modul:

> **Map & Heatmap Intelligence Layer**

Dengan kemampuan:

- render peta Indonesia,
- tampilkan unit pembangkit,
- hitung opportunity/readiness/confidence/composite score,
- tampilkan heatmap berdasarkan score,
- ranking unit,
- selected unit detail,
- sensitivity analysis,
- data gap,
- investor summary via LLM.

Output akhir harus menyerupai mockup dashboard MECH WIZ AI Digital Twin yang modern, high-tech, clean, premium, dan profesional.

