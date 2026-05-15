# Blueprint Aplikasi — MECH WIZ AI Digital Twin

**Nama Produk:** MECH WIZ AI Digital Twin  
**Subtitle:** Simulation & Decision-Support Engine  
**Versi Blueprint:** v1.0 — MVP / Pre-Feasibility Mode  
**Target Pengguna:** Tim Business Development, MMRK, Engineering, Manajemen PLN NP, calon partner, dan investor  
**Tujuan Dokumen:** Menjadi arahan teknis untuk Codex/Claude Code dalam membangun aplikasi web dashboard berbasis data, simulasi, scoring, sensitivity analysis, dan LLM insight.

---

## 1. Ringkasan Eksekutif

MECH WIZ AI Digital Twin adalah aplikasi **pre-feasibility simulation and decision-support engine** untuk memetakan potensi unit pembangkit PLN NP sebagai kandidat proyek **e-methanol / carbon-to-fuel**.

Aplikasi ini belum dirancang sebagai full operational digital twin berbasis data real-time DCS/SCADA. Pada fase awal, aplikasi dirancang untuk bekerja dengan data yang masih terbatas, seperti:

- detail unit pembangkit,
- geolokasi,
- hasil uji emisi/kualitas udara,
- data cerobong,
- data lahan,
- akses pelabuhan/logistik,
- data utilitas sederhana,
- asumsi bisnis,
- benchmark teknis dan finansial.

Aplikasi harus tetap bisa berjalan meskipun data reactor methanol, hydrogen plant, vendor EPC, FEED, CAPEX detail, atau offtake contract belum tersedia.

Prinsip utama:

> **Data aktual digunakan jika tersedia. Data yang belum tersedia diganti dengan assumption library, ditandai sebagai asumsi, diberi confidence level, dan dimunculkan sebagai data gap.**

---

## 2. Tujuan Produk

Aplikasi memiliki dua output utama.

### 2.1 Output 1 — Unit Mapping & Economic Site Selection

Aplikasi harus menampilkan pemetaan unit pembangkit untuk memilih unit dengan nilai ekonomi terbaik.

Fitur utama:

1. peta unit pembangkit,
2. heatmap economic opportunity,
3. scoring unit,
4. ranking unit,
5. opportunity score,
6. readiness score,
7. composite score,
8. CO₂ potential,
9. H₂ gap estimator,
10. e-methanol potential,
11. sensitivity analysis,
12. data confidence,
13. data gap analysis.

### 2.2 Output 2 — Investor-Friendly Dashboard

Aplikasi harus mampu menghasilkan informasi yang ramah investor dan manajemen.

Fitur utama:

1. investment thesis,
2. selected pilot site,
3. IRR indikatif,
4. NPV indikatif,
5. LCOM indikatif,
6. payback period indikatif,
7. CAPEX structure,
8. revenue mix,
9. scenario comparison: WIZ Access vs WIZ Align vs WIZ Augment,
10. key risks & mitigation,
11. roadmap to scale,
12. why this project wins,
13. AI-generated investor summary.

---

## 3. Positioning Aplikasi

Aplikasi ini **bukan** sekadar dashboard visual.

Aplikasi ini adalah gabungan dari:

1. **calculation engine**  
   menghitung CO₂, H₂, e-methanol, LCOM, IRR, NPV, payback, scoring, dan sensitivity.

2. **decision-support engine**  
   membantu memilih unit terbaik dan skenario bisnis terbaik.

3. **assumption-driven simulator**  
   memungkinkan proyek tetap disimulasikan walau data belum lengkap.

4. **LLM insight layer**  
   menggunakan OpenRouter untuk menjelaskan hasil, membuat insight, menyusun investor summary, dan menampilkan rekomendasi.

5. **document intelligence layer**  
   membaca dokumen pendukung seperti laporan uji emisi, PDF, proposal partner, market report, dan dokumen internal lain.

---

## 4. Prinsip Penting Pengembangan

### 4.1 LLM Tidak Boleh Menjadi Kalkulator Utama

Jangan menghitung angka teknis/finansial utama langsung dengan LLM.

Perhitungan deterministik wajib dilakukan oleh backend calculation engine.

LLM hanya digunakan untuk:

- menjelaskan hasil,
- membuat narasi,
- membuat executive summary,
- menyusun insight,
- membuat daftar data gap,
- membandingkan skenario secara naratif,
- membantu ekstraksi data dari dokumen,
- menjelaskan sensitivity analysis.

### 4.2 Setiap Data Harus Punya Data Status

Setiap input penting harus memiliki `data_status`:

| Status | Arti |
|---|---|
| `actual` | data resmi/aktual dari unit/laporan |
| `estimated` | data estimasi internal |
| `benchmark` | asumsi benchmark industri |
| `user_assumption` | asumsi manual user |
| `unknown` | belum tersedia |
| `partner_supplied` | diasumsikan akan disediakan partner |

### 4.3 Setiap Output Harus Punya Confidence Level

Setiap output penting harus memiliki `confidence_level`:

| Level | Arti |
|---|---|
| `high` | mayoritas input aktual/resmi |
| `medium` | campuran aktual dan estimasi |
| `low` | mayoritas benchmark/asumsi |
| `unknown` | data terlalu minim |

### 4.4 Aplikasi Harus Bisa Jalan Walau Data Belum Lengkap

Jika data tidak tersedia:

- gunakan default assumption,
- tandai hasil sebagai `low confidence`,
- tampilkan data gap,
- tampilkan rekomendasi data yang perlu dikumpulkan.

---

