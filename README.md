# MECH WIZ AI Digital Twin

MECH WIZ AI Digital Twin adalah cockpit pre-feasibility untuk membantu PLN NP/PLN group menyaring kandidat pilot carbon-to-fuel, terutama konversi CO2 dari PLTU menjadi e-methanol. Aplikasi ini bukan hanya dashboard tampilan data. Backend menghitung simulasi teknis, ekonomi awal, scoring kandidat, sensitivity, kesiapan pelabuhan, data gap, investor case, dan kesiapan Pre-FEED secara deterministik.

Tujuan utama aplikasi:

- Mengumpulkan data unit pembangkit, emisi, kesiapan lahan, H2, skenario bisnis, biaya, offtake, MRV, risiko, dan dokumen.
- Menghitung potensi CO2, captured CO2, e-methanol, kebutuhan H2, ukuran electrolyzer, revenue, LCOM, NPV, IRR, payback, ranking, sensitivity, dan readiness.
- Menjelaskan mana data aktual, estimasi, benchmark, asumsi user, partner-supplied, atau unknown.
- Membantu memilih unit pilot yang paling masuk akal sebelum masuk studi teknis dan komersial yang lebih mahal.

Catatan implementasi tambahan dalam bahasa Indonesia tersedia di [`docs/GSD_v2_PREFEED_DETAILED_EXPLANATION.md`](docs/GSD_v2_PREFEED_DETAILED_EXPLANATION.md).

## Ringkasan Modul

| Modul | Halaman | Fungsi Utama | Output Utama |
|-------|---------|--------------|--------------|
| Unit Data | `/units` | Input data PLTU, emisi stack, kesiapan site, dan strategi H2 | Profil unit dan status kelengkapan data |
| Scenario Simulation | `/scenarios` | Hitung CO2, methanol, H2, electrolyzer, revenue, LCOM, NPV, IRR, payback | `ScenarioResult` |
| Map & Scoring | `/dashboard/map` | Ranking unit, heatmap, economic zone, pelabuhan, koridor ekspor indikatif | Skor prioritas dan layer map |
| Sensitivity | `/sensitivity` | Uji pengaruh perubahan variabel ekonomi/teknis | Tornado chart dan driver dominan |
| Investor Case | `/investor` | Ringkas kasus investasi dari data yang sudah dihitung backend | KPI, thesis, risiko, roadmap, data gap |
| Pre-FEED | `/prefeed` | Kelola paket Pre-FEED, biaya, vendor, offtake, MRV, risiko, gate keputusan | Dashboard kesiapan komite |
| Documents | `/documents` | Upload, ekstrak, dan tanya jawab dokumen | Teks ekstraksi dan insight dokumen |
| Settings | `/settings` | Atur asumsi default, bobot scoring, OpenRouter, dan data quality | Konfigurasi dan data gap |

## Cara Membaca Aplikasi

Alur logisnya adalah:

1. `Units`: definisikan unit pembangkit dan data teknis dasar.
2. `Scenarios`: buat skenario bisnis dan financial assumptions.
3. `Run Simulation`: backend menghitung hasil teknis dan ekonomi awal.
4. `Map`: backend memberi ranking, heatmap, port-aware map, dan data gap.
5. `Sensitivity`: backend menghitung variabel mana yang paling mempengaruhi ekonomi.
6. `Investor`: aplikasi merangkum hasil menjadi kasus investasi.
7. `Pre-FEED`: masukkan data biaya/vendor/offtake/MRV/risiko untuk menuju keputusan komite.
8. `Documents`: upload dokumen pendukung dan gunakan LLM hanya untuk narasi berbasis data tersimpan.
9. `Settings`: sesuaikan asumsi, scoring weights, dan API key OpenRouter.

Semua angka yang dihitung backend harus dibaca sebagai screening/pre-feasibility, bukan angka final EPC, bankable feasibility study, atau investment decision tanpa validasi lapangan.

## Status Validitas Data

Setiap data penting punya `data_status` dan `confidence_level`.

`data_status`:

- `actual`: data aktual atau terkonfirmasi.
- `estimated`: estimasi dari sumber publik atau kalkulasi.
- `benchmark`: benchmark umum untuk screening.
- `user_assumption`: asumsi yang dimasukkan pengguna.
- `partner_supplied`: data dari vendor/partner.
- `unknown`: belum diketahui.

`confidence_level`:

- `high`: cukup kuat untuk dipakai sebagai dasar diskusi.
- `medium`: cukup untuk screening, masih perlu verifikasi.
- `low`: hanya indikatif.
- `unknown`: belum ada dasar yang jelas.

Data publik yang saat ini dipakai:

