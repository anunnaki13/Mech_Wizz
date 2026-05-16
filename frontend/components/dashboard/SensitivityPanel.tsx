"use client";

import { Activity, PlayCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getScenarioSensitivity, runSensitivity } from "@/lib/api";
import type { SensitivityResult } from "@/types/sensitivity";
import type { UnitRankingRow } from "@/types/scoring";

type SensitivityPanelProps = {
  row: UnitRankingRow | null;
  scenarioId: string;
};

const variableLabels: Record<string, string> = {
  h2_price: "H2 price",
  electricity_price: "Electricity price",
  methanol_price: "Methanol price",
  capex: "CAPEX",
  capture_rate: "Capture rate",
  plant_availability: "Plant availability",
  carbon_credit_price: "Carbon credit price",
  exchange_rate: "Exchange rate",
};

function formatPercent(value: number | null) {
  if (value === null) {
    return "Not calculated";
  }
  return `${(value * 100).toLocaleString("en-US", { maximumFractionDigits: 1 })}%`;
}

function formatMoney(value: number | null, suffix = "") {
  if (value === null) {
    return "Not calculated";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 0, notation: "compact" })}${suffix}`;
}

function latestRunResults(results: SensitivityResult[]) {
  const latestRunId = results[0]?.run_id;
  return latestRunId ? results.filter((result) => result.run_id === latestRunId) : [];
}

export function SensitivityPanel({ row, scenarioId }: SensitivityPanelProps) {
  const [results, setResults] = useState<SensitivityResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const currentResults = useMemo(() => latestRunResults(results), [results]);
  const dominant = useMemo(
    () => [...currentResults].sort((a, b) => b.impact_score - a.impact_score)[0] ?? null,
    [currentResults],
  );
  const maxImpact = useMemo(
    () => Math.max(0.0001, ...currentResults.map((result) => result.impact_score)),
    [currentResults],
  );
  const warnings = useMemo(
    () => Array.from(new Set(currentResults.flatMap((result) => result.warnings))).slice(0, 4),
    [currentResults],
  );

  async function loadResults() {
    if (!row || !scenarioId) {
      setResults([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      setResults(await getScenarioSensitivity(scenarioId, row.plant_id));
    } catch {
      setErrorMessage("Sensitivity results are not reachable.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunSensitivity() {
    if (!row || !scenarioId) {
      return;
    }
    setRunning(true);
    setErrorMessage(null);
    try {
      const response = await runSensitivity({ scenarioId, plantId: row.plant_id });
      setResults(response.results);
    } catch {
      setErrorMessage("Sensitivity run failed.");
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    void loadResults();
  }, [row?.plant_id, scenarioId]);

  return (
    <section className="sensitivity-panel" aria-label="Sensitivity analysis">
      <div className="map-panel-header">
        <div>
          <h3>Sensitivity</h3>
          <span>{loading ? "Loading" : `${currentResults.length} variable${currentResults.length === 1 ? "" : "s"}`}</span>
        </div>
        <button
          className="button secondary"
          disabled={!row || !scenarioId || running}
          type="button"
          onClick={() => void handleRunSensitivity()}
        >
          <PlayCircle size={15} aria-hidden="true" />
          {running ? "Running" : "Run Sensitivity"}
        </button>
      </div>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}

      <div className="sensitivity-driver">
        <Activity size={18} aria-hidden="true" />
        <div>
          <span>Dominant sensitivity driver</span>
          <strong>{dominant ? variableLabels[dominant.variable_name] ?? dominant.variable_name : "Not calculated"}</strong>
        </div>
      </div>

      <div className="tornado-chart" aria-label="Sensitivity tornado chart">
        {currentResults
          .slice()
          .sort((a, b) => b.impact_score - a.impact_score)
          .map((result) => (
            <div className="tornado-row" key={result.id}>
              <span>{variableLabels[result.variable_name] ?? result.variable_name}</span>
              <div>
                <i style={{ width: `${Math.max(4, (result.impact_score / maxImpact) * 100)}%` }} />
              </div>
              <strong>{result.impact_score.toLocaleString("en-US", { maximumFractionDigits: 3 })}</strong>
            </div>
          ))}
        {!loading && currentResults.length === 0 ? <p className="muted">No sensitivity run stored.</p> : null}
      </div>

      {dominant ? (
        <div className="sensitivity-metrics">
          <div>
            <span>Low IRR</span>
            <strong>{formatPercent(dominant.low_irr)}</strong>
          </div>
          <div>
            <span>High IRR</span>
            <strong>{formatPercent(dominant.high_irr)}</strong>
          </div>
          <div>
            <span>Low NPV</span>
            <strong>{formatMoney(dominant.low_npv_usd, " USD")}</strong>
          </div>
          <div>
            <span>High NPV</span>
            <strong>{formatMoney(dominant.high_npv_usd, " USD")}</strong>
          </div>
          <div>
            <span>Low LCOM</span>
            <strong>{formatMoney(dominant.low_lcom_usd_per_ton, " USD/t")}</strong>
          </div>
          <div>
            <span>High LCOM</span>
            <strong>{formatMoney(dominant.high_lcom_usd_per_ton, " USD/t")}</strong>
          </div>
        </div>
      ) : null}

      {warnings.length > 0 ? (
        <div className="data-gap-list">
          {warnings.map((warning) => (
            <div className="data-gap-row" key={warning}>
              <strong>{warning}</strong>
              <span>warning</span>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
