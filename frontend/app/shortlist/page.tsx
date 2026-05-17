import Link from "next/link";
import { AlertTriangle, ArrowRight, BadgeCheck, FileText, Gauge, Ship, TrendingUp } from "lucide-react";

import { AppShell } from "@/components/layout/AppShell";
import { getShortlistDecisionMatrix } from "@/lib/api";
import type { ShortlistCandidate, ShortlistDecisionMatrix } from "@/types/shortlist";

export const dynamic = "force-dynamic";

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
  if (Math.abs(value) >= 1_000_000_000) {
    return `USD ${(value / 1_000_000_000).toLocaleString("en-US", { maximumFractionDigits: 2 })}B`;
  }
  if (Math.abs(value) >= 1_000_000) {
    return `USD ${(value / 1_000_000).toLocaleString("en-US", { maximumFractionDigits: 1 })}M`;
  }
  return `USD ${formatNumber(value)}`;
}

function recommendationLabel(value: string) {
  const labels: Record<string, string> = {
    shortlist_top3: "Top 3",
    shortlist_top5: "Top 5",
    watchlist: "Watchlist",
  };
  return labels[value] ?? value;
}

function readinessLabel(value: string) {
  const labels: Record<string, string> = {
    ready_for_top3_validation: "Ready for Top 3 validation",
    validate_next: "Validate next",
    watchlist: "Watchlist",
    defer: "Defer",
  };
  return labels[value] ?? value;
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const width = `${Math.round(value * 100)}%`;
  return (
    <div className="shortlist-score-row">
      <span>{label}</span>
      <div aria-hidden="true">
        <i style={{ width }} />
      </div>
      <strong>{formatNumber(value, 3)}</strong>
    </div>
  );
}

function CandidateCard({ candidate }: { candidate: ShortlistCandidate }) {
  return (
    <article className="shortlist-candidate-card">
      <div className="shortlist-candidate-head">
        <div>
          <span>{recommendationLabel(candidate.recommendation)}</span>
          <h3>#{candidate.shortlist_rank} {candidate.site_name}</h3>
          <p>{candidate.province ?? "Unknown"} · {formatNumber(candidate.capacity_mw, 1)} MW</p>
        </div>
        <strong>{formatNumber(candidate.score_breakdown.final_score, 3)}</strong>
      </div>
      <div className="shortlist-score-stack">
        <ScoreBar label="Screening" value={candidate.score_breakdown.screening_score} />
        <ScoreBar label="Economics" value={candidate.score_breakdown.economics_score} />
        <ScoreBar label="Logistics" value={candidate.score_breakdown.logistics_score} />
        <ScoreBar label="Confidence" value={candidate.score_breakdown.confidence_score} />
      </div>
      <div className="shortlist-card-metrics">
        <div><span>Port</span><strong>{candidate.nearest_port_name ?? "-"}</strong></div>
        <div><span>Distance</span><strong>{formatNumber(candidate.nearest_port_distance_km, 1)} km</strong></div>
        <div><span>Methanol</span><strong>{formatCompact(candidate.methanol_tpy, " t/y")}</strong></div>
        <div><span>LCOM</span><strong>{formatNumber(candidate.estimated_lcom_usd_ton, 0)} USD/t</strong></div>
      </div>
      <div className="shortlist-rationale">
        <strong>{readinessLabel(candidate.readiness_label)}</strong>
        {candidate.decision_rationale.map((item) => (
          <p key={item}>{item}</p>
        ))}
      </div>
    </article>
  );
}