## 5. Tech Stack yang Disarankan

User menyebut akan menggunakan:

- OpenRouter,
- VPS,
- Codex,
- Claude Code.

Rekomendasi stack:

### 5.1 Frontend

**Pilihan utama:** Next.js + React + TypeScript

Library UI:

- Tailwind CSS,
- shadcn/ui,
- Recharts,
- Mapbox GL JS atau Leaflet,
- Framer Motion,
- Lucide Icons.

Alasan:

- mudah dibangun dengan Codex/Claude Code,
- cocok untuk dashboard modern,
- mudah deploy ke VPS,
- mudah integrasi API.

### 5.2 Backend

**Pilihan utama:** FastAPI + Python

Alasan:

- cocok untuk calculation engine,
- kuat untuk scientific/financial calculations,
- mudah integrasi pandas/numpy,
- mudah integrasi LLM dan document extraction.

Alternatif:

- Node.js/NestJS jika ingin full TypeScript.

Namun untuk aplikasi simulasi teknis/finansial, **Python FastAPI lebih disarankan**.

### 5.3 Database

**MVP:**

- PostgreSQL

**Jika nanti ada time-series:**

- PostgreSQL + TimescaleDB

**Untuk dokumen dan RAG:**

- pgvector di PostgreSQL, atau
- Qdrant jika ingin vector database terpisah.

### 5.4 Object Storage

Untuk dokumen PDF/Excel:

- local VPS storage untuk MVP,
- MinIO untuk production,
- S3-compatible storage jika tersedia.

### 5.5 LLM

Melalui OpenRouter.

Gunakan LLM untuk:

- investor summary,
- data gap explanation,
- scenario explanation,
- risk explanation,
- document Q&A.

### 5.6 Deployment

Di VPS:

- Docker Compose,
- Nginx Reverse Proxy,
- HTTPS via Certbot,
- PostgreSQL container,
- Backend FastAPI container,
- Frontend Next.js container,
- Worker container untuk document parsing / embeddings.

---

## 6. Arsitektur Sistem

```text
┌─────────────────────────────┐
│         Frontend UI          │
│ Next.js + Tailwind + Charts  │
└──────────────┬──────────────┘
               │ REST/JSON
┌──────────────▼──────────────┐
│        Backend API           │
│ FastAPI Calculation Engine   │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│       PostgreSQL DB          │
│ Units, Scenarios, Results    │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│ Document & Vector Layer      │
│ PDFs, Excel, RAG, pgvector   │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│         OpenRouter LLM       │
│ Insight, Summary, Q&A        │
└─────────────────────────────┘
```

---

## 7. Modul Aplikasi

### 7.1 Unit Database Module

Fungsi:

- menyimpan data unit pembangkit,
- lokasi,
- kapasitas,
- bahan bakar,
- status operasi,
- data readiness.

Output:

- daftar unit,
- unit profile,
- marker di peta,
- basis scoring.

### 7.2 Emission Data Module

Fungsi:

- input hasil pengujian kualitas udara/emisi,
- data cerobong,
- CO₂ concentration,
- gas velocity,
- suhu,
- moisture,
- O₂,
- SO₂,
- NOx,
- particulate,
- Hg.

Output:

- CO₂ ton/jam,
- CO₂ ton/hari,
- CO₂ ton/tahun,
- flue gas quality score,
- capture compatibility flag.

### 7.3 CO₂ Potential Calculator

Fungsi:

- menghitung potensi CO₂ tersedia,
- menghitung potensi CO₂ tertangkap berdasarkan capture rate,
- menampilkan skenario capture.

Output:

- captured CO₂,
- vented CO₂,
- capture potential,
- carbon availability score.

### 7.4 Methanol Potential Calculator

Fungsi:

- menghitung potensi e-methanol dari CO₂ captured,
- menghitung kebutuhan H₂,
- menghitung methanol output berdasarkan efisiensi proses.

Output:

- e-methanol ton/hari,
- e-methanol ton/tahun,
- H₂ requirement,
- H₂ gap.

### 7.5 Hydrogen Strategy Module

Fungsi:

- bukan untuk memasukkan data H₂ lengkap,
- melainkan menentukan strategi H₂.

Input:

- existing H₂: yes/no/unknown,
- strategy: partner electrolyzer / blue H₂ bridge / buy H₂ / hybrid / unknown,
- cost assumption: conservative/base/optimistic,
- readiness score.

Output:

- H₂ readiness,
- H₂ gap,
- estimated electrolyzer size,
- key risk flag.

### 7.6 Site Readiness Module

Fungsi:

- mengukur kesiapan lahan, pelabuhan, utilitas, permit, sosial, dan logistik.

Output:

- land score,
- port/logistics score,
- infrastructure score,
- readiness score.

### 7.7 Business Scheme Module

Membandingkan:

1. WIZ Access,
2. WIZ Align,
3. WIZ Augment.

Output:

- risk-return profile,
- CAPEX responsibility,
- PLN ownership,
- revenue share,
- recommended scheme.

### 7.8 Financial Simulation Module

Fungsi:

- revenue estimation,
- CAPEX/OPEX estimation,
- LCOM,
- IRR,
- NPV,
- payback.

Output:

- investor KPI,
- scenario comparison,
- break-even methanol price,
- financial confidence.

### 7.9 Scoring & Ranking Engine

Fungsi:

- menghitung opportunity score,
- readiness score,
- composite score,
- ranking unit.

Output:

- heatmap score,
- ranking table,
- site recommendation.

### 7.10 Sensitivity Analysis Module

Fungsi:

