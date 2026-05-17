import Link from "next/link";
import { AlertTriangle, ArrowRight, BarChart3, Factory, FileText, MapPinned, Ship, Zap } from "lucide-react";

import { AppShell } from "@/components/layout/AppShell";
import { getPlants, getUnitRanking } from "@/lib/api";
import type { Plant } from "@/types/plant";
import type { UnitRankingRow } from "@/types/scoring";

export const dynamic = "force-dynamic";

type DashboardData = {
  plants: Plant[];
  ranking: UnitRankingRow[];
};

function formatNumber(value: number | null | undefined, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

function formatCompact(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1, notation: "compact" })}${suffix}`;
}

function formatMoney(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  const absolute = Math.abs(value);
  if (absolute >= 1_000_000_000) {
    return `USD ${(value / 1_000_000_000).toLocaleString("en-US", { maximumFractionDigits: 2 })}B`;
  }
  if (absolute >= 1_000_000) {
    return `USD ${(value / 1_000_000).toLocaleString("en-US", { maximumFractionDigits: 1 })}M`;
  }
  return `USD ${formatNumber(value)}`;
}

function average(values: number[]) {
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
}

function sum(values: Array<number | null | undefined>) {
  return values.reduce<number>((total, value) => total + (value ?? 0), 0);
}

function confidenceCounts(plants: Plant[]) {
  return plants.reduce(
    (counts, plant) => {
      const key = plant.confidence_level ?? "unknown";
      counts[key] = (counts[key] ?? 0) + 1;
      return counts;
    },
    {} as Record<string, number>,
  );
}

async function loadDashboardData(): Promise<DashboardData> {
  const [plants, ranking] = await Promise.all([getPlants(), getUnitRanking({ scheme: "align" })]);
  return {
    plants,
    ranking,
  };
}

export default async function DashboardPage() {
  let data: DashboardData = { plants: [], ranking: [] };
  let loadError = false;

  try {
    data = await loadDashboardData();
  } catch {
    loadError = true;
  }

  const { plants, ranking } = data;
  const topCandidate = ranking[0] ?? null;
  const totalCapacity = sum(plants.map((plant) => plant.capacity_mw));
  const totalCo2 = sum(ranking.map((row) => row.co2_tpy));
  const capturedCo2 = sum(ranking.map((row) => row.captured_co2_tpy));
  const methanol = sum(ranking.map((row) => row.methanol_tpy));
  const h2Required = sum(ranking.map((row) => row.h2_required_tpy));
  const electrolyzer = sum(ranking.map((row) => row.electrolyzer_required_mw));
  const grossRevenue = sum(ranking.map((row) => row.gross_revenue_usd_per_year));
  const averageLcom = average(ranking.map((row) => row.estimated_lcom_usd_ton ?? 0).filter((value) => value > 0));
  const confidence = confidenceCounts(plants);
  const topTen = ranking.slice(0, 10);

  return (
    <AppShell>
      <div className="executive-dashboard">
        <section className="dashboard-hero">
          <div>
            <div className="eyebrow">26-site PLTU screening cockpit</div>
            <h2>MECH WIZ Target Screening Summary</h2>
            <p>
              Ringkasan nilai, output, dan prioritas awal dari dataset PLTU target untuk CO2 capture to
              e-methanol. Dashboard ini membaca hasil simulasi dan scoring terbaru dari backend.
            </p>
          </div>
          <div className="hero-actions">
            <Link className="button secondary" href="/dashboard/map">
              <MapPinned size={16} aria-hidden="true" />
              Open Map
            </Link>
            <Link className="button secondary" href="/investor">
              <FileText size={16} aria-hidden="true" />
              Investor Case
            </Link>
            <Link className="button secondary" href="/shortlist">
              <BarChart3 size={16} aria-hidden="true" />
              Shortlist
            </Link>
          </div>
        </section>

        {loadError ? (
          <div className="notice">
            Backend data is not reachable. Start the backend API, run the curated PLTU importer, then refresh this
            page.
          </div>
        ) : null}

        <section className="summary-grid" aria-label="Executive summary KPIs">
          <div className="summary-card primary">
            <span>Top candidate</span>
            <strong>{topCandidate?.site_name ?? "-"}</strong>
            <small>{topCandidate ? `${topCandidate.province ?? "Unknown"} · ${formatNumber(topCandidate.capacity_mw, 1)} MW` : "No ranked site"}</small>
          </div>
          <div className="summary-card">
            <span>Target PLTU</span>
            <strong>{plants.length}</strong>
            <small>{formatNumber(totalCapacity, 1)} MW total kapasitas</small>
          </div>
          <div className="summary-card">
            <span>Potensi CO2</span>
            <strong>{formatCompact(totalCo2, " t/y")}</strong>
            <small>{formatCompact(capturedCo2, " t/y")} captured @ 85%</small>
          </div>
          <div className="summary-card">
            <span>Potensi e-methanol</span>
            <strong>{formatCompact(methanol, " t/y")}</strong>
            <small>{formatCompact(h2Required, " t/y")} H2 required</small>
          </div>
          <div className="summary-card">
            <span>Electrolyzer indikatif</span>
            <strong>{formatCompact(electrolyzer, " MW")}</strong>
            <small>Screening scale, not EPC sizing</small>
          </div>
          <div className="summary-card">
            <span>Gross revenue benchmark</span>
            <strong>{formatMoney(grossRevenue)}</strong>
            <small>Avg LCOM {formatNumber(averageLcom, 0)} USD/t</small>
          </div>
        </section>

        <section className="dashboard-warning">
          <AlertTriangle size={18} aria-hidden="true" />
          <div>
            <strong>Status: screening/pre-feasibility.</strong>
            <p>
              Angka belum menggantikan konfirmasi PLN, site visit, data CEMS/DCS, stack test aktual, vendor quotation,
              terminal operator confirmation, atau offtake contract. Output ini dipakai untuk memilih prioritas studi,
              bukan investment decision final.
            </p>
          </div>
        </section>

        <section className="dashboard-layout">
          <div className="dashboard-main-stack">
            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Apa Yang Dihitung Aplikasi</h3>
                  <p>Output ini menjelaskan value dataset dan alasan ranking kandidat.</p>
                </div>
              </div>
              <div className="calculation-grid">
                <div>
                  <Factory size={18} aria-hidden="true" />
                  <strong>Total CO2</strong>
                  <span>Estimasi CO2 tahunan dari benchmark stack berbasis kapasitas.</span>
                </div>
                <div>
                  <BarChart3 size={18} aria-hidden="true" />
                  <strong>Captured CO2</strong>
                  <span>CO2 yang bisa masuk proses dengan capture rate 85%.</span>
                </div>
                <div>
                  <Zap size={18} aria-hidden="true" />
                  <strong>E-methanol & H2</strong>
                  <span>Potensi methanol, kebutuhan hydrogen, dan ukuran electrolyzer.</span>
                </div>
                <div>
                  <Ship size={18} aria-hidden="true" />
                  <strong>Ranking & map</strong>
                  <span>Composite score, heatmap weight, dan konteks pelabuhan/koridor ekspor.</span>
                </div>
              </div>
            </section>

            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Top 10 Kandidat Screening</h3>
                  <p>Ranking saat ini didominasi skala kapasitas dan CO2. Kalibrasi ekonomi/logistik berikutnya akan memperketat shortlist.</p>
                </div>
                <Link className="section-link" href="/dashboard/map">
                  Detail map <ArrowRight size={14} aria-hidden="true" />
                </Link>
              </div>
              <div className="table-wrap">
                <table className="data-table executive-ranking-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Site</th>
                      <th>MW</th>
                      <th>Score</th>
                      <th>CO2 t/y</th>
                      <th>Methanol t/y</th>
                      <th>H2 t/y</th>
                      <th>LCOM</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topTen.map((row) => (
                      <tr key={row.scoring_result_id}>
                        <td>#{row.rank}</td>
                        <td>
                          <strong>{row.site_name}</strong>
                          <span>{row.province ?? "Unknown"}</span>
                        </td>
                        <td>{formatNumber(row.capacity_mw, 1)}</td>
                        <td>{formatNumber(row.composite_score, 3)}</td>
                        <td>{formatCompact(row.co2_tpy)}</td>
                        <td>{formatCompact(row.methanol_tpy)}</td>
                        <td>{formatCompact(row.h2_required_tpy)}</td>
                        <td>{formatNumber(row.estimated_lcom_usd_ton, 0)}</td>
                        <td>{row.data_confidence_label}</td>
                      </tr>
                    ))}
                    {!loadError && topTen.length === 0 ? (
                      <tr>
                        <td colSpan={9}>No scoring records yet. Run simulations and scoring first.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          <aside className="dashboard-side-stack">
            <section className="card report-panel">
              <h3>Data Confidence</h3>
              <div className="confidence-summary">
                <div><strong>{confidence.high ?? 0}</strong><span>High</span></div>
                <div><strong>{confidence.medium ?? 0}</strong><span>Medium</span></div>
                <div><strong>{confidence.low ?? 0}</strong><span>Low</span></div>
              </div>
              <p className="muted">
                Low confidence saat ini terutama menandai site dengan alamat publik tetapi belum punya koordinat fence-line
                yang kuat.
              </p>
            </section>

            <section className="card report-panel">
              <h3>Value Yang Diberikan</h3>
              <div className="value-list">
                <div><strong>Strategic shortlist</strong><span>Memilih site prioritas untuk studi lanjut.</span></div>
                <div><strong>Scale sizing</strong><span>Membaca kebutuhan CO2, H2, dan electrolyzer.</span></div>
                <div><strong>Data gap control</strong><span>Membedakan data kuat, medium, dan indikatif.</span></div>
                <div><strong>Pre-FEED preparation</strong><span>Menyiapkan pertanyaan vendor, site, offtake, dan pelabuhan.</span></div>
              </div>
            </section>

            <section className="card next-phase-panel">
              <span>Current validation work</span>
              <h3>Phase 11</h3>
              <p>Top 3 Validation Pack & Committee Memo.</p>
              <ul>
                <li>Evidence checklist Top 3</li>
                <li>Perbandingan kandidat utama</li>
                <li>Committee memo PDF</li>
                <li>No-go trigger validasi</li>
              </ul>
              <Link className="section-link" href="/validation-pack">
                Open validation pack <ArrowRight size={14} aria-hidden="true" />
              </Link>
            </section>
          </aside>
        </section>
      </div>
    </AppShell>
  );
}
