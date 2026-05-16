"use client";

import type { ScenarioResult } from "@/types/scenario-result";

function formatNumber(value: number | null, suffix = "", maximumFractionDigits = 2) {
  if (value === null) {
    return "Not calculated";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits })}${suffix}`;
}

function formatCurrency(value: number | null, suffix = "") {
  if (value === null) {
    return "Not calculated";
  }
  return `$${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}${suffix}`;
}

function formatPercent(value: number | null) {
  if (value === null) {
    return "Not calculated";
  }
  return `${(value * 100).toLocaleString("en-US", { maximumFractionDigits: 2 })}%`;
}

export function SimulationResultPanel({ result }: { result: ScenarioResult | null }) {
  if (!result) {
    return <div className="notice">No scenario result has been stored for the selected scenario.</div>;
  }

  return (
    <div className="section-stack">
      <div className="result-grid">
        <div className="result-cell">
          <span className="metric-label">Captured CO2</span>
          <strong>{formatNumber(result.captured_co2_ton_per_year, " t/y", 0)}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">E-Methanol</span>
          <strong>{formatNumber(result.methanol_ton_per_year, " t/y", 0)}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">H2 Required</span>
          <strong>{formatNumber(result.h2_required_ton_per_year, " t/y", 0)}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">Electrolyzer</span>
          <strong>{formatNumber(result.electrolyzer_required_mw, " MW")}</strong>
        </div>
      </div>

      <div className="result-grid">
        <div className="result-cell">
          <span className="metric-label">Gross Revenue</span>
          <strong>{formatCurrency(result.gross_revenue_usd_per_year, "/y")}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">LCOM</span>
          <strong>{formatCurrency(result.lcom_usd_per_ton, "/t")}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">NPV</span>
          <strong>{formatCurrency(result.npv_usd)}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">IRR</span>
          <strong>{formatPercent(result.irr)}</strong>
        </div>
        <div className="result-cell">
          <span className="metric-label">Payback</span>
          <strong>{formatNumber(result.payback_years, " years")}</strong>
        </div>
      </div>

      <div className="chip-row">
        <span className="chip">confidence_level: {result.confidence_level}</span>
        <span className="chip">calculation_version: {result.calculation_version}</span>
        <span className="chip">{new Date(result.created_at).toLocaleString("en-US")}</span>
      </div>

      {result.missing_inputs.length > 0 ? (
        <div className="notice">
          Missing or assumption-limited inputs: {result.missing_inputs.join(", ")}
        </div>
      ) : null}
    </div>
  );
}