- menguji perubahan variabel kunci.

Variabel:

- H₂ price,
- electricity price,
- methanol price,
- CAPEX,
- capture rate,
- plant availability,
- carbon price,
- exchange rate.

Output:

- tornado chart,
- IRR impact,
- LCOM impact,
- key risk driver.

### 7.11 Investor Dashboard Module

Fungsi:

- mengubah hasil simulasi menjadi tampilan investor-friendly.

Output:

- selected pilot site,
- IRR,
- NPV,
- LCOM,
- payback,
- CAPEX structure,
- revenue mix,
- risk matrix,
- investment thesis,
- roadmap.

### 7.12 LLM Insight Module

Fungsi:

- membuat insight otomatis dari hasil simulasi.

Output:

- executive summary,
- key insights,
- risk explanation,
- data gap explanation,
- investor memo,
- next action plan.

---

## 8. Data Input MVP

### 8.1 Unit Profile

```json
{
  "plant_name": "PLTU Tenayan",
  "unit_name": "Unit 1-2",
  "province": "Riau",
  "city": "Pekanbaru",
  "latitude": -0.0,
  "longitude": 101.0,
  "capacity_mw": 220,
  "fuel_type": "coal",
  "status": "active",
  "capacity_factor": 0.90,
  "operating_days_per_year": 330,
  "owner": "PLN NP",
  "data_status": "actual"
}
```

### 8.2 Emission Test Data

```json
{
  "plant_id": "uuid",
  "stack_id": "Chimney #1",
  "test_date": "2026-02-06",
  "lab_name": "SUCOFINDO",
  "stack_diameter_m": 3.0,
  "gas_velocity_m_s": 14.4,
  "flue_gas_temperature_c": 124,
  "co2_percent_dry": 8.48,
  "o2_percent": 9.54,
  "moisture_percent": 5.84,
  "so2_mg_nm3": 233,
  "nox_mg_nm3": 263,
  "particulate_mg_nm3": 55.4,
  "hg_mg_nm3": null,
  "compliance_status": "comply",
  "data_status": "actual"
}
```

### 8.3 Site Readiness

```json
{
  "plant_id": "uuid",
  "available_land_ha": 10,
  "land_status": "owned",
  "distance_to_stack_km": 0.5,
  "has_port_or_jetty": true,
  "distance_to_port_km": 2.0,
  "road_access": "good",
  "water_availability": "medium",
  "power_availability": "high",
  "utility_readiness": "medium",
  "permit_risk": "medium",
  "social_risk": "low",
  "data_status": "estimated"
}
```

### 8.4 Hydrogen Strategy

```json
{
  "plant_id": "uuid",
  "existing_h2_available": false,
  "h2_strategy": "partner_supplied_electrolyzer",
  "h2_cost_case": "base",
  "h2_cost_usd_per_kg": 3.0,
  "h2_readiness_score": 0.45,
  "data_status": "benchmark",
  "confidence_level": "low"
}
```

### 8.5 Business Scenario

```json
{
  "scenario_name": "WIZ Align Base Case",
  "scheme": "align",
  "pln_ownership_percent": 25,
  "partner_capex_responsibility_percent": 100,
  "pln_capex_responsibility_percent": 0,
  "revenue_model": "equity_share_plus_asset_revenue",
  "data_status": "user_assumption"
}
```

### 8.6 Financial Assumptions

```json
{
  "methanol_price_usd_per_ton": 1250,
  "grey_methanol_price_usd_per_ton": 350,
  "hydrogen_price_usd_per_kg": 3.0,
  "electricity_price_usd_per_kwh": 0.06,
  "carbon_credit_price_idr_per_ton": 58800,
  "exchange_rate_idr_usd": 17500,
  "discount_rate": 0.10,
  "tax_rate": 0.22,
  "capex_capture_usd": null,
  "capex_electrolyzer_usd": null,
  "capex_methanol_plant_usd": null,
  "opex_percent_capex": 0.04,
  "data_status": "benchmark"
}
```

---

## 9. Data Model Database

Gunakan PostgreSQL.

### 9.1 Tabel `plants`

```sql
CREATE TABLE plants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_name TEXT NOT NULL,
    unit_name TEXT,
    province TEXT,
    city TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    capacity_mw NUMERIC,
    fuel_type TEXT,
    status TEXT,
    capacity_factor NUMERIC,
    operating_days_per_year NUMERIC,
    owner TEXT,
    data_status TEXT DEFAULT 'unknown',
    confidence_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 9.2 Tabel `emission_tests`

```sql
CREATE TABLE emission_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID REFERENCES plants(id) ON DELETE CASCADE,
    stack_id TEXT,
    test_date DATE,
    lab_name TEXT,
    stack_diameter_m NUMERIC,
    gas_velocity_m_s NUMERIC,
    flue_gas_temperature_c NUMERIC,
    co2_percent_dry NUMERIC,
    o2_percent NUMERIC,
    moisture_percent NUMERIC,
    so2_mg_nm3 NUMERIC,
    nox_mg_nm3 NUMERIC,
    particulate_mg_nm3 NUMERIC,
    hg_mg_nm3 NUMERIC,
    compliance_status TEXT,
    data_status TEXT DEFAULT 'unknown',
    confidence_level TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.3 Tabel `site_readiness`

