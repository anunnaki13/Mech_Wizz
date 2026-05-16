# Penjelasan Detail MECH WIZ AI Digital Twin - GSD v2.0 Pre-FEED

Dokumen ini menjelaskan hasil implementasi MECH WIZ AI Digital Twin yang dibangun dengan workflow GSD. Fokus utama branch ini adalah mengubah blueprint awal MECH WIZ menjadi aplikasi kerja untuk screening pilot carbon-to-fuel dan memperluasnya sampai milestone v2.0 Pre-FEED.

## Ringkasan Produk

MECH WIZ AI Digital Twin adalah cockpit pre-feasibility dan Pre-FEED untuk membantu PLN NP memilih unit pilot terbaik, menilai kelayakan awal, dan menyiapkan narasi manajemen/investor tanpa membuat angka yang tidak didukung data.

Aplikasi terdiri dari:

- Backend FastAPI untuk API, persistence, kalkulasi deterministik, scoring, data quality, Pre-FEED package, risk, dan LLM prompt orchestration.
- Frontend Next.js untuk dashboard, scenario simulation, map intelligence, investor case, document workspace, settings, dan Pre-FEED workspace.
- Database PostgreSQL-ready dengan migration Alembic, tetap bisa dites lokal memakai SQLite.
- OpenRouter integration untuk narasi, tetapi hanya sebagai narrative layer. Angka tetap berasal dari backend deterministik.

Prinsip desain yang dijaga:

- Backend adalah source of truth untuk kalkulasi.
- Frontend tidak menghitung ulang IRR, NPV, LCOM, scoring, revenue, MRV, severity, readiness, blockers, atau next actions.
- LLM tidak boleh menciptakan angka, tidak boleh recalculation, dan harus memisahkan actual data, assumptions, confidence, dan gaps.
- Semua data Pre-FEED bersifat auditable dan package-scoped.

## Workflow GSD Yang Dipakai

Project ini dikerjakan memakai GSD secara bertahap:

1. `new project` dari blueprint MECH WIZ.
2. `ingest` addendum heatmap/map.
3. Per phase: context, UI spec, research/patterns, plan, execute, verify, review.
4. Commit atomic per phase atau per plan besar.
5. State GSD disimpan di `.planning/STATE.md`, roadmap di `.planning/ROADMAP.md`, dan requirements di `.planning/REQUIREMENTS.md`.