- Curated 26-site PLTU target dataset: [`docs/PLTU_CURATED_DATASET_SOURCES.md`](docs/PLTU_CURATED_DATASET_SOURCES.md)
- Global Energy Monitor Global Coal Plant Tracker untuk data publik PLTU: `https://globalenergymonitor.org/projects/global-coal-plant-tracker/`
- Permen LHK P.15/2019 untuk benchmark baku mutu emisi PLTU termal: `https://ppkl.menlhk.go.id/website/filebox/767/190930180734PERMENLHK%20NOMOR%2015%20TAHUN%202019.pdf`
- NGA World Port Index untuk data pelabuhan: `https://msi.nga.mil/Publications/WPI`
- Maritime and Port Authority of Singapore untuk konteks methanol bunkering: `https://www.mpa.gov.sg/media-centre/details/singapore-gears-up-to-meet-net-zero-needs-of-shipping`

Catatan penting: data publik valid untuk screening awal, tetapi belum menggantikan konfirmasi PLN, site visit, data DCS/stack test aktual, vendor quote, terminal operator confirmation, atau offtake contract.

## Modul 1: Unit Data

Halaman: `/units`

Modul ini adalah fondasi semua kalkulasi. Tanpa unit, scenario, scoring, map, sensitivity, dan investor case tidak punya objek yang dihitung.

### Input Utama

Data unit:

- `plant_name`: nama PLTU/site.
- `unit_name`: nama unit.
- `province`, `city`: lokasi administratif.
- `latitude`, `longitude`: koordinat untuk map, nearest port, dan economic zone.
- `capacity_mw`: kapasitas unit.
- `fuel_type`: jenis bahan bakar, misalnya coal/gas.
- `status`: status unit.
- `owner`: pemilik/operator.
- `operating_days_per_year`: hari operasi per tahun.
- `data_status`, `confidence_level`: kualitas data.

Emission tests:

- `stack_diameter_m`
- `gas_velocity_m_s`
- `flue_gas_temperature_c`
- `co2_percent_dry`
- `moisture_percent`
- status dan confidence data emisi.

Site readiness:

- luas lahan tersedia.
- status lahan.
- jarak ke pelabuhan.
- apakah ada port/jetty.
- akses jalan.
- kesiapan utility, power, water.
- permit risk.

Hydrogen strategy:

- apakah H2 eksisting tersedia.
- strategi supply H2.
- estimasi biaya H2.
- readiness score H2.

### Apa Yang Dihitung

Modul ini tidak melakukan simulasi ekonomi penuh. Ia menyimpan input yang akan dipakai modul lain.

Emission data dipakai di modul simulation untuk menghitung CO2. Site readiness dan hydrogen strategy dipakai di scoring untuk menilai kesiapan lokasi.

### Arti Output

Output modul ini adalah profil unit. Kalau data kosong, output modul lain akan tetap bisa muncul, tetapi banyak hasil menjadi `null`, confidence turun, dan data gap bertambah.

## Modul 2: Scenario Simulation

Halaman: `/scenarios`

Modul ini menghitung potensi teknis dan ekonomi awal dari satu unit dalam satu skenario bisnis.

### Input Utama

Scenario:

- `scenario_name`: nama skenario.
- `scheme`: `access`, `align`, atau `augment`.
- `capture_rate`: porsi CO2 yang ditangkap. Default fallback backend: `0.85`.
- `process_efficiency`: efisiensi proses methanol. Default fallback: `0.60`.
- `pln_ownership_percent`
- `partner_capex_responsibility_percent`
- `pln_capex_responsibility_percent`
- `revenue_model`
- `data_status`, `confidence_level`

Financial assumptions:

- `methanol_price_usd_per_ton`
- `grey_methanol_price_usd_per_ton`
- `hydrogen_price_usd_per_kg`
- `electricity_price_usd_per_kwh`
- `carbon_credit_price_idr_per_ton`
- `exchange_rate_idr_usd`
- `discount_rate`
- `tax_rate`
- `capex_capture_usd`
- `capex_electrolyzer_usd`
- `capex_methanol_plant_usd`
- `capex_storage_port_usd`
- `opex_percent_capex`

### Kalkulasi CO2

Backend menghitung CO2 dari emission test:

```text
stack_area_m2 = pi * (stack_diameter_m / 2)^2
normalized_gas_flow_nm3_s = gas_velocity_m_s * stack_area_m2 * 273.15 / (273.15 + flue_gas_temperature_c)
co2_wet_fraction = (co2_percent_dry / 100) * (1 - moisture_percent / 100)
co2_kg_s = normalized_gas_flow_nm3_s * co2_wet_fraction * 1.964
co2_ton_day = co2_kg_s * 86400 / 1000
total_co2_ton_year = co2_ton_day * operating_days_per_year
```