```sql
CREATE TABLE site_readiness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID REFERENCES plants(id) ON DELETE CASCADE,
    available_land_ha NUMERIC,
    land_status TEXT,
    distance_to_stack_km NUMERIC,
    has_port_or_jetty BOOLEAN,
    distance_to_port_km NUMERIC,
    port_capacity_dwt NUMERIC,
    road_access TEXT,
    water_availability TEXT,
    power_availability TEXT,
    utility_readiness TEXT,
    permit_risk TEXT,
    social_risk TEXT,
    data_status TEXT DEFAULT 'unknown',
    confidence_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.4 Tabel `hydrogen_strategies`

```sql
CREATE TABLE hydrogen_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID REFERENCES plants(id) ON DELETE CASCADE,
    existing_h2_available BOOLEAN,
    h2_strategy TEXT,
    h2_cost_case TEXT,
    h2_cost_usd_per_kg NUMERIC,
    h2_readiness_score NUMERIC,
    data_status TEXT DEFAULT 'benchmark',
    confidence_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.5 Tabel `financial_assumptions`

```sql
CREATE TABLE financial_assumptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID,
    methanol_price_usd_per_ton NUMERIC,
    grey_methanol_price_usd_per_ton NUMERIC,
    hydrogen_price_usd_per_kg NUMERIC,
    electricity_price_usd_per_kwh NUMERIC,
    carbon_credit_price_idr_per_ton NUMERIC,
    exchange_rate_idr_usd NUMERIC,
    discount_rate NUMERIC,
    tax_rate NUMERIC,
    capex_capture_usd NUMERIC,
    capex_electrolyzer_usd NUMERIC,
    capex_methanol_plant_usd NUMERIC,
    capex_storage_port_usd NUMERIC,
    opex_percent_capex NUMERIC,
    data_status TEXT DEFAULT 'benchmark',
    confidence_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.6 Tabel `business_scenarios`

```sql
CREATE TABLE business_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID REFERENCES plants(id) ON DELETE CASCADE,
    scenario_name TEXT,
    scheme TEXT,
    pln_ownership_percent NUMERIC,
    partner_capex_responsibility_percent NUMERIC,
    pln_capex_responsibility_percent NUMERIC,
    revenue_model TEXT,
    data_status TEXT DEFAULT 'user_assumption',
    confidence_level TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.7 Tabel `scenario_results`

```sql
CREATE TABLE scenario_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES business_scenarios(id) ON DELETE CASCADE,
    total_co2_ton_per_year NUMERIC,
    captured_co2_ton_per_year NUMERIC,
    methanol_ton_per_year NUMERIC,
    h2_required_ton_per_year NUMERIC,
    electrolyzer_required_mw NUMERIC,
    gross_revenue_usd_per_year NUMERIC,
    lcom_usd_per_ton NUMERIC,
    npv_usd NUMERIC,
    irr NUMERIC,
    payback_years NUMERIC,
    opportunity_score NUMERIC,
    readiness_score NUMERIC,
    composite_score NUMERIC,
    confidence_level TEXT DEFAULT 'low',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.8 Tabel `sensitivity_results`

```sql
CREATE TABLE sensitivity_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES business_scenarios(id) ON DELETE CASCADE,
    variable_name TEXT,
    base_value NUMERIC,
    low_value NUMERIC,
    high_value NUMERIC,
    irr_low NUMERIC,
    irr_high NUMERIC,
    npv_low NUMERIC,
    npv_high NUMERIC,
    lcom_low NUMERIC,
    lcom_high NUMERIC,
    impact_score NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.9 Tabel `documents`

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plant_id UUID REFERENCES plants(id) ON DELETE SET NULL,
    filename TEXT,
    file_type TEXT,
    storage_path TEXT,
    document_category TEXT,
    upload_status TEXT DEFAULT 'uploaded',
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 9.10 Tabel `llm_insights`