export default async function ShortlistPage() {
  let matrix: ShortlistDecisionMatrix | null = null;
  let loadError = false;

  try {
    matrix = await getShortlistDecisionMatrix({ scheme: "align", topN: 5 });
  } catch {
    loadError = true;
  }

  const candidates = matrix?.candidates ?? [];
  const topFive = candidates.slice(0, matrix?.top_n ?? 5);

  return (
    <AppShell>
      <div className="shortlist-page">
        <section className="shortlist-hero">
          <div>
            <div className="eyebrow">Phase 10 decision matrix</div>
            <h2>Economic Calibration & Shortlist Validation</h2>
            <p>
              Prioritas Top 3/Top 5 dari 26 PLTU target dengan kombinasi screening teknis, ekonomi,
              kesiapan pelabuhan, dan confidence data.
            </p>
          </div>
          <div className="hero-actions">
            <Link className="button secondary" href="/dashboard/map">
              <Ship size={16} aria-hidden="true" />
              Map Context
            </Link>
            <Link className="button secondary" href="/dashboard">
              <ArrowRight size={16} aria-hidden="true" />
              Summary
            </Link>
            <Link className="button secondary" href="/validation-pack">
              <FileText size={16} aria-hidden="true" />
              Validation Pack
            </Link>
          </div>
        </section>

        {loadError ? (
          <div className="notice">
            Backend shortlist data is not reachable. Start the backend API, run scoring, then refresh this page.
          </div>
        ) : null}

        <section className="summary-grid" aria-label="Shortlist summary">
          <div className="summary-card primary">
            <span>Top shortlist</span>
            <strong>{matrix?.summary.top_candidate ?? "-"}</strong>
            <small>Score {formatNumber(matrix?.summary.top_score, 3)}</small>
          </div>
          <div className="summary-card">
            <span>Candidate pool</span>
            <strong>{matrix?.summary.candidate_count ?? 0}</strong>
            <small>{matrix?.summary.shortlist_count ?? 0} masuk Top 5</small>
          </div>
          <div className="summary-card">
            <span>Top 5 captured CO2</span>
            <strong>{formatCompact(matrix?.summary.shortlist_captured_co2_tpy, " t/y")}</strong>
            <small>Portfolio shortlist</small>
          </div>
          <div className="summary-card">
            <span>Top 5 e-methanol</span>
            <strong>{formatCompact(matrix?.summary.shortlist_methanol_tpy, " t/y")}</strong>
            <small>Indicative production</small>
          </div>
          <div className="summary-card">
            <span>Top 5 revenue</span>
            <strong>{formatMoney(matrix?.summary.shortlist_gross_revenue_usd_per_year)}</strong>
            <small>Benchmark only</small>
          </div>
          <div className="summary-card">
            <span>Avg shortlist LCOM</span>
            <strong>{formatNumber(matrix?.summary.average_shortlist_lcom_usd_ton, 0)}</strong>
            <small>USD/t</small>
          </div>
        </section>

        <section className="shortlist-method">
          <div>
            <Gauge size={18} aria-hidden="true" />
            <strong>Metode</strong>
            <span>{matrix?.method ?? "No method available"}</span>
          </div>
          <div>
            <TrendingUp size={18} aria-hidden="true" />
            <strong>Economics</strong>
            <span>Revenue, methanol potential, dan LCOM relatif terhadap kandidat lain.</span>
          </div>
          <div>
            <Ship size={18} aria-hidden="true" />
            <strong>Logistics</strong>
            <span>Kesiapan pelabuhan dan jarak indikatif ke port terdekat.</span>
          </div>
          <div>
            <BadgeCheck size={18} aria-hidden="true" />
            <strong>Confidence</strong>
            <span>Confidence score dikurangi penalti data gap.</span>
          </div>
        </section>

        <section className="shortlist-layout">
          <div className="shortlist-main-stack">
            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Top 5 Validation Candidates</h3>
                  <p>Kandidat ini menjadi prioritas untuk validasi ekonomi, pelabuhan, data site, dan pembahasan PLN/partner.</p>
                </div>
              </div>
              <div className="shortlist-card-grid">
                {topFive.map((candidate) => (
                  <CandidateCard candidate={candidate} key={candidate.plant_id} />
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Full Decision Matrix</h3>
                  <p>Urutan ini bisa berubah setelah CAPEX/OPEX, port handling, dan data PLN diverifikasi.</p>
                </div>
              </div>
              <div className="table-wrap">
                <table className="data-table shortlist-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Site</th>
                      <th>Final</th>
                      <th>Economics</th>
                      <th>Logistics</th>
                      <th>Confidence</th>
                      <th>Port</th>
                      <th>Methanol</th>
                      <th>Revenue</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidates.map((candidate) => (
                      <tr key={candidate.plant_id}>
                        <td>#{candidate.shortlist_rank}</td>
                        <td>
                          <strong>{candidate.site_name}</strong>
                          <span>{candidate.province ?? "Unknown"} · {recommendationLabel(candidate.recommendation)}</span>
                        </td>
                        <td>{formatNumber(candidate.score_breakdown.final_score, 3)}</td>
                        <td>{formatNumber(candidate.score_breakdown.economics_score, 3)}</td>
                        <td>{formatNumber(candidate.score_breakdown.logistics_score, 3)}</td>
                        <td>{candidate.data_confidence_label}</td>
                        <td>
                          <strong>{candidate.nearest_port_name ?? "-"}</strong>
                          <span>{formatNumber(candidate.nearest_port_distance_km, 1)} km</span>
                        </td>
                        <td>{formatCompact(candidate.methanol_tpy)}</td>
                        <td>{formatMoney(candidate.gross_revenue_usd_per_year)}</td>
                        <td>{candidate.next_actions[0] ?? "-"}</td>
                      </tr>
                    ))}
                    {!loadError && candidates.length === 0 ? (
                      <tr>
                        <td colSpan={10}>No shortlist records yet. Run simulations and scoring first.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          <aside className="shortlist-side-stack">
            <section className="card report-panel">
              <h3>Caveats</h3>
              <div className="shortlist-warning-list">
                {(matrix?.warnings ?? []).map((warning) => (
                  <div key={warning}>
                    <AlertTriangle size={16} aria-hidden="true" />
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            </section>
            <section className="card report-panel">
              <h3>Next Validation Work</h3>
              <div className="value-list">
                <div><strong>Top 3 site pack</strong><span>Konfirmasi koordinat, lahan, utilitas, stack, dan data operasi.</span></div>
                <div><strong>Port commercial check</strong><span>Konfirmasi jetty, terminal, handling methanol, storage, dan export route.</span></div>
                <div><strong>CAPEX/OPEX calibration</strong><span>Masukkan vendor quotation atau Pre-FEED estimate untuk LCOM yang lebih tajam.</span></div>
                <div><strong>Committee memo</strong><span>Bandingkan Top 3 secara teknis, komersial, data confidence, dan decision blockers.</span></div>
              </div>
            </section>
          </aside>
        </section>
      </div>
    </AppShell>
  );
}