Output `total_co2_ton_per_year` menjelaskan estimasi total CO2 per tahun dari data stack yang tersedia.

### Kalkulasi Captured CO2 Dan Methanol

```text
captured_co2_ton_per_year = total_co2_ton_per_year * capture_rate
vented_co2_ton_per_year = total_co2_ton_per_year - captured_co2_ton_per_year
methanol_theoretical_ton_per_year = captured_co2_ton_per_year * 0.7273
methanol_ton_per_year = methanol_theoretical_ton_per_year * process_efficiency
```

Arti output:

- `captured_co2_ton_per_year`: CO2 yang masuk proses carbon-to-fuel.
- `vented_co2_ton_per_year`: CO2 yang belum ditangkap.
- `methanol_ton_per_year`: potensi produksi e-methanol setelah efisiensi proses.

### Kalkulasi H2 Dan Electrolyzer

```text
h2_required_ton_per_year = methanol_ton_per_year * 0.1875 / 0.90
electrolyzer_required_mw = (h2_required_ton_per_year * 1000 / operating_days_per_year) / 480
```

Arti output:

- `h2_required_ton_per_year`: kebutuhan H2 tahunan.
- `electrolyzer_required_mw`: ukuran electrolyzer indikatif untuk memenuhi kebutuhan H2.

### Kalkulasi Revenue Dan Ekonomi

```text
carbon_credit_price_usd_per_ton = carbon_credit_price_idr_per_ton / exchange_rate_idr_usd
gross_revenue = methanol_ton_per_year * methanol_price_usd_per_ton
              + captured_co2_ton_per_year * carbon_credit_price_usd_per_ton
total_capex = capex_capture + capex_electrolyzer + capex_methanol_plant + capex_storage_port
annualized_capex = total_capex * capital_recovery_factor
annual_opex = total_capex * opex_percent_capex
annual_h2_cost = h2_required_ton_per_year * 1000 * hydrogen_price_usd_per_kg
annual_electricity_cost = electrolyzer_mw * 1000 * 24 * operating_days_per_year * electricity_price_usd_per_kwh
LCOM = (annualized_capex + annual_opex + annual_h2_cost + annual_electricity_cost) / methanol_ton_per_year
annual_cashflow = (gross_revenue - annual_opex - annual_h2_cost - annual_electricity_cost) after tax if positive
NPV = discounted annual cashflow over 20 years - initial capex
IRR = discount rate where project cashflow NPV becomes zero
payback_years = total_capex / annual_cashflow
```

Arti output:

- `gross_revenue_usd_per_year`: pendapatan indikatif dari methanol dan carbon credit.
- `lcom_usd_per_ton`: levelized cost of methanol. Makin rendah makin baik.
- `npv_usd`: nilai bersih proyek indikatif. Positif berarti cashflow diskonto melebihi capex.
- `irr`: return proyek indikatif.
- `payback_years`: estimasi waktu balik modal.
- `missing_inputs`: daftar field yang membuat hasil tidak lengkap.
- `confidence_level`: confidence output, turun ke low jika input kunci hilang atau asumsi masih benchmark.

## Modul 3: Map, Heatmap, Scoring, Port Intelligence

Halaman: `/dashboard/map`

Modul ini menjawab: unit mana yang paling layak diprioritaskan, dimana konsentrasi potensi terbesar, dan bagaimana konteks pelabuhannya.

### Input Utama

- hasil simulation terbaru dari setiap scenario.
- data unit dan koordinat.
- emission tests.
- site readiness.
- hydrogen strategy.
- financial assumptions.
- scoring weights dari Settings.
- data pelabuhan dari NGA World Port Index.

### Score Yang Dihitung

Backend menghitung tiga score utama:

```text
opportunity_score =
  0.30 * co2_score
  + 0.20 * methanol_score
  + 0.15 * market_access_score
  + 0.10 * land_score
  + 0.10 * utility_score
  + 0.05 * carbon_credit_score
  + 0.10 * strategic_value_score

readiness_score =
  0.20 * data_completeness_score
  + 0.20 * emission_quality_score
  + 0.15 * land_score
  + 0.15 * utility_score
  + 0.15 * h2_strategy_score
  + 0.15 * permit_logistic_score

confidence_score = average confidence dari plant, scenario, financial, site readiness, H2 strategy, dan emission tests

composite_score =
  0.45 * opportunity_score
  + 0.35 * readiness_score
  + 0.20 * confidence_score
```

Bobot composite bisa diubah di `/settings`.