```sql
CREATE TABLE llm_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES business_scenarios(id) ON DELETE CASCADE,
    insight_type TEXT,
    prompt TEXT,
    response TEXT,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 10. Rumus Calculation Engine

### 10.1 Luas Penampang Cerobong

```text
A = π × (D / 2)^2
```

Keterangan:

- A = luas penampang cerobong, m²
- D = diameter cerobong, m

### 10.2 Normalized Gas Flow

```text
Q_normal = velocity × area × (273.15 / (273.15 + temperature_c))
```

Keterangan:

- Q_normal = Nm³/s
- velocity = m/s
- area = m²
- temperature_c = °C

### 10.3 CO₂ Wet Basis

```text
CO2_wet_fraction = (CO2_dry_percent / 100) × (1 - moisture_percent / 100)
```

### 10.4 CO₂ Mass Flow

```text
CO2_kg_s = Q_normal × CO2_wet_fraction × CO2_density
```

Default:

```text
CO2_density = 1.964 kg/Nm³
```

### 10.5 CO₂ Ton per Day

```text
CO2_ton_day = CO2_kg_s × 86400 / 1000
```

### 10.6 CO₂ Ton per Year

```text
CO2_ton_year = CO2_ton_day × operating_days_per_year
```

### 10.7 Captured CO₂

```text
captured_CO2 = total_CO2 × capture_rate
```

### 10.8 Stoikiometri Methanol

Reaksi:

```text
CO₂ + 3H₂ → CH₃OH + H₂O
```

Default teoritis:

```text
1 ton CO₂ → 0.7273 ton methanol
1 ton methanol → 1.375 ton CO₂
1 ton methanol → 0.1875 ton H₂
1 ton CO₂ → 0.1364 ton H₂
```

### 10.9 Methanol Production

```text
methanol_theoretical_ton_year = captured_CO2_ton_year × 0.7273
methanol_actual_ton_year = methanol_theoretical_ton_year × process_efficiency
```

Default:

```text
process_efficiency = 0.60
```

### 10.10 H₂ Requirement

Basis produk methanol:

```text
h2_required_ton_year = methanol_actual_ton_year × 0.1875 / h2_utilization_factor
```

Default:

```text
h2_utilization_factor = 0.90
```

Catatan:

- Bedakan `net h2 consumption` dan `gross h2 feed requirement`.
- Untuk MVP, tampilkan sebagai indikatif.

### 10.11 Electrolyzer Size

```text
h2_required_kg_day = h2_required_ton_year × 1000 / operating_days_per_year
electrolyzer_mw = h2_required_kg_day / h2_productivity_kg_day_per_mw
```

Default:

```text
h2_productivity_kg_day_per_mw = 480
```

### 10.12 Gross Revenue

```text
methanol_revenue = methanol_ton_year × methanol_price_usd_per_ton
carbon_credit_revenue = captured_CO2_ton_year × carbon_credit_price_usd_per_ton
total_gross_revenue = methanol_revenue + carbon_credit_revenue + asset_revenue
```

### 10.13 LCOM

MVP approximation:

```text
LCOM = (annualized_CAPEX + annual_OPEX + annual_H2_cost + annual_electricity_cost) / methanol_ton_year
```

### 10.14 NPV

```text
NPV = Σ (cashflow_t / (1 + discount_rate)^t) - initial_investment
```

### 10.15 IRR

Gunakan fungsi numerical IRR.

Di Python:

```python
import numpy_financial as npf
irr = npf.irr(cashflows)
```

Jika tidak ingin dependency:

- implementasi binary search IRR.

### 10.16 Payback

```text
payback_year = tahun saat cumulative cashflow >= 0
```

---

## 11. Scoring Engine

Aplikasi harus menghitung tiga skor:

1. Opportunity Score,
2. Readiness Score,
3. Composite Score.

### 11.1 Opportunity Score

Mengukur potensi ekonomi jika proyek berhasil dikembangkan.

Bobot awal:

| Komponen | Bobot |
|---|---:|
| CO₂ availability | 30% |
| Methanol potential | 20% |
| Market/logistics | 15% |
| Land availability | 10% |
| Utility advantage | 10% |
| Carbon credit potential | 5% |
| Strategic value | 10% |

Formula:

```text
opportunity_score =
  0.30 * co2_availability_score +
  0.20 * methanol_potential_score +
  0.15 * market_logistics_score +
  0.10 * land_availability_score +
  0.10 * utility_advantage_score +
  0.05 * carbon_credit_score +
  0.10 * strategic_value_score
```

### 11.2 Readiness Score

Mengukur kesiapan unit dieksekusi.

Bobot awal:

| Komponen | Bobot |
|---|---:|
| Data completeness | 20% |
| Emission data quality | 20% |
| Land readiness | 15% |
| Utility readiness | 15% |
| H₂ strategy clarity | 15% |
| Permit/logistics readiness | 15% |

Formula:

```text
readiness_score =
  0.20 * data_completeness_score +
  0.20 * emission_data_quality_score +
  0.15 * land_readiness_score +
  0.15 * utility_readiness_score +
  0.15 * h2_strategy_clarity_score +
  0.15 * permit_logistics_score
```

### 11.3 Composite Score

```text
composite_score = 0.60 * opportunity_score + 0.40 * readiness_score
```

### 11.4 Normalisasi Score

Semua score berada pada rentang 0–1.

Interpretasi:

| Score | Kategori |
|---:|---|
| 0.75–1.00 | High opportunity |
| 0.50–0.74 | Medium opportunity |
| 0.00–0.49 | Low opportunity |

---

## 12. Sensitivity Analysis

### 12.1 Variabel Wajib

| Variabel | Range Default |
|---|---:|
| H₂ price | ±20% |
| Electricity price | ±20% |
| Methanol price | ±20% |
| CAPEX | ±20% |
| Capture rate | ±10% |
| Plant availability | ±10% |
| Carbon credit price | ±50% |
| Exchange rate | ±10% |

### 12.2 Output Sensitivity

Untuk setiap variabel, hitung:

- IRR low,
- IRR high,
- NPV low,
- NPV high,
- LCOM low,
- LCOM high,
- impact score.

### 12.3 Visualisasi

Gunakan tornado chart:

- sisi kiri: decrease IRR,
- sisi kanan: increase IRR,
- center line: base case IRR.

---

## 13. Data Gap Engine

Setiap unit harus memiliki daftar data gap.

Contoh output:

```json
[
  {
    "missing_data": "Hydrogen supply strategy",
    "impact": "high",
    "priority": "urgent",
    "recommendation": "Request indicative proposal from electrolyzer or hydrogen partner."
  },
  {
    "missing_data": "Detailed CAPEX carbon capture",
    "impact": "high",
    "priority": "urgent",
    "recommendation": "Use benchmark for screening, validate during pre-FEED."
  },
  {
    "missing_data": "Land layout confirmation",
    "impact": "medium",
    "priority": "medium",
    "recommendation": "Confirm available land with site engineering team."
  }
]
```

Data gap harus muncul di:

- unit profile,
- investor dashboard,
- LLM summary.

---

## 14. UI/UX Blueprint Berdasarkan Mockup

Aplikasi harus menggunakan style:

- dark navy background,
- cyan/teal accent,
- premium enterprise look,
- clean typography,
- glassmorphism cards,
- high-tech but professional,
- tidak terlalu ramai,
- 16:9 optimized.

### 14.1 Screen 1 — Strategy Overview / Unit Map & Ranking

Tujuan:

Menampilkan peta unit, heatmap opportunity, ranking, scoring, sensitivity, dan insight.

Layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: MECH WIZ AI DIGITAL TWIN + Scenario Selector          │
├───────────────┬──────────────────────────────────────────────┤
│ Sidebar       │ KPI Cards                                     │
│               ├───────────────────────┬──────────────────────┤
│               │ Indonesia Map Heatmap │ Unit Economic Ranking │
│               ├───────────────┬───────┴──────────────────────┤
│               │ Score Radar   │ Sensitivity Chart | Insights │
└───────────────┴──────────────────────────────────────────────┘
```

