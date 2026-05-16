"use client";

import { RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getInvestorCase, getPlantScenarios, getPlants } from "@/lib/api";
import type { InvestorCase } from "@/types/investor";
import type { Plant } from "@/types/plant";
import type { BusinessScenario } from "@/types/scenario";

type ScenarioOption = BusinessScenario & {
  plant_name: string;
  unit_name: string;
};

function formatNumber(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1, notation: "compact" })}${suffix}`;
}

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return `${(value * 100).toLocaleString("en-US", { maximumFractionDigits: 1 })}%`;
}

function stringValue(value: unknown) {
  return typeof value === "string" && value ? value : "";
}

export function InvestorDashboard() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioOption[]>([]);
  const [selectedPlantId, setSelectedPlantId] = useState("");
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [investorCase, setInvestorCase] = useState<InvestorCase | null>(null);
  const [loadingReference, setLoadingReference] = useState(true);
  const [loadingCase, setLoadingCase] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const scenarioOptions = useMemo(
    () => scenarios.filter((scenario) => !selectedPlantId || scenario.plant_id === selectedPlantId),
    [scenarios, selectedPlantId],
  );

  async function loadReferenceData() {
    setLoadingReference(true);
    setErrorMessage(null);
    try {
      const plantRecords = await getPlants();
      const scenarioRecords = (
        await Promise.all(
          plantRecords.map(async (plant) => {
            const plantScenarios = await getPlantScenarios(plant.id);
            return plantScenarios.map((scenario) => ({
              ...scenario,
              plant_name: plant.plant_name,
              unit_name: plant.unit_name,
            }));
          }),
        )
      ).flat();
      setPlants(plantRecords);
      setScenarios(scenarioRecords);
      setSelectedPlantId((current) => current || plantRecords[0]?.id || "");
      setSelectedScenarioId((current) => current || scenarioRecords[0]?.id || "");
    } catch {
      setErrorMessage("Backend investor data is not reachable.");
    } finally {
      setLoadingReference(false);
    }
  }

  async function loadInvestorCase(plantId = selectedPlantId, scenarioId = selectedScenarioId) {
    if (!plantId && !scenarioId) {
      setInvestorCase(null);
      return;
    }
    setLoadingCase(true);
    setErrorMessage(null);
    try {
      const payload = await getInvestorCase({
        plantId: plantId || undefined,
        scenarioId: scenarioId || undefined,
      });
      setInvestorCase(payload);
      setSelectedPlantId(stringValue(payload.plant.id));
      setSelectedScenarioId(stringValue(payload.scenario.id));
    } catch {
      setErrorMessage("Investor case could not be loaded.");
      setInvestorCase(null);
    } finally {
      setLoadingCase(false);
    }
  }

  useEffect(() => {
    void loadReferenceData();
  }, []);

  useEffect(() => {
    if (!loadingReference && (selectedPlantId || selectedScenarioId)) {
      void loadInvestorCase(selectedPlantId, selectedScenarioId);
    }
  }, [selectedPlantId, selectedScenarioId, loadingReference]);

  return (
    <div className="investor-dashboard">
      <section className="page-header">
        <div>
          <h2>Investor Case</h2>
          <p>Indicative case assembled from stored simulation, scoring, sensitivity, and data quality records.</p>
        </div>
        <div className="inline-actions">
          <button className="button secondary" type="button" onClick={() => void loadInvestorCase()}>
            <RefreshCw size={16} aria-hidden="true" />
            {loadingCase ? "Refreshing" : "Refresh"}
          </button>
        </div>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {investorCase?.warnings?.length ? <div className="notice">{investorCase.warnings[0]}</div> : null}

      <section className="investor-controls">
        <label className="field">
          <span>Plant</span>
          <select
            disabled={loadingReference || plants.length === 0}
            value={selectedPlantId}
            onChange={(event) => {
              const plantId = event.target.value;
              setSelectedPlantId(plantId);
              setSelectedScenarioId(scenarios.find((scenario) => scenario.plant_id === plantId)?.id || "");
            }}
          >
            {plants.map((plant) => (
              <option key={plant.id} value={plant.id}>
                {plant.plant_name} {plant.unit_name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Scenario</span>
          <select
            disabled={loadingReference || scenarioOptions.length === 0}
            value={selectedScenarioId}
            onChange={(event) => setSelectedScenarioId(event.target.value)}
          >
            {scenarioOptions.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.scenario_name}
              </option>
            ))}
          </select>
        </label>
        <div className="investor-selected">
          <span>Selected pilot site</span>
          <strong>
            {investorCase
              ? `${String(investorCase.plant.plant_name ?? "Unknown")} ${String(investorCase.plant.unit_name ?? "")}`
              : "Not loaded"}
          </strong>
        </div>
      </section>

      <section className="map-kpi-grid investor-kpis" aria-label="Investor KPIs">
        <div className="card">
          <div className="metric-label">Project IRR</div>
          <div className="metric-value">{formatPercent(investorCase?.kpis.project_irr)}</div>
        </div>
        <div className="card">
          <div className="metric-label">Estimated NPV</div>
          <div className="metric-value">{formatNumber(investorCase?.kpis.estimated_npv_usd, " USD")}</div>
        </div>
        <div className="card">
          <div className="metric-label">LCOM</div>
          <div className="metric-value">{formatNumber(investorCase?.kpis.lcom_usd_per_ton, " USD/t")}</div>
        </div>
        <div className="card">
          <div className="metric-label">Payback Period</div>
          <div className="metric-value">{formatNumber(investorCase?.kpis.payback_years, " years")}</div>
        </div>
        <div className="card">
          <div className="metric-label">E-Methanol Capacity</div>
          <div className="metric-value">{formatNumber(investorCase?.kpis.e_methanol_capacity_tpy, " t/y")}</div>
        </div>
        <div className="card">
          <div className="metric-label">CO2 Abatement</div>
          <div className="metric-value">{formatNumber(investorCase?.kpis.co2_abatement_tpy, " t/y")}</div>
        </div>
      </section>

      <section className="investor-grid">
        <div className="card investor-panel">
          <h3>Investment thesis</h3>
          <div className="thesis-flow">
            {(investorCase?.thesis_flow ?? []).map((item) => (
              <div key={item.stage}>
                <span>{item.stage}</span>
                <p>{item.summary}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card investor-panel">
          <h3>Revenue Mix</h3>
          <div className="detail-list">
            {(investorCase?.revenue_mix ?? []).map((segment) => (
              <div className="detail-row" key={segment.label}>
                <span>{segment.label}</span>
                <span>{formatNumber(segment.value_usd_per_year, " USD/y")}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card investor-panel wide">
          <h3>Scenario Comparison</h3>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Scheme</th>
                  <th>Scenario</th>
                  <th>IRR</th>
                  <th>NPV</th>
                  <th>LCOM</th>
                  <th>Payback</th>
                  <th>Composite</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {(investorCase?.scenario_comparison ?? []).map((row) => (
                  <tr key={row.scheme}>
                    <td>{row.scheme}</td>
                    <td>{row.scenario_name ?? "Missing"}</td>
                    <td>{formatPercent(row.irr)}</td>
                    <td>{formatNumber(row.npv_usd, " USD")}</td>
                    <td>{formatNumber(row.lcom_usd_per_ton, " USD/t")}</td>
                    <td>{formatNumber(row.payback_years, " years")}</td>
                    <td>{row.composite_score?.toLocaleString("en-US", { maximumFractionDigits: 2 }) ?? "Not calculated"}</td>
                    <td>{row.confidence_level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card investor-panel">
          <h3>Risk & Mitigation</h3>
          <div className="risk-list">
            {(investorCase?.risks ?? []).map((risk) => (
              <div key={`${risk.source}-${risk.risk}`} className="risk-row">
                <strong>{risk.risk}</strong>
                <span>{risk.impact} impact / {risk.priority}</span>
                <p>{risk.mitigation}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card investor-panel">
          <h3>Roadmap to Scale</h3>
          <div className="roadmap-list">
            {(investorCase?.roadmap ?? []).map((item) => (
              <div key={item.step}>
                <span>{item.step}</span>
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card investor-panel">
          <h3>Why This Project Wins</h3>
          <ul className="win-list">
            {(investorCase?.why_this_wins ?? []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="card investor-panel">
          <h3>CAPEX Structure</h3>
          <div className="detail-list">
            <div className="detail-row">
              <span>Total CAPEX</span>
              <span>{formatNumber(investorCase?.capex_structure.total_capex_usd, " USD")}</span>
            </div>
            <div className="detail-row">
              <span>PLN responsibility</span>
              <span>{investorCase?.capex_structure.pln_responsibility_percent ?? "Unknown"}%</span>
            </div>
            <div className="detail-row">
              <span>Partner responsibility</span>
              <span>{investorCase?.capex_structure.partner_responsibility_percent ?? "Unknown"}%</span>
            </div>
          </div>
        </div>

        <div className="card investor-panel wide">
          <h3>Data Quality & Gaps</h3>
          <div className="confidence-strip">
            <span className="chip">Investor confidence: {investorCase?.confidence_level ?? "unknown"}</span>
            <span className="chip">
              Dominant sensitivity: {investorCase?.sensitivity?.dominant_driver ?? "Not calculated"}
            </span>
          </div>
          <div className="data-gap-list" style={{ marginTop: 12 }}>
            {(investorCase?.data_gaps ?? []).map((gap) => (
              <div className="data-gap-row" key={`${gap.module}-${gap.name}`}>
                <strong>{gap.missing_data}</strong>
                <span>{gap.impact} impact / {gap.priority} / {gap.recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