Arti score:

- `opportunity_score`: seberapa besar potensi bisnis dan teknisnya.
- `readiness_score`: seberapa siap lokasi dan datanya untuk maju ke studi berikutnya.
- `confidence_score`: seberapa kuat kualitas data.
- `composite_score`: angka ranking total untuk memilih kandidat pilot.
- `key_bottleneck`: hambatan utama seperti H2, CAPEX, financial assumptions, koordinat, land, atau utility.
- `data_gap_count`: jumlah gap yang perlu ditutup.

### Heatmap Weight

Heatmap tidak hanya memakai composite score. Default:

```text
heatmap_weight =
  0.45 * opportunity_score
  + 0.25 * readiness_score
  + 0.20 * economic_return_score
  + 0.10 * confidence_score
```

Arti output: area yang lebih panas menunjukkan kombinasi potensi, readiness, return, dan confidence yang lebih baik.

### Port Intelligence

Backend mengambil pelabuhan Indonesia dan Singapura dari NGA World Port Index, lalu menghitung:

```text
nearest_port_distance_km = haversine_distance(unit_coordinate, port_coordinate)
port_readiness_score =
  0.30 * harbor_size_score
  + 0.30 * depth_score
  + 0.25 * cargo_handling_score
  + 0.15 * operations_score
```

Port readiness memakai atribut WPI seperti harbor size, depth, wharf, container, liquid bulk, oil terminal, first port of entry, tugs, radio, turning area, dan ETA message.

Economic value per unit:

```text
economic_value_score =
  0.38 * composite_score
  + 0.24 * methanol_score_relative
  + 0.22 * nearest_port_readiness_score
  + 0.16 * port_proximity_score
```

Economic zones digabung berdasarkan pelabuhan terdekat:

```text
economic_zone_score =
  0.34 * methanol_volume_score
  + 0.18 * co2_volume_score
  + 0.16 * average_composite_score
  + 0.16 * port_readiness_score
  + 0.10 * port_proximity_score
  + 0.06 * unit_count_score
```

Arti layer map:

- `Unit markers`: titik unit PLTU.
- `Heatmap`: densitas dan kekuatan peluang unit.
- `Economic Area`: area konsentrasi potensi ekonomi berbasis unit terdekat ke pelabuhan.
- `Ports`: pelabuhan WPI dan readiness tier.
- `SG Route`: koridor ekspor indikatif menuju Jurong Island Singapura.

Catatan: `SG Route` adalah garis proxy screening, bukan rute navigasi, bukan AIS route, dan bukan rekomendasi pelayaran.

## Modul 4: Sensitivity Analysis

Halaman: `/sensitivity`

Modul ini menjawab: variabel mana yang paling membuat ekonomi proyek berubah.

### Input Utama

- unit dan scenario yang dipilih.
- simulation result terbaru.
- financial assumptions.
- variabel sensitivity:
  - `h2_price`
  - `electricity_price`
  - `methanol_price`
  - `capex`
  - `capture_rate`
  - `plant_availability`
  - `carbon_credit_price`
  - `exchange_rate`

Default backend menguji low/high multiplier:

```text
low = base * 0.80
high = base * 1.20
```

Untuk `capture_rate`, nilai tetap dibatasi antara 0 dan 1.

### Apa Yang Dihitung

Untuk setiap variabel, backend menghitung ulang:

- low/base/high input value.
- low/base/high IRR.
- low/base/high NPV.
- low/base/high LCOM.
- payback jika bisa dihitung.
- missing inputs dan warnings.

Impact score:

```text
Jika IRR tersedia:
  impact_score = max(abs(low_irr - base_irr), abs(high_irr - base_irr))
Jika IRR tidak tersedia tetapi NPV tersedia:
  impact_score = perubahan relatif NPV terbesar
Jika NPV tidak tersedia tetapi LCOM tersedia:
  impact_score = perubahan relatif LCOM terbesar
```

Arti output:

- `Dominant Driver`: variabel dengan impact score tertinggi.
- `Tornado Chart`: urutan variabel dari paling sensitif ke paling kecil dampaknya.
- `Low/Base/High Table`: bagaimana ekonomi berubah jika input turun/naik 20%.
- `Warnings`: alasan kenapa sebagian output null atau confidence rendah.

## Modul 5: Investor Case

Halaman: `/investor`

Modul ini bukan mesin kalkulasi baru. Ia merangkum data yang sudah dihitung dari simulation, scoring, sensitivity, financial assumptions, site readiness, H2 strategy, dan data gaps.

### Input Utama