Artefak GSD penting:

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/`
- `.planning/milestones/`

## Milestone v1.0 MVP

Milestone v1.0 menyelesaikan lima phase awal sebagai simulator pre-feasibility.

### Phase 1 - MVP Spine & Unit Data

Hasil:

- Backend dan frontend skeleton.
- Data plant/unit awal.
- Emission test data.
- Hydrogen strategy input.
- Site readiness input.

Tujuan phase ini adalah memastikan aplikasi bisa menyimpan data unit dan menampilkan workspace dasar.

### Phase 2 - Scenario Simulation Engine

Hasil:

- Business scenario management.
- Financial assumptions per scenario.
- Deterministic calculation services.
- Stored `ScenarioResult`.
- Frontend scenario workbench.

Scenario outputs disimpan sebagai history. Saat Pre-FEED data berubah di phase berikutnya, history ini tidak ditimpa.

### Phase 3 - Strategy Dashboard & Ranking

Hasil:

- Unit scoring result.
- Opportunity, readiness, confidence, composite score, heatmap weight, ranking.
- MapLibre map dashboard.
- Sensitivity analysis.

Map intelligence memakai addendum `docs/MECH_WIZ_Heatmap_Map_Addendum.md`.

### Phase 4 - Investor Case & Data Quality

Hasil:

- Investor case aggregate endpoint.
- Investor dashboard.
- Data gap persistence.
- Editable default assumptions and scoring weights.
- Settings workspace.

Investor dashboard tetap membaca backend aggregate, bukan menghitung ulang di frontend.

### Phase 5 - LLM & Document Intelligence

Hasil:

- `LlmInsight` persistence.
- Direct OpenRouter Chat Completions integration.
- Executive summary, investor memo, data gap explanation, sensitivity explanation.
- Document upload, extraction, repository browsing, and document Q&A.

Jika `OPENROUTER_API_KEY` belum dikonfigurasi, backend tetap membuat failed insight record dan mengembalikan error eksplisit. Ini menjaga audit trail.

## Milestone v2.0 Pre-FEED

Milestone v2.0 memperluas simulator menjadi Pre-FEED decision workspace. Phase numbering dilanjutkan dari v1.0, sehingga dimulai dari Phase 6.

### Phase 6 - Pre-FEED Package Foundation

Tujuan:

Membuat package layer yang mengikat plant, scenario, dokumen, source metadata, confidence, dan package-level gaps.

Hasil:

- `PreFeedPackage`
- `PreFeedPackageDocument`
- Package CRUD APIs.
- Document linking by role.
- Package gap service.
- `/prefeed` package workspace.

Data penting:

- Package memiliki `package_status`, `owner_name`, `source_organization`, `received_date`, `version_label`, `data_status`, `confidence_level`, dan notes.
- Dokumen yang sudah ada di document layer direuse. Phase 6 tidak membuat upload system baru.

Endpoint utama:

```text
GET/POST /api/prefeed/packages
GET/PUT /api/prefeed/packages/{package_id}
POST /api/prefeed/packages/{package_id}/archive
GET/POST /api/prefeed/packages/{package_id}/documents
DELETE /api/prefeed/packages/{package_id}/documents/{link_id}
GET /api/prefeed/packages/{package_id}/gaps
```

### Phase 7 - Cost & Vendor Proposal Engine

Tujuan:

Membuat detailed CAPEX/OPEX line item, vendor/EPC proposal comparison, dan active cost basis selection.

Hasil:

- `PreFeedCostItem`
- `PreFeedVendorProposal`
- `PreFeedCostBasisSelection`
- Cost summary service.
- Vendor comparison and proposal gap service.
- Active cost basis API.
- Cost/vendor UI in `/prefeed`.

Keputusan penting:

- CAPEX dan OPEX disimpan sebagai line item detail.
- Aggregation dilakukan backend.
- Active cost basis selection tidak menulis ke `FinancialAssumption`.
- Scenario history tetap aman.

Endpoint utama:

```text
GET/POST /api/prefeed/packages/{package_id}/cost-items
PUT/DELETE /api/prefeed/cost-items/{cost_item_id}
GET /api/prefeed/packages/{package_id}/cost-summary
GET/POST /api/prefeed/packages/{package_id}/vendor-proposals
PUT/DELETE /api/prefeed/vendor-proposals/{proposal_id}
GET /api/prefeed/packages/{package_id}/vendor-comparison
GET /api/prefeed/vendor-proposals/{proposal_id}/gaps
GET/POST /api/prefeed/scenarios/{scenario_id}/active-cost-basis
```

### Phase 8 - Offtake & MRV Readiness

Tujuan:

Menambahkan commercial readiness dan carbon-market readiness agar package Pre-FEED punya revenue, offtake readiness, MRV readiness, carbon intensity, dan carbon credit screening.

Hasil:

- `PreFeedPriceDeck`
- `PreFeedOfftakeProspect`
- `PreFeedMrvAssumption`
- Offtake summary and gaps.
- MRV summary and gaps.
- Offtake/MRV UI in `/prefeed`.

Keputusan penting:

- Price deck package-scoped dan hanya satu yang active per package.
- Offtake revenue dihitung backend dari price deck dan prospects.
- MRV carbon intensity dan abatement bersifat indicative deterministic outputs.
- Output Phase 8 hanya scenario-ready patch/summary, tidak overwrite scenario tables.

Endpoint utama:

```text
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
```

### Phase 9 - Risk & Pre-FEED Decision Dashboard

Tujuan:

Mengemas seluruh data Pre-FEED menjadi management-facing decision workspace dengan risk register, decision gates, blockers, next actions, dashboard aggregate, dan committee brief.

Hasil:

- `PreFeedRisk`
- `PreFeedDecisionGate`
- Risk summary.
- Decision gate summary.
- Deterministic blockers.
- Deterministic next actions.
- Pre-FEED decision dashboard aggregate.
- Committee brief LLM workflow.
- Decision dashboard UI in `/prefeed`.

Keputusan penting:

- Risk dan gate records package-scoped.
- Risk severity = `likelihood * impact`, dihitung backend.
- Blockers dibuat backend dari high/escalated risks, critical/blocked gates, upstream package/cost/vendor/offtake/MRV gaps, dan missing active cost basis.
- Committee brief memakai `prefeed_committee_brief` insight type dan existing `LlmInsight` persistence.
- Brief prompt memakai deterministic package/dashboard context saja.

Endpoint utama:

```text
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

