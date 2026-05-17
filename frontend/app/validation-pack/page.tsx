import Link from "next/link";
import { AlertTriangle, ArrowRight, ClipboardCheck, Download, FileText, ShieldCheck } from "lucide-react";

import { AppShell } from "@/components/layout/AppShell";
import { API_BASE_URL, getTop3ValidationPack } from "@/lib/api";
import type { Top3ValidationPack, ValidationCandidatePack, ValidationEvidenceItem } from "@/types/validation-pack";

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

function statusLabel(item: ValidationEvidenceItem) {
  if (item.status === "available") {
    return "Available";
  }
  if (item.status === "critical_gap") {
    return "Critical gap";
  }
  return "Needs validation";
}

function CandidatePanel({ candidate }: { candidate: ValidationCandidatePack }) {
  const highPriority = candidate.validation_items.filter((item) => item.priority === "high" && item.status !== "available").length;
  return (
    <article className="validation-candidate-card">
      <div className="validation-candidate-head">
        <div>
          <span>Top 3 candidate</span>
          <h3>#{candidate.validation_rank} {candidate.site_name}</h3>
          <p>{candidate.province ?? "Unknown"} · {formatNumber(candidate.capacity_mw, 1)} MW</p>
        </div>
        <strong>{formatNumber(candidate.final_score, 3)}</strong>
      </div>
      <div className="validation-metric-grid">
        <div><span>Methanol</span><strong>{formatCompact(candidate.methanol_tpy, " t/y")}</strong></div>
        <div><span>Captured CO2</span><strong>{formatCompact(candidate.captured_co2_tpy, " t/y")}</strong></div>
        <div><span>Revenue</span><strong>{formatMoney(candidate.gross_revenue_usd_per_year)}</strong></div>
        <div><span>LCOM</span><strong>{formatNumber(candidate.estimated_lcom_usd_ton, 0)} USD/t</strong></div>
        <div><span>Port</span><strong>{candidate.nearest_port_name ?? "-"}</strong></div>
        <div><span>Evidence gaps</span><strong>{highPriority} high</strong></div>
      </div>
      <div className="validation-reason-list">
        {candidate.why_shortlisted.map((reason) => (
          <p key={reason}>{reason}</p>
        ))}
      </div>
    </article>
  );
}