- selected plant.
- selected scenario.
- latest scenario result.
- latest scoring result.
- latest sensitivity run.
- financial assumptions.
- site readiness.
- hydrogen strategy.
- emission tests.

### Output Dan Artinya

- `KPIs`: IRR, NPV, LCOM, payback, methanol capacity, CO2 abatement, total CO2, composite score, opportunity score, readiness score, confidence score, rank.
- `CAPEX Structure`: ringkasan biaya capture, electrolyzer, methanol plant, storage/port, plus porsi tanggung jawab PLN/partner.
- `Revenue Mix`: pemisahan revenue e-methanol, carbon credit, dan service revenue jika tersedia.
- `Scenario Comparison`: perbandingan WIZ Access, WIZ Align, WIZ Augment untuk unit yang sama.
- `Thesis Flow`: narasi deterministik mengapa unit/skenario ini menarik.
- `Risks`: data gaps dan dominant sensitivity driver yang perlu dimitigasi.
- `Roadmap`: urutan pilot, financial close, construction, COD, scale-up.
- `Why This Wins`: daftar alasan strategis yang berasal dari data dan ranking.
- `Data Quality`: status input dan output confidence.

Investor case harus dibaca sebagai paket komunikasi awal. Angka masih mengikuti kualitas input.

## Modul 6: Pre-FEED Package

Halaman: `/prefeed`

Modul Pre-FEED mengubah screening menjadi checklist kesiapan keputusan. Di sini user memasukkan dokumen vendor, biaya, offtake, MRV, risiko, dan decision gate.

### 6.1 Package Foundation

Input:

- plant dan scenario.
- nama package.
- owner.
- source organization.
- received date.
- version label.
- package status.
- linked documents.
- document role.

Backend menghasilkan gaps jika:

- owner kosong.
- source organization kosong.
- version label kosong.
- received date kosong.
- tidak ada dokumen `vendor_proposal`.
- tidak ada dokumen `epc_estimate`.
- confidence package masih low/unknown.

Arti output: apakah paket Pre-FEED punya metadata dan dokumen dasar yang cukup untuk direview.

### 6.2 Cost And Vendor Proposal

Input cost item:

- cost type: CAPEX atau OPEX.
- cost component/category.
- amount.
- currency.
- recurrence untuk OPEX.
- contingency percent.
- escalation percent.
- source label.
- confidence.

Kalkulasi cost:

```text
adjusted_capex = amount * (1 + contingency_percent/100) * (1 + escalation_percent/100)
annualized_opex = amount * recurrence_multiplier
```

Recurrence multiplier:

- annual = 1
- monthly = 12
- quarterly = 4
- weekly = 52
- daily = 365
- one_time = 0

Output:

- `capex_total_by_currency`
- `annual_opex_total_by_currency`
- `scenario_ready_assumptions`
- warnings jika tidak ada item atau ada banyak currency.

Catatan: sistem tidak melakukan konversi multi-currency di Phase 7. Jika ada IDR dan USD, hasil dipisahkan per currency.

Vendor proposal:

- vendor name.
- proposal name.
- supporting document.
- scope capture package.
- scope electrolyzer.
- scope methanol plant.
- scope storage port.
- scope grid power.
- scope land.
- scope MRV.
- commercial basis.
- delivery assumptions.
- exclusions.
- validity date.

Vendor comparison menghitung:

```text
scope_completeness_score = covered_scope_count / 7
```

Proposal diurutkan dengan prioritas gap count lebih rendah, scope completeness lebih tinggi, CAPEX USD lebih rendah, lalu nama vendor.

Active cost basis:

- user bisa memilih package blended basis atau vendor proposal.
- pilihan disimpan sebagai snapshot.
- tidak mengubah history financial assumptions atau scenario results yang sudah dihitung.

### 6.3 Offtake And MRV

Price deck input:

- methanol price.
- carbon credit price.
- electricity price.
- hydrogen price.
- exchange rate.
- escalation.
- active deck flag.

Offtake prospect input:

- counterparty.
- product: e-methanol, carbon credit, CO2 supply, hydrogen, atau other.
- target volume.
- term years.
- pricing basis.
- price.
- status: lead, discussion, LOI, term sheet, contracted, signed, inactive.
- supporting document.

Offtake readiness:

```text
readiness =
  0.25 * counterparty_status
  + 0.25 * volume_coverage
  + 0.20 * term_certainty
  + 0.20 * pricing_clarity
  + 0.10 * document_confidence
```

Output:

- committed methanol volume.
- methanol volume coverage terhadap scenario methanol output.
- methanol revenue.
- carbon credit revenue.
- gross revenue.
- readiness score dan komponennya.
- scenario-ready assumption patch.
- offtake gaps.

MRV input:

