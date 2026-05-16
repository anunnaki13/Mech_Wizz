"use client";

import type { UnitProfile, UnitRankingRow } from "@/types/scoring";

type ScoreBreakdownPanelProps = {
  row: UnitRankingRow | null;
  profile: UnitProfile | null;
  loading: boolean;
};

function formatNumber(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1 })}${suffix}`;
}

function formatScore(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 });
}

function scorePercent(value: number | null | undefined) {
  return `${Math.max(0, Math.min(1, value ?? 0)) * 100}%`;
}

function confidenceChip(value: string | undefined) {
  return value || "unknown";
}

export function ScoreBreakdownPanel({ loading, profile, row }: ScoreBreakdownPanelProps) {
  const confidenceLabels = profile?.confidence_labels ?? {};
  return (
    <aside className="map-side-panel" aria-label="Selected unit profile">
      <div className="map-panel-header">
        <div>
          <h3>Selected Unit Profile</h3>
          <span>{row ? `${row.site_name} ${row.unit_name}` : loading ? "Loading profile" : "No unit selected"}</span>
        </div>
        {row ? <span className="chip">Rank #{row.rank}</span> : null}
      </div>

      {row ? (
        <>
          <div className="score-summary">
            <div>
              <span>Composite Score</span>
              <strong>{formatScore(row.composite_score)}</strong>
            </div>
            <div>
              <span>Opportunity Score</span>
              <strong>{formatScore(row.opportunity_score)}</strong>
            </div>
            <div>
              <span>Readiness Score</span>
              <strong>{formatScore(row.readiness_score)}</strong>
            </div>
            <div>
              <span>Confidence Score</span>
              <strong>{formatScore(row.confidence_score)}</strong>
            </div>
          </div>

          <div className="score-bars" aria-label="Score breakdown">
            <div>
              <span>Composite</span>
              <div><i style={{ width: scorePercent(row.composite_score) }} /></div>
            </div>
            <div>
              <span>Opportunity</span>
              <div><i style={{ width: scorePercent(row.opportunity_score) }} /></div>
            </div>
            <div>
              <span>Readiness</span>
              <div><i style={{ width: scorePercent(row.readiness_score) }} /></div>
            </div>
            <div>
              <span>Confidence</span>
              <div><i style={{ width: scorePercent(row.confidence_score) }} /></div>
            </div>
          </div>

          <div className="detail-list">
            <div className="detail-row">
              <span>Captured CO2</span>
              <span>{formatNumber(row.captured_co2_tpy, " t/y")}</span>
            </div>
            <div className="detail-row">
              <span>E-Methanol</span>
              <span>{formatNumber(row.methanol_tpy, " t/y")}</span>
            </div>
            <div className="detail-row">
              <span>H2 Required</span>
              <span>{formatNumber(row.h2_required_tpy, " t/y")}</span>
            </div>
            <div className="detail-row">
              <span>Estimated LCOM</span>
              <span>{formatNumber(row.estimated_lcom_usd_ton, " USD/t")}</span>
            </div>
            <div className="detail-row">
              <span>Recommended Scheme</span>
              <span>{row.recommended_scheme}</span>
            </div>
            <div className="detail-row">
              <span>Key Bottleneck</span>
              <span>{row.key_bottleneck}</span>
            </div>
          </div>

          <div className="confidence-strip" aria-label="Data confidence">
            <span className="chip">Plant: {confidenceChip(confidenceLabels.plant)}</span>
            <span className="chip">Scenario: {confidenceChip(confidenceLabels.scenario)}</span>
            <span className="chip">Simulation: {confidenceChip(confidenceLabels.simulation)}</span>
            <span className="chip">Scoring: {confidenceChip(confidenceLabels.scoring)}</span>
          </div>

          <div className="data-gap-list">
            <h4>Data Gaps</h4>
            {(profile?.data_gaps ?? []).slice(0, 6).map((gap) => (
              <div key={`${gap.module}-${gap.name}`} className="data-gap-row">
                <strong>{gap.name}</strong>
                <span>{gap.impact} impact / {gap.priority}</span>
              </div>
            ))}
            {profile?.data_gaps?.length === 0 ? <p className="muted">No active score-derived gaps.</p> : null}
          </div>
        </>
      ) : (
        <div className="notice">No selected unit profile.</div>
      )}
    </aside>
  );
}