Top KPI cards:

1. Best Site Selected,
2. Estimated IRR,
3. LCOM,
4. Captured CO₂,
5. E-Methanol Potential,
6. CAPEX Model.

Map panel:

- peta Indonesia,
- marker unit,
- heatmap opportunity,
- warna:
  - red/orange = high opportunity,
  - yellow = medium,
  - blue = low,
- Tenayan highlight jika ranking tertinggi.

Ranking table columns:

- Rank,
- Unit/Site,
- Composite Score,
- CO₂ Availability,
- H₂ Readiness,
- Logistics,
- IRR Potential,
- Development Readiness.

Score breakdown:

- radar chart,
- CO₂ availability,
- H₂ readiness,
- logistics,
- IRR potential,
- development readiness,
- infrastructure readiness.

Sensitivity chart:

- tornado chart,
- H₂ price,
- electricity price,
- methanol price,
- carbon price,
- CAPEX,
- capture rate.

Key insight panel:

- Tenayan ranks #1,
- H₂ cost is dominant sensitivity,
- CO₂ availability is strong,
- confidence level.

### 14.2 Screen 2 — Investor Overview / Investment Case Dashboard

Tujuan:

Menampilkan informasi investor-friendly.

Layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: Investment Case Dashboard + selected site/scenario    │
├───────────────┬──────────────────────────────────────────────┤
│ Sidebar       │ Investor KPI Cards                            │
│               ├─────────────────────────┬────────────────────┤
│               │ Investment Thesis Flow  │ Revenue Mix         │
│               ├─────────────────────────┬────────────────────┤
│               │ Scenario Comparison     │ Risk & Mitigation   │
│               ├─────────────────────────┬────────────────────┤
│               │ Roadmap to Scale        │ Why This Project Wins│
└───────────────┴──────────────────────────────────────────────┘
```

Investor KPI cards:

1. Project IRR,
2. Estimated NPV,
3. LCOM,
4. Payback Period,
5. E-Methanol Capacity,
6. CO₂ Abatement,
7. CAPEX Structure.

Investment thesis flow:

```text
Assets & Advantages → Partner Solution → Market Access → Output & Value
```

Assets:

- abundant CO₂,
- H₂ strategy,
- strategic land & port,
- reliable utilities.

Partner Solution:

- partner-financed plant,
- EPC + O&M by partner,
- merchant + offtake structure.

Market Access:

- global e-methanol market,
- premium offtake,
- carbon markets.

Output:

- e-methanol,
- low-cost,
- low-carbon,
- scalable.

Revenue mix:

- e-methanol sales,
- utilities,
- carbon credit,
- hydrogen value,
- land & port services.

Scenario comparison:

- Access,
- Align,
- Augment.

Risk matrix:

- H₂ cost volatility,
- offtake certainty,
- carbon intensity/MRV,
- execution complexity,
- partner readiness.

Roadmap:

1. Pilot & Feasibility,
2. Financial Close,
3. Construction,
4. COD Phase 1,
5. Scale-Up.

Why this project wins:

- first-mover advantage,
- concentrated natural advantages,
- partner-financed approach,
- export-market proximity,
- scalable multi-site platform,
- digital MRV & AI decision support.

---

## 15. Frontend Route Structure

```text
/
  redirect to /dashboard

/dashboard
  Strategy Overview

/units
  Unit database and map

/units/:id
  Unit profile and simulation

/scenarios
  Scenario comparison

/scenarios/:id
  Detailed scenario result

/investor
  Investor overview dashboard

/sensitivity
  Sensitivity analysis

/documents
  Upload and manage documents

/settings
  Assumptions, scoring weights, LLM settings
```

---

## 16. Backend API Endpoints

### 16.1 Plants

```text
GET    /api/plants
POST   /api/plants
GET    /api/plants/{id}
PUT    /api/plants/{id}
DELETE /api/plants/{id}
```

### 16.2 Emission Tests

```text
GET    /api/plants/{id}/emission-tests
POST   /api/plants/{id}/emission-tests
PUT    /api/emission-tests/{id}
DELETE /api/emission-tests/{id}
```

### 16.3 Site Readiness

```text
GET    /api/plants/{id}/site-readiness
POST   /api/plants/{id}/site-readiness
PUT    /api/site-readiness/{id}
```

### 16.4 Hydrogen Strategy

```text
GET    /api/plants/{id}/hydrogen-strategy
POST   /api/plants/{id}/hydrogen-strategy
PUT    /api/hydrogen-strategy/{id}
```

### 16.5 Scenarios

```text
GET    /api/scenarios
POST   /api/scenarios
GET    /api/scenarios/{id}
PUT    /api/scenarios/{id}
DELETE /api/scenarios/{id}
```

### 16.6 Simulation

```text
POST /api/simulate/{scenario_id}
GET  /api/scenario-results/{scenario_id}
```

### 16.7 Ranking

```text
GET /api/ranking
GET /api/ranking?scheme=align&case=base
```

### 16.8 Sensitivity

```text
POST /api/sensitivity/{scenario_id}
GET  /api/sensitivity/{scenario_id}
```

### 16.9 Investor Dashboard

```text
GET /api/investor-dashboard?plant_id={id}&scenario_id={id}
```

### 16.10 LLM Insight

```text
POST /api/llm/summary/{scenario_id}
POST /api/llm/data-gap/{plant_id}
POST /api/llm/investor-memo/{scenario_id}
POST /api/llm/explain-sensitivity/{scenario_id}
```

### 16.11 Documents

```text
POST /api/documents/upload
GET  /api/documents
GET  /api/documents/{id}
POST /api/documents/{id}/extract
POST /api/documents/{id}/ask
```

---

## 17. LLM Prompt Templates

### 17.1 Executive Summary Prompt

```text
You are an investment and technical analyst for MECH WIZ AI Digital Twin.