- baseline emissions.
- captured CO2 accounting.
- product carbon intensity.
- electricity source.
- electricity emission factor.
- methanol pathway.
- carbon credit methodology.
- verification status.
- verifier name.
- carbon credit eligibility.
- eligibility basis.
- supporting document.

MRV readiness:

```text
readiness =
  0.15 * baseline_data
  + 0.15 * captured_accounting
  + 0.15 * methodology
  + 0.20 * verification
  + 0.15 * electricity_source
  + 0.10 * credit_eligibility
  + 0.10 * confidence
```

Output:

- carbon intensity tCO2e per ton methanol.
- abatement tCO2e per year.
- baseline emissions.
- captured CO2 accounting.
- carbon credit eligibility.
- readiness components.
- MRV gaps.

Jika product carbon intensity kosong, backend bisa menurunkan nilai indikatif dari CO2 balance scenario:

```text
carbon_intensity = max(baseline - captured, 0) / methanol_ton_per_year
```

### 6.4 Risk And Decision Gate

Risk register input:

- category.
- risk statement.
- likelihood 1 sampai 5.
- impact 1 sampai 5.
- mitigation.
- owner.
- due date.
- status.

Kalkulasi:

```text
severity_score = likelihood * impact
```

Severity band dipakai untuk risk summary dan blocker. Risk escalated atau severity tinggi menjadi blocker prioritas.

Decision gate input:

- category.
- gate title.
- evidence reference.
- owner.
- due date.
- critical flag.
- status: not_started, in_progress, ready, blocked, atau waived.

Gate readiness:

```text
readiness_score = ready_or_waived_gate_count / total_gate_count
```

Decision dashboard output:

- package gaps.
- cost summary.
- active cost basis.
- vendor comparison.
- offtake summary.
- MRV summary.
- risk summary.
- decision gate summary.
- blockers.
- next actions.
- warnings.

Arti output: apakah package layak dibawa ke komite, dan apa pekerjaan paling penting berikutnya.

## Modul 7: Documents And LLM

Halaman: `/documents` dan panel insight di `/investor`

### Documents

File yang didukung untuk extraction:

- PDF.
- XLSX.
- CSV.
- TXT.
- MD.
- JSON.

Backend menyimpan file upload ke `UPLOAD_DIR`, membuat nama aman, lalu mengekstrak teks.

Output:

- document metadata.
- extraction status: pending, extracted, failed.
- extracted text.
- extraction error jika gagal.

### LLM Dengan OpenRouter

LLM dipakai untuk narasi, bukan sumber angka.

Input LLM:

- stored plant data.
- stored scenario result.
- stored scoring.
- stored sensitivity.
- stored data gaps.
- extracted document text untuk document Q&A.

Output LLM:

- executive summary.
- investor memo.
- data gap explanation.
- sensitivity explanation.
- document answer.

Aturan penting di prompt backend:

- LLM tidak boleh membuat angka baru.
- LLM tidak boleh menghitung ulang IRR, NPV, LCOM, payback, scoring, sensitivity, CO2, H2, atau methanol.
- LLM hanya menjelaskan data yang sudah dihitung backend.

OpenRouter API key bisa dimasukkan di `/settings`. API key tidak ditampilkan mentah kembali ke frontend; backend hanya menampilkan status dan masked key.

## Modul 8: Settings And Data Quality

Halaman: `/settings`

Settings berisi:

- default financial assumptions.
- scoring weights.
- OpenRouter provider settings.
- data quality summary.

Default financial assumptions dipakai sebagai referensi/asumsi awal. Scoring weights mengubah cara ranking dan heatmap dihitung.

Data quality summary menampilkan:

- input status: plant, emission tests, site readiness, hydrogen strategy, scenario, financial assumptions.
- output confidence: scenario result, scoring, sensitivity.
- data gap recommendations.

Data gap dibuat dari logika backend, misalnya:

- koordinat kosong.
- available land belum dikonfirmasi.
- hydrogen strategy belum jelas.
- financial assumptions kosong.
- methanol price kosong.
- CAPEX belum tervalidasi.
- missing input dari simulation.

## Import Curated 26 PLTU Target Dataset

Script:

```bash
cd backend
.venv/bin/python -m app.import_target_pltu
```

Script ini adalah importer utama untuk dataset kerja saat ini. Ia menghapus plant-linked dataset lama, lalu mengisi tepat 26 site PLTU target yang dipilih user: plant, benchmark emission, site readiness, H2 strategy, WIZ Align scenario, financial assumptions, simulation result, dan scoring/map ranking.