export default async function ValidationPackPage() {
  let pack: Top3ValidationPack | null = null;
  let loadError = false;

  try {
    pack = await getTop3ValidationPack({ scheme: "align", limit: 3 });
  } catch {
    loadError = true;
  }

  const pdfHref = `${API_BASE_URL}/validation-pack/committee-memo.pdf?scheme=align&limit=3`;
  const candidates = pack?.candidates ?? [];

  return (
    <AppShell>
      <div className="validation-pack-page">
        <section className="validation-hero">
          <div>
            <div className="eyebrow">Phase 11 validation pack</div>
            <h2>Top 3 Validation Pack & Committee Memo</h2>
            <p>
              Paket diskusi manajemen untuk kandidat Top 3: bukti yang harus dikonfirmasi, perbandingan kandidat,
              pertanyaan komite, dan memo PDF.
            </p>
          </div>
          <div className="hero-actions">
            <a className="button secondary" href={pdfHref} target="_blank" rel="noreferrer">
              <Download size={16} aria-hidden="true" />
              Memo PDF
            </a>
            <Link className="button secondary" href="/shortlist">
              <ArrowRight size={16} aria-hidden="true" />
              Shortlist
            </Link>
            <Link className="button secondary" href="/evidence">
              <ClipboardCheck size={16} aria-hidden="true" />
              Evidence
            </Link>
          </div>
        </section>

        {loadError ? (
          <div className="notice">
            Validation pack data is not reachable. Start the backend API, run scoring, then refresh this page.
          </div>
        ) : null}

        <section className="summary-grid" aria-label="Validation summary">
          <div className="summary-card primary">
            <span>Lead candidate</span>
            <strong>{pack?.summary.lead_candidate ?? "-"}</strong>
            <small>{pack?.summary.candidate_count ?? 0} kandidat Top 3</small>
          </div>
          <div className="summary-card">
            <span>Captured CO2</span>
            <strong>{formatCompact(pack?.summary.total_captured_co2_tpy, " t/y")}</strong>
            <small>Top 3 portfolio</small>
          </div>
          <div className="summary-card">
            <span>e-methanol</span>
            <strong>{formatCompact(pack?.summary.total_methanol_tpy, " t/y")}</strong>
            <small>Top 3 screening output</small>
          </div>
          <div className="summary-card">
            <span>Revenue benchmark</span>
            <strong>{formatMoney(pack?.summary.total_gross_revenue_usd_per_year)}</strong>
            <small>Not contracted revenue</small>
          </div>
          <div className="summary-card">
            <span>Avg LCOM</span>
            <strong>{formatNumber(pack?.summary.average_lcom_usd_ton, 0)}</strong>
            <small>USD/t benchmark</small>
          </div>
          <div className="summary-card">
            <span>High evidence gaps</span>
            <strong>{pack?.summary.high_priority_evidence_count ?? 0}</strong>
            <small>Must close before decision</small>
          </div>
        </section>

        <section className="validation-layout">
          <div className="validation-main-stack">
            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Top 3 Candidate Packs</h3>
                  <p>Ringkasan kandidat yang harus dibawa ke validasi PLN, site, port, vendor, offtake, dan MRV.</p>
                </div>
              </div>
              <div className="validation-candidate-grid">
                {candidates.map((candidate) => (
                  <CandidatePanel candidate={candidate} key={candidate.plant_id} />
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Evidence Checklist</h3>
                  <p>Checklist ini adalah pekerjaan validasi sebelum komite memilih single pilot candidate.</p>
                </div>
              </div>
              <div className="validation-checklist">
                {candidates.map((candidate) => (
                  <div className="validation-checklist-group" key={candidate.plant_id}>
                    <h4>{candidate.site_name}</h4>
                    {candidate.validation_items.map((item) => (
                      <div className={`validation-evidence ${item.status}`} key={`${candidate.plant_id}-${item.category}-${item.item}`}>
                        <div>
                          <span>{item.category} · {item.priority}</span>
                          <strong>{item.item}</strong>
                          <p>{item.required_evidence}</p>
                        </div>
                        <em>{statusLabel(item)}</em>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Top 3 Comparison</h3>
                  <p>Axis perbandingan utama untuk diskusi komite.</p>
                </div>
              </div>
              <div className="validation-axis-grid">
                {(pack?.comparison_axes ?? []).map((axis) => (
                  <div key={axis.axis}>
                    <span>{axis.axis}</span>
                    <strong>{axis.leader ?? "-"}</strong>
                    <p>{axis.notes}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <aside className="validation-side-stack">
            <section className="card report-panel committee-memo-card">
              <FileText size={18} aria-hidden="true" />
              <h3>{pack?.committee_memo.title ?? "Committee Memo"}</h3>
              <strong>{pack?.committee_memo.recommendation ?? "-"}</strong>
              <p>{pack?.committee_memo.executive_summary ?? "-"}</p>
              <a className="button secondary" href={pdfHref} target="_blank" rel="noreferrer">
                <Download size={16} aria-hidden="true" />
                Open PDF
              </a>
            </section>

            <section className="card report-panel">
              <h3>Decision Ask</h3>
              <p>{pack?.committee_memo.decision_ask ?? "-"}</p>
            </section>

            <section className="card report-panel">
              <h3>Committee Questions</h3>
              <div className="validation-list">
                {(pack?.committee_memo.decision_questions ?? []).map((item) => (
                  <div key={item}><ClipboardCheck size={15} aria-hidden="true" /><span>{item}</span></div>
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <h3>No-Go Triggers</h3>
              <div className="validation-list warning">
                {(pack?.committee_memo.no_go_triggers ?? []).map((item) => (
                  <div key={item}><AlertTriangle size={15} aria-hidden="true" /><span>{item}</span></div>
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <h3>Caveats</h3>
              <div className="validation-list">
                {(pack?.warnings ?? []).map((item) => (
                  <div key={item}><ShieldCheck size={15} aria-hidden="true" /><span>{item}</span></div>
                ))}
              </div>
            </section>
          </aside>
        </section>
      </div>
    </AppShell>
  );
}