Given the following simulation result, write an executive summary in Indonesian for PLN NP management and potential investors.

Rules:
- Do not invent numbers.
- Mention data confidence.
- Clearly separate actual data, assumptions, and data gaps.
- Explain why the selected site is attractive.
- Explain the main risks and mitigation.
- Use concise professional language.

Simulation result:
{{simulation_result}}

Data gap:
{{data_gap}}

Scenario:
{{scenario}}
```

### 17.2 Data Gap Prompt

```text
You are a pre-feasibility analyst.

Analyze the following unit data and identify missing data required to improve project bankability.

For each missing data, provide:
- missing data name,
- impact level: low / medium / high,
- priority: low / medium / urgent,
- recommendation.

Unit data:
{{unit_data}}

Simulation result:
{{simulation_result}}
```

### 17.3 Sensitivity Explanation Prompt

```text
You are explaining a sensitivity analysis to a business development team.

Explain which variables most affect IRR, NPV, and LCOM.

Rules:
- Use the values from the sensitivity result only.
- Do not invent additional numbers.
- Explain in simple but professional Indonesian.
- Provide 3 to 5 key insights.

Sensitivity result:
{{sensitivity_result}}
```

### 17.4 Investor Memo Prompt

```text
You are preparing an investor-friendly memo for a low-carbon e-methanol project.

Write a structured memo with:
1. investment thesis,
2. selected site rationale,
3. key economics,
4. business scheme,
5. risk and mitigation,
6. data confidence,
7. next actions.

Use only the following data:
{{dashboard_data}}
```

---

## 18. MVP Development Phases

### Phase 0 — Project Setup

Deliverables:

- repo setup,
- Docker Compose,
- PostgreSQL,
- FastAPI backend,
- Next.js frontend,
- Tailwind/shadcn setup,
- environment variables.

### Phase 1 — Data Input & Unit Database

Deliverables:

- CRUD plants,
- CRUD emission data,
- CRUD site readiness,
- CRUD hydrogen strategy,
- CRUD financial assumptions,
- seed sample data Tenayan.

### Phase 2 — Calculation Engine

Deliverables:

- CO₂ calculator,
- captured CO₂ calculator,
- methanol potential calculator,
- H₂ requirement estimator,
- electrolyzer size estimator,
- revenue estimator,
- LCOM approximation.

### Phase 3 — Scoring & Ranking

Deliverables:

- opportunity score,
- readiness score,
- composite score,
- ranking table,
- heatmap-ready API.

### Phase 4 — Dashboard UI

Deliverables:

- strategy overview dashboard,
- map heatmap,
- ranking table,
- KPI cards,
- score radar,
- sensitivity chart,
- key insights panel.

### Phase 5 — Investor Dashboard

Deliverables:

- investor KPI cards,
- investment thesis flow,
- revenue mix,
- scenario comparison,
- risk matrix,
- roadmap,
- why this project wins.

### Phase 6 — Sensitivity Analysis

Deliverables:

- sensitivity variables,
- tornado chart,
- IRR/NPV/LCOM impact,
- summary.

### Phase 7 — LLM Insight Layer

Deliverables:

- OpenRouter integration,
- executive summary,
- data gap summary,
- investor memo,
- sensitivity explanation.

### Phase 8 — Document Upload

Deliverables:

- upload PDF/Excel,
- text extraction,
- document repository,
- basic document Q&A.

---

## 19. Recommended Folder Structure

```text
mechwiz-ai-digital-twin/
├── docker-compose.yml
├── README.md
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   │   ├── co2_calculator.py
│   │   │   ├── methanol_calculator.py
│   │   │   ├── financial_model.py
│   │   │   ├── scoring_engine.py
│   │   │   ├── sensitivity_engine.py
│   │   │   ├── llm_service.py
│   │   │   └── document_service.py
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── units/
│   │   ├── investor/
│   │   ├── scenarios/
│   │   ├── sensitivity/
│   │   └── settings/
│   ├── components/
│   │   ├── layout/
│   │   ├── cards/
│   │   ├── charts/
│   │   ├── maps/
│   │   └── dashboards/
│   ├── lib/
│   ├── types/
│   ├── package.json
│   └── Dockerfile
└── docs/
    ├── blueprint.md
    ├── formulas.md
    ├── api.md
    └── data_dictionary.md