Sumber kapasitas dan koordinat dicatat per site. Jika sumber publik kuat, `confidence_level` dibuat `high`; jika ada perbedaan kapasitas/status publik atau hanya ada alamat, dibuat `medium`/`low`. Untuk PLTU Ampana, sumber publik mengonfirmasi Desa Sabo/Ampana Tete tetapi belum ada koordinat fence-line publik, sehingga tetap ditandai `low`.

Emission pollutant fields (`SO2`, `NOx`, `PM`, `Hg`) memakai benchmark baku mutu existing coal PLTU dari Permen LHK P.15/2019, bukan data stack test aktual. CO2 stack geometry juga benchmark deterministik dari kapasitas, capacity factor, dan faktor emisi batubara untuk kebutuhan screening.

Dokumentasi detail:

- [`docs/PLTU_CURATED_DATASET_SOURCES.md`](docs/PLTU_CURATED_DATASET_SOURCES.md)
- [`docs/PLN_PLTU_PUBLIC_SCREENING_IMPORT.md`](docs/PLN_PLTU_PUBLIC_SCREENING_IMPORT.md)
- [`docs/MAP_PORT_INTELLIGENCE_VALIDITY.md`](docs/MAP_PORT_INTELLIGENCE_VALIDITY.md)

Data import ini adalah screening dataset. Nama unit, kapasitas, status, owner, dan koordinat berasal dari sumber publik atau daftar target user. Emisi benchmark, CAPEX, site readiness, H2 strategy, dan asumsi ekonomi tetap harus divalidasi sebelum keputusan investasi.

Importer lama `python -m app.import_pln_pltu` masih tersedia sebagai broad public GEM screening import, tetapi bukan dataset default untuk project ini.

## Arti WIZ Access, WIZ Align, WIZ Augment

Sistem menyimpan skenario dengan `scheme`:

- `WIZ Access`: biasanya dipakai untuk skema akses aset/site dengan keterlibatan partner lebih besar.
- `WIZ Align`: skema kolaborasi yang menyeimbangkan peran PLN dan partner.
- `WIZ Augment`: skema ekspansi/peningkatan kapabilitas yang bisa menyertakan integrasi lebih dalam.

Di codebase saat ini, `scheme` terutama mempengaruhi label rekomendasi, grouping scenario, dan konteks investor. Perbedaan ekonomi tetap berasal dari input financial assumptions, ownership/capex responsibility, capture rate, process efficiency, dan data pendukung masing-masing scenario.

## Local Development

Copy environment sample jika ingin override lokal:

```bash
cp .env.example .env
```

Start full stack:

```bash
docker compose up --build
```

Di terminal kedua, apply migration:

```bash
docker compose exec backend alembic upgrade head
```

Seed initial Tenayan unit, WIZ Align base scenario, coordinates, dan benchmark financial assumptions:

```bash
docker compose exec backend python -m app.seed
```

Buka:

- Dashboard: `http://localhost:3000/dashboard`
- Map: `http://localhost:3000/dashboard/map`
- Units: `http://localhost:3000/units`
- Scenarios: `http://localhost:3000/scenarios`
- Sensitivity: `http://localhost:3000/sensitivity`
- Investor: `http://localhost:3000/investor`
- Pre-FEED: `http://localhost:3000/prefeed`
- Documents: `http://localhost:3000/documents`
- Settings: `http://localhost:3000/settings`
- API health: `http://localhost:8000/api/health`

## Remote Preview / Production-Like Run

Untuk server/IP preview, jalankan frontend dengan production build. `next dev` menampilkan indikator `N` dan compile module saat pertama dibuka, sehingga terasa lebih berat.

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

