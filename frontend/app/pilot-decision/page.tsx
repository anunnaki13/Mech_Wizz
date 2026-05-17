import Link from "next/link";
import { AlertTriangle, ArrowRight, ClipboardCheck, Gauge, ShieldAlert, Target } from "lucide-react";

import { AppShell } from "@/components/layout/AppShell";
import { getPilotDecisionDashboard } from "@/lib/api";
import type { PilotDecisionCandidate, PilotDecisionDashboard } from "@/types/pilot-decision";

export const dynamic = "force-dynamic";

function labelFor(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

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

function gateLabel(candidate: PilotDecisionCandidate) {
  if (candidate.gate_status === "committee_ready") {
    return "Advance to committee";
  }
  if (candidate.gate_status === "blocked") {
    return "Blocked";
  }
  return "Continue validation";
}

function CandidateDecisionCard({ candidate }: { candidate: PilotDecisionCandidate }) {
  return (
    <article className={`pilot-candidate-card ${candidate.gate_status}`}>
      <div className="pilot-candidate-head">
        <div>
          <span>Decision rank #{candidate.decision_rank} · shortlist #{candidate.validation_rank}</span>
          <h3>{candidate.site_name}</h3>
          <p>{candidate.province ?? "Unknown"} · {formatNumber(candidate.capacity_mw, 1)} MW</p>
        </div>
        <strong>{formatNumber(candidate.evidence_adjusted_score, 3)}</strong>
      </div>
      <div className="pilot-gate-row">
        <em>{gateLabel(candidate)}</em>
        <span>{formatNumber(candidate.evidence_readiness_score, 1)}% evidence ready</span>
      </div>
      <div className="pilot-score-grid">
        <div><span>Shortlist</span><strong>{formatNumber(candidate.shortlist_score, 3)}</strong></div>
        <div><span>Verified</span><strong>{candidate.verified_items}</strong></div>
        <div><span>High gaps</span><strong>{candidate.high_priority_open_items}</strong></div>
        <div><span>Rejected</span><strong>{candidate.rejected_items}</strong></div>
        <div><span>Methanol</span><strong>{formatCompact(candidate.methanol_tpy, " t/y")}</strong></div>
        <div><span>Port</span><strong>{candidate.nearest_port_name ?? "-"}</strong></div>
      </div>
      <div className="pilot-actions-list">
        {candidate.next_actions.slice(0, 3).map((action) => (
          <p key={action}>{action}</p>
        ))}
      </div>
    </article>
  );
}

export default async function PilotDecisionPage() {
  let dashboard: PilotDecisionDashboard | null = null;
  let loadError = false;

  try {
    dashboard = await getPilotDecisionDashboard({ scheme: "align", limit: 3 });
  } catch {
    loadError = true;
  }

  const candidates = dashboard?.candidates ?? [];
  const leader = candidates[0] ?? null;

  return (
    <AppShell>
      <div className="pilot-decision-page">
        <section className="pilot-hero">
          <div>
            <div className="eyebrow">Phase 13 pilot decision</div>
            <h2>Pilot Decision Dashboard</h2>
            <p>
              Rekomendasi pilot berbasis shortlist deterministic dan evidence readiness. Ini membantu melihat kandidat
              terkuat, blocker, dan tindakan yang harus ditutup sebelum komite.
            </p>
          </div>
          <div className="hero-actions">
            <Link className="button secondary" href="/evidence">
              <ClipboardCheck size={16} aria-hidden="true" />
              Evidence
            </Link>
            <Link className="button secondary" href="/validation-pack">
              <ArrowRight size={16} aria-hidden="true" />
              Validation Pack
            </Link>
          </div>
        </section>

        {loadError ? (
          <div className="notice">
            Pilot decision data is not reachable. Start the backend API, run scoring, then refresh this page.
          </div>
        ) : null}

        <section className="summary-grid" aria-label="Pilot decision summary">
          <div className="summary-card primary">
            <span>Recommended candidate</span>
            <strong>{dashboard?.summary.recommended_candidate ?? "-"}</strong>
            <small>{dashboard?.summary.decision_message ?? "No decision data available"}</small>
          </div>
          <div className="summary-card">
            <span>Decision score</span>
            <strong>{formatNumber(leader?.evidence_adjusted_score, 3)}</strong>
            <small>70% shortlist + 30% evidence readiness minus penalties</small>
          </div>
          <div className="summary-card">
            <span>Evidence readiness</span>
            <strong>{formatNumber(dashboard?.summary.average_evidence_readiness_score, 1)}%</strong>
            <small>Average across Top 3</small>
          </div>
          <div className="summary-card">
            <span>Committee ready</span>
            <strong>{dashboard?.summary.committee_ready_count ?? 0}</strong>
            <small>Zero high gaps and readiness at least 80%</small>
          </div>
          <div className="summary-card">
            <span>Blocked</span>
            <strong>{dashboard?.summary.blocked_count ?? 0}</strong>
            <small>Rejected evidence exists</small>
          </div>
          <div className="summary-card">
            <span>High gaps</span>
            <strong>{dashboard?.summary.high_priority_open_items ?? 0}</strong>
            <small>Must close before approval</small>
          </div>
        </section>

        <section className="pilot-layout">
          <div className="pilot-main-stack">
            <section className="card report-panel pilot-lead-card">
              <Target size={20} aria-hidden="true" />
              <div>
                <h3>{leader ? `Current Lead: ${leader.site_name}` : "No Lead Candidate"}</h3>
                <p>{dashboard?.summary.decision_message ?? "Run scoring and evidence workspace first."}</p>
              </div>
              {leader ? (
                <div className="pilot-lead-metrics">
                  <div><span>Gate</span><strong>{gateLabel(leader)}</strong></div>
                  <div><span>Readiness</span><strong>{formatNumber(leader.evidence_readiness_score, 1)}%</strong></div>
                  <div><span>LCOM</span><strong>{formatNumber(leader.estimated_lcom_usd_ton, 0)} USD/t</strong></div>
                  <div><span>Methanol</span><strong>{formatCompact(leader.methanol_tpy, " t/y")}</strong></div>
                </div>
              ) : null}
            </section>

            <section className="card report-panel">
              <div className="section-title-row">
                <div>
                  <h3>Candidate Decision Ranking</h3>
                  <p>Rank keputusan tidak mengubah shortlist asal; ini hanya membaca status evidence terkini.</p>
                </div>
              </div>
              <div className="pilot-candidate-grid">
                {candidates.map((candidate) => (
                  <CandidateDecisionCard candidate={candidate} key={candidate.plant_id} />
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <h3>Methodology</h3>
              <div className="pilot-method-grid">
                {(dashboard?.methodology ?? []).map((item) => (
                  <div key={item}>
                    <Gauge size={16} aria-hidden="true" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <aside className="pilot-side-stack">
            <section className="card report-panel">
              <h3>Action Plan</h3>
              <div className="validation-list">
                {(dashboard?.action_plan ?? []).map((item) => (
                  <div key={item}><ClipboardCheck size={15} aria-hidden="true" /><span>{item}</span></div>
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <h3>Top Blockers</h3>
              <div className="pilot-blocker-list">
                {(dashboard?.blockers ?? []).slice(0, 8).map((blocker) => (
                  <div className={blocker.status} key={`${blocker.plant_id}-${blocker.evidence_key}-${blocker.status}`}>
                    <span>{blocker.site_name} · {labelFor(blocker.category)} · {labelFor(blocker.status)}</span>
                    <strong>{blocker.title}</strong>
                    <p>{blocker.recommendation}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="card report-panel">
              <h3>Warnings</h3>
              <div className="validation-list warning">
                {(dashboard?.warnings ?? []).map((warning) => (
                  <div key={warning}><ShieldAlert size={15} aria-hidden="true" /><span>{warning}</span></div>
                ))}
                {!dashboard?.warnings.length ? (
                  <div><AlertTriangle size={15} aria-hidden="true" /><span>No warnings available.</span></div>
                ) : null}
              </div>
            </section>
          </aside>
        </section>
      </div>
    </AppShell>
  );
}