```

---

## 20. Environment Variables

```env
DATABASE_URL=postgresql://mechwiz:password@db:5432/mechwiz
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
APP_ENV=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
JWT_SECRET=change_this_secret
UPLOAD_DIR=/app/uploads
```

---

## 21. UI Design Tokens

### Colors

```text
background_primary: #020817
background_secondary: #071426
panel: #0B1B33
panel_border: #163B5C
cyan: #00E5FF
teal: #00C2A8
blue: #0EA5E9
green: #7CFF6B
yellow: #FFD84D
orange: #FF9F1C
red: #FF4D6D
text_primary: #F8FAFC
text_secondary: #94A3B8
```

### Typography

- Font: Inter, Satoshi, or Geist.
- Header: bold, uppercase where appropriate.
- KPI number: large, bright, high contrast.
- Body text: compact but readable.

### Card Style

- rounded-2xl,
- border with low opacity cyan/blue,
- dark gradient background,
- subtle glow on active state,
- hover effect light border.

---

## 22. Sample Seed Data — Tenayan

Gunakan sample data berikut untuk seed awal.

```json
{
  "plant": {
    "plant_name": "PLTU Tenayan",
    "unit_name": "Unit 1-2",
    "province": "Riau",
    "city": "Pekanbaru",
    "capacity_mw": 220,
    "fuel_type": "coal",
    "status": "active",
    "capacity_factor": 0.90,
    "operating_days_per_year": 330,
    "owner": "PLN NP",
    "data_status": "actual",
    "confidence_level": "medium"
  },
  "emission_tests": [
    {
      "stack_id": "Chimney #1",
      "stack_diameter_m": 3.0,
      "gas_velocity_m_s": 14.4,
      "flue_gas_temperature_c": 124,
      "co2_percent_dry": 8.48,
      "o2_percent": 9.54,
      "moisture_percent": 5.84,
      "so2_mg_nm3": 233,
      "nox_mg_nm3": 263,
      "particulate_mg_nm3": 55.4
    },
    {
      "stack_id": "Chimney #2",
      "stack_diameter_m": 3.0,
      "gas_velocity_m_s": 13.5,
      "flue_gas_temperature_c": 109,
      "co2_percent_dry": 3.54,
      "o2_percent": 15.0,
      "moisture_percent": 6.48,
      "so2_mg_nm3": 268,
      "nox_mg_nm3": 202,
      "particulate_mg_nm3": 52.3
    }
  ]
}
```

---

## 23. Acceptance Criteria

### 23.1 MVP dianggap selesai jika:

1. User bisa menambahkan unit pembangkit.
2. User bisa menambahkan data emisi/cerobong.
3. Aplikasi bisa menghitung CO₂ ton/hari dan ton/tahun.
4. Aplikasi bisa menghitung captured CO₂ berdasarkan capture rate.
5. Aplikasi bisa menghitung e-methanol potential.
6. Aplikasi bisa menghitung H₂ requirement indikatif.
7. Aplikasi bisa menghitung ranking unit.
8. Aplikasi bisa menampilkan peta unit.
9. Aplikasi bisa menampilkan heatmap/scoring.
10. Aplikasi bisa menampilkan dashboard investor.
11. Aplikasi bisa menjalankan sensitivity analysis.
12. Aplikasi bisa menghasilkan LLM executive summary.
13. Aplikasi menampilkan confidence level dan data gap.
14. UI mengikuti style modern, high-tech, clean, premium, professional.

---

## 24. Important Notes for Codex / Developer

1. Jangan hardcode semua angka di frontend.
2. Semua angka harus berasal dari backend API.
3. Semua rumus deterministic harus berada di backend.
4. LLM tidak boleh membuat angka baru.
5. Jika LLM menghasilkan insight, simpan prompt dan response ke database.
6. Semua scenario result harus dapat direproduce.
7. Semua input harus memiliki data status.
8. Semua output utama harus memiliki confidence level.
9. Default assumptions harus bisa diubah di settings.
10. Desain frontend harus menyerupai mockup:
    - dark premium UI,
    - cyan/teal accent,
    - KPI cards,
    - map heatmap,
    - ranking table,
    - radar chart,
    - tornado sensitivity,
    - investor dashboard.

---

## 25. Future Roadmap

### v1.0 — Site Screening & Investment Simulator

- manual input,
- basic simulation,
- scoring,
- investor dashboard,
- LLM summary.

### v1.5 — Document Intelligence

- PDF/Excel upload,
- automatic extraction,
- admin validation,
- document Q&A.

### v2.0 — Pre-FEED Digital Twin

- detailed CAPEX/OPEX,
- partner proposal comparison,
- offtake readiness,
- MRV module,
- detailed risk register.

### v3.0 — Operational Digital Twin

- real-time data integration,
- DCS/SCADA/historian,
- process optimization,
- predictive maintenance,
- live MRV,
- production optimization.

---

## 26. Kesimpulan

Blueprint ini membangun MECH WIZ AI Digital Twin sebagai aplikasi **assumption-driven pre-feasibility simulator** yang cocok untuk kondisi proyek saat ini: masih berupa draft ide bisnis, belum ada reactor methanol, belum ada hydrogen plant di semua unit, belum ada FEED, dan belum ada CAPEX detail.

Aplikasi tetap dapat memberi nilai tinggi karena mampu:

1. memetakan unit pembangkit,
2. menghitung potensi CO₂,
3. menghitung potensi e-methanol,
4. memperkirakan kebutuhan H₂,
5. menilai readiness unit,
6. membuat heatmap economic opportunity,
7. membandingkan skenario bisnis,
8. melakukan sensitivity analysis,
9. menyusun informasi investor-friendly,
10. menampilkan confidence level dan data gap.

Target akhir MVP:

> **Membantu PLN NP memilih unit terbaik untuk pilot MECH WIZ dan menjelaskan kelayakan awal proyek secara visual, terukur, dan investor-friendly.**