cd ../frontend
npm run build
npm run start -- --hostname 0.0.0.0 --port 3000
```

Jika `NEXT_PUBLIC_API_BASE_URL` tetap default local, browser client otomatis mengubah API call dari `localhost:8000` ke host yang sama dengan frontend. Gunakan `CORS_ALLOWED_ORIGINS` untuk deployment yang lebih terkunci.

## Core API Endpoints

Unit and source data:

```text
GET/POST /api/plants/
GET/PUT/DELETE /api/plants/{plant_id}
GET/POST /api/plants/{plant_id}/emission-tests
PUT/DELETE /api/emission-tests/{emission_test_id}
GET/POST /api/plants/{plant_id}/site-readiness
PUT /api/site-readiness/{record_id}
GET/POST /api/plants/{plant_id}/hydrogen-strategy
PUT /api/hydrogen-strategy/{record_id}
GET /api/units/{plant_id}/profile
```

Scenario and simulation:

```text
GET/POST /api/plants/{plant_id}/scenarios
GET/PUT/DELETE /api/scenarios/{scenario_id}
GET/POST/PUT /api/scenarios/{scenario_id}/financial-assumptions
POST /api/scenarios/{scenario_id}/simulate
GET /api/scenarios/{scenario_id}/results
GET /api/scenario-results/{result_id}
```

Scoring, map, and sensitivity:

```text
POST /api/scoring/recalculate
GET /api/scoring/unit-ranking
GET /api/map/unit-opportunity
GET /api/map/ports
GET /api/map/economic-zones
GET /api/map/export-corridors
POST /api/sensitivity/run
GET /api/scenarios/{scenario_id}/sensitivity
```

Investor, settings, and LLM:

```text
GET /api/investor-case
GET /api/settings
GET /api/settings/{key}
PUT /api/settings/{key}
GET /api/settings/openrouter/provider
PUT /api/settings/openrouter/provider
GET /api/data-quality/summary
GET /api/llm/insights
POST /api/llm/summary/{scenario_id}
POST /api/llm/data-gap/{plant_id}
POST /api/llm/investor-memo/{scenario_id}
POST /api/llm/explain-sensitivity/{scenario_id}
```

Documents:

```text
POST /api/documents/upload
GET /api/documents
GET /api/documents/{document_id}
POST /api/documents/{document_id}/extract
POST /api/documents/{document_id}/ask
```

Pre-FEED:

```text
GET/POST /api/prefeed/packages
GET/PUT /api/prefeed/packages/{package_id}
POST /api/prefeed/packages/{package_id}/archive
GET/POST /api/prefeed/packages/{package_id}/documents
DELETE /api/prefeed/packages/{package_id}/documents/{link_id}
GET /api/prefeed/packages/{package_id}/gaps

GET/POST /api/prefeed/packages/{package_id}/cost-items
PUT/DELETE /api/prefeed/cost-items/{cost_item_id}
GET /api/prefeed/packages/{package_id}/cost-summary
GET/POST /api/prefeed/packages/{package_id}/vendor-proposals
PUT/DELETE /api/prefeed/vendor-proposals/{proposal_id}
GET /api/prefeed/packages/{package_id}/vendor-comparison
GET /api/prefeed/vendor-proposals/{proposal_id}/gaps
GET/POST /api/prefeed/scenarios/{scenario_id}/active-cost-basis

GET/POST /api/prefeed/packages/{package_id}/price-decks
PUT/DELETE /api/prefeed/price-decks/{deck_id}
POST /api/prefeed/price-decks/{deck_id}/activate
GET/POST /api/prefeed/packages/{package_id}/offtake-prospects
PUT/DELETE /api/prefeed/offtake-prospects/{prospect_id}
GET /api/prefeed/packages/{package_id}/offtake-summary
GET /api/prefeed/packages/{package_id}/offtake-gaps
GET/POST /api/prefeed/packages/{package_id}/mrv-assumptions
PUT/DELETE /api/prefeed/mrv-assumptions/{assumption_id}
GET /api/prefeed/packages/{package_id}/mrv-summary
GET /api/prefeed/packages/{package_id}/mrv-gaps

GET/POST /api/prefeed/packages/{package_id}/risks
PUT/DELETE /api/prefeed/risks/{risk_id}
GET /api/prefeed/packages/{package_id}/risk-summary
GET/POST /api/prefeed/packages/{package_id}/decision-gates
PUT/DELETE /api/prefeed/decision-gates/{gate_id}
GET /api/prefeed/packages/{package_id}/decision-gate-summary
GET /api/prefeed/packages/{package_id}/decision-blockers
GET /api/prefeed/packages/{package_id}/decision-next-actions
GET /api/prefeed/packages/{package_id}/decision-dashboard
POST /api/prefeed/packages/{package_id}/committee-brief
```

## Verification

```bash
docker compose config
cd backend && pytest -q
cd frontend && npm run build
```

Untuk local migration smoke test di luar Docker:

```bash
cd backend
DATABASE_URL=sqlite:////tmp/mechwiz_phase9_full.db .venv/bin/alembic upgrade head
```

## Batasan Penting

- Hasil simulation adalah deterministic screening, bukan FEED final.
- Port distance memakai haversine distance, bukan jarak jalan/pipa atau rute kapal aktual.
- Port readiness adalah proxy dari World Port Index, bukan terminal capacity study.
- Economic zone dan SG route adalah indikatif untuk prioritisasi, bukan rekomendasi investasi atau pelayaran.
- LLM hanya membuat narasi dari data tersimpan. Angka tetap berasal dari backend deterministic calculations.
- Jika input masih benchmark/low confidence, output harus dipakai sebagai bahan diskusi awal, bukan angka komite final.