## Cara Menggunakan Aplikasi

1. Jalankan stack:

```bash
docker compose up --build
```

2. Jalankan migration:

```bash
docker compose exec backend alembic upgrade head
```

3. Seed data awal:

```bash
docker compose exec backend python -m app.seed
```

4. Buka aplikasi:

```text
http://localhost:3000/prefeed
```

Urutan pemakaian Pre-FEED yang disarankan:

1. Pilih plant dan scenario.
2. Buat Pre-FEED package.
3. Link dokumen pendukung.
4. Isi CAPEX/OPEX dan vendor proposals.
5. Pilih active cost basis.
6. Isi price deck dan offtake prospects.
7. Isi MRV assumptions.
8. Isi risk register dan decision gates.
9. Review decision dashboard, blockers, dan next actions.
10. Generate committee brief jika `OPENROUTER_API_KEY` tersedia.

## Backend Architecture

Backend mengikuti pola:

- Models: `backend/app/models/`
- Schemas: `backend/app/schemas/`
- Services: `backend/app/services/`
- Routers: `backend/app/routers/`
- Tests: `backend/tests/`
- Migrations: `backend/alembic/versions/`

Pre-FEED modules utama:

- `pre_feed_package.py`
- `pre_feed_cost.py`
- `pre_feed_market.py`
- `pre_feed_decision.py`

Service modules utama:

- `prefeed.py`
- `prefeed_costs.py`
- `prefeed_market.py`
- `prefeed_decision.py`
- `llm.py`

## Frontend Architecture

Frontend mengikuti pola:

- App routes: `frontend/app/`
- Components: `frontend/components/`
- API helpers: `frontend/lib/api.ts`
- Types: `frontend/types/`

Pre-FEED components utama:

- `PreFeedWorkspace`
- `CostVendorWorkspace`
- `OfftakeMrvWorkspace`
- `DecisionDashboardWorkspace`

Semua komponen tersebut memakai backend API helpers di `frontend/lib/api.ts`.

## Data Integrity And Audit

Hal yang dijaga selama implementasi:

- `FinancialAssumption` tidak diubah oleh Pre-FEED cost, market, risk, atau dashboard workflow.
- `ScenarioResult` tidak ditimpa oleh active cost basis, offtake summary, MRV summary, atau decision dashboard.
- `UnitScoringResult` dan `SensitivityResult` tetap menjadi historical outputs.
- Active cost basis selection disimpan sebagai record terpisah.
- LLM attempts selalu tersimpan di `LlmInsight`, termasuk failed attempts.

## Verification Yang Sudah Dilakukan

Verifikasi akhir branch:

```bash
docker compose config
cd backend && pytest -q
cd frontend && npm run build
cd backend && DATABASE_URL=sqlite:////tmp/mechwiz_phase9_full.db .venv/bin/alembic upgrade head
gsd-sdk query state.validate
```

Hasil:

- Backend tests: `47 passed`
- Frontend build: passed
- Fresh migration: passed through `0011_phase9_risk_decision`
- GSD state validation: valid
- `/prefeed`: HTTP 200 OK

## Branch GitHub

Branch yang berisi pekerjaan ini:

```text
codex/gsd-v2-prefeed
```

Pull request dapat dibuat dari:

```text
https://github.com/anunnaki13/Mech_Wizz/pull/new/codex/gsd-v2-prefeed
```

Branch ini tidak dipush langsung ke `main` karena remote `main` memiliki histori upload yang berbeda dari histori lokal. Push ke branch terpisah menghindari force push dan menjaga repo aman.

## Next Step

Opsional berikutnya:

- Buat Pull Request dari branch `codex/gsd-v2-prefeed`.
- Review UI `/prefeed` secara manual.
- Configure `OPENROUTER_API_KEY` untuk live committee brief generation.
- Jalankan `$gsd-complete-milestone` jika ingin mengarsipkan milestone v2.0 di GSD.
- Mulai milestone berikutnya dengan `$gsd-new-milestone`.
