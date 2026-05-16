"use client";

import { Activity, PlayCircle, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getScenarioSensitivity, getUnitRanking, runSensitivity } from "@/lib/api";
import type { SensitivityResult, SensitivityVariable } from "@/types/sensitivity";
import type { UnitRankingRow } from "@/types/scoring";

const sensitivityVariables: Array<{ id: SensitivityVariable; label: string }> = [
  { id: "h2_price", label: "H2 price" },
  { id: "electricity_price", label: "Electricity price" },
  { id: "methanol_price", label: "Methanol price" },
  { id: "capex", label: "CAPEX" },
  { id: "capture_rate", label: "Capture rate" },
  { id: "plant_availability", label: "Plant availability" },
  { id: "carbon_credit_price", label: "Carbon credit price" },
  { id: "exchange_rate", label: "Exchange rate" },
];

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
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1, notation: "compact" })}${suffix}`;
}

function formatNumber(value: number | null) {
  if (value === null) {
    return "Not calculated";
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: 3 });
}

function variableLabel(variableName: string) {
  return sensitivityVariables.find((variable) => variable.id === variableName)?.label ?? variableName;
}

function latestRunResults(results: SensitivityResult[]) {
  const latestRunId = results[0]?.run_id;
  return latestRunId ? results.filter((result) => result.run_id === latestRunId) : [];
}

export function SensitivityWorkspace() {
  const [ranking, setRanking] = useState<UnitRankingRow[]>([]);
  const [selectedScoringId, setSelectedScoringId] = useState("");
  const [results, setResults] = useState<SensitivityResult[]>([]);
  const [selectedVariables, setSelectedVariables] = useState<SensitivityVariable[]>(
    sensitivityVariables.map((variable) => variable.id),
  );
  const [loading, setLoading] = useState(true);
  const [loadingResults, setLoadingResults] = useState(false);
  const [running, setRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const selectedRow = useMemo(
    () => ranking.find((row) => row.scoring_result_id === selectedScoringId) ?? ranking[0] ?? null,
    [ranking, selectedScoringId],
  );
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
    () => Array.from(new Set(currentResults.flatMap((result) => result.warnings))).slice(0, 5),
    [currentResults],
  );

  async function loadRanking(preferredScoringId = selectedScoringId) {
    setLoading(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const rows = await getUnitRanking();
      setRanking(rows);
      const nextScoringId =
        preferredScoringId && rows.some((row) => row.scoring_result_id === preferredScoringId)
          ? preferredScoringId
          : rows[0]?.scoring_result_id || "";
      setSelectedScoringId(nextScoringId);
      if (rows.length === 0) {
        setStatusMessage("No scoring records are available. Run simulations and scoring first.");
      }
    } catch {
      setErrorMessage("Sensitivity reference data is not reachable.");
      setRanking([]);
      setSelectedScoringId("");
    } finally {
      setLoading(false);
    }
  }

  async function loadSensitivity(row = selectedRow) {
    if (!row) {
      setResults([]);
      return;
    }
    setLoadingResults(true);
    setErrorMessage(null);
    try {
      const records = await getScenarioSensitivity(row.scenario_id, row.plant_id);
      setResults(records);
      if (records.length === 0) {
        setStatusMessage("No sensitivity run stored for this unit yet.");
      }
    } catch {
      setErrorMessage("Sensitivity results are not reachable.");
      setResults([]);
    } finally {
      setLoadingResults(false);
    }
  }

  async function handleRunSensitivity() {
    if (!selectedRow || selectedVariables.length === 0) {
      return;
    }
    setRunning(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const response = await runSensitivity({
        scenarioId: selectedRow.scenario_id,
        plantId: selectedRow.plant_id,
        variables: selectedVariables,
      });
      setResults(response.results);
      setStatusMessage(`${response.results.length} sensitivity variable${response.results.length === 1 ? "" : "s"} calculated.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Sensitivity run failed.");
    } finally {
      setRunning(false);
    }
  }

  function toggleVariable(variable: SensitivityVariable) {
    setSelectedVariables((current) =>
      current.includes(variable)
        ? current.filter((item) => item !== variable)
        : [...current, variable],
    );
  }

  useEffect(() => {
    void loadRanking();
  }, []);

  useEffect(() => {
    if (!loading) {
      void loadSensitivity(selectedRow);
    }
  }, [loading, selectedRow?.scoring_result_id]);

  return (
    <div className="sensitivity-workspace">
      <section className="page-header">
        <div>
          <h2>Sensitivity Analysis</h2>
          <p>Run tornado-style sensitivity on stored scenario results and compare low/base/high economics.</p>
        </div>
        <div className="inline-actions">
          <button className="button secondary" disabled={loading} type="button" onClick={() => void loadRanking()}>
            <RefreshCw size={16} aria-hidden="true" />
            {loading ? "Refreshing" : "Refresh"}
          </button>
          <button
            className="button"
            disabled={!selectedRow || running || selectedVariables.length === 0}
            type="button"
            onClick={() => void handleRunSensitivity()}
          >
            <PlayCircle size={16} aria-hidden="true" />
            {running ? "Running" : "Run Sensitivity"}
          </button>
        </div>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="sensitivity-controls">
        <label className="field">
          <span>Unit / Scenario</span>
          <select
            disabled={loading || ranking.length === 0}
            value={selectedRow?.scoring_result_id ?? ""}
            onChange={(event) => setSelectedScoringId(event.target.value)}
          >
            {ranking.map((row) => (
              <option key={row.scoring_result_id} value={row.scoring_result_id}>
                #{row.rank} {row.site_name} {row.unit_name} - {row.scenario_name}
              </option>
            ))}
          </select>
        </label>
        <div className="sensitivity-selected">
          <span>Selected case</span>
          <strong>{selectedRow ? `${selectedRow.site_name} ${selectedRow.unit_name}` : "No case selected"}</strong>
          <small>
            {selectedRow
              ? `${selectedRow.recommended_scheme} / ${formatMoney(selectedRow.methanol_tpy, " t/y methanol")}`
              : "Run scoring first"}
          </small>
        </div>
        <div className="sensitivity-variable-picker" aria-label="Sensitivity variables">
          {sensitivityVariables.map((variable) => (
            <label key={variable.id}>
              <input
                checked={selectedVariables.includes(variable.id)}
                type="checkbox"
                onChange={() => toggleVariable(variable.id)}
              />
              {variable.label}
            </label>
          ))}
        </div>
      </section>

      <section className="sensitivity-overview-grid">
        <article className="card">
          <div className="metric-label">Dominant Driver</div>
          <div className="metric-value">
            {dominant ? variableLabel(dominant.variable_name) : loadingResults ? "Loading" : "Not calculated"}
          </div>
        </article>
        <article className="card">
          <div className="metric-label">Impact Score</div>
          <div className="metric-value">{dominant ? formatNumber(dominant.impact_score) : "Not calculated"}</div>
        </article>
        <article className="card">
          <div className="metric-label">Base IRR</div>
          <div className="metric-value">{dominant ? formatPercent(dominant.base_irr) : "Not calculated"}</div>
        </article>
        <article className="card">
          <div className="metric-label">Base LCOM</div>
          <div className="metric-value">
            {dominant ? formatMoney(dominant.base_lcom_usd_per_ton, " USD/t") : "Not calculated"}
          </div>
        </article>
      </section>

      <section className="sensitivity-layout">
        <article className="sensitivity-panel">
          <div className="map-panel-header">
            <div>
              <h3>Tornado Chart</h3>
              <span>{currentResults.length} variable{currentResults.length === 1 ? "" : "s"}</span>
            </div>
            <Activity size={18} aria-hidden="true" />
          </div>
          <div className="tornado-chart">
            {currentResults
              .slice()
              .sort((a, b) => b.impact_score - a.impact_score)
              .map((result) => (
                <div className="tornado-row wide" key={result.id}>
                  <span>{variableLabel(result.variable_name)}</span>
                  <div>
                    <i style={{ width: `${Math.max(4, (result.impact_score / maxImpact) * 100)}%` }} />
                  </div>
                  <strong>{formatNumber(result.impact_score)}</strong>
                </div>
              ))}
            {!loadingResults && currentResults.length === 0 ? <p className="muted">No sensitivity run stored.</p> : null}
          </div>
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
        </article>

        <article className="card">
          <h3>Result Table</h3>
          <div className="table-wrap">
            <table className="data-table sensitivity-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th>Low input</th>
                  <th>Base input</th>
                  <th>High input</th>
                  <th>Low IRR</th>
                  <th>High IRR</th>
                  <th>Low LCOM</th>
                  <th>High LCOM</th>
                </tr>
              </thead>
              <tbody>
                {currentResults
                  .slice()
                  .sort((a, b) => b.impact_score - a.impact_score)
                  .map((result) => (
                    <tr key={result.id}>
                      <td>{variableLabel(result.variable_name)}</td>
                      <td>{formatNumber(result.low_input_value)}</td>
                      <td>{formatNumber(result.base_input_value)}</td>
                      <td>{formatNumber(result.high_input_value)}</td>
                      <td>{formatPercent(result.low_irr)}</td>
                      <td>{formatPercent(result.high_irr)}</td>
                      <td>{formatMoney(result.low_lcom_usd_per_ton, " USD/t")}</td>
                      <td>{formatMoney(result.high_lcom_usd_per_ton, " USD/t")}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </div>
  );
}
