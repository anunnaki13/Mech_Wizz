"use client";

import { PlayCircle, Plus, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { FinancialAssumptionsForm } from "@/components/scenarios/FinancialAssumptionsForm";
import { ScenarioForm } from "@/components/scenarios/ScenarioForm";
import { SimulationResultPanel } from "@/components/scenarios/SimulationResultPanel";
import {
  createScenario,
  deleteScenario,
  getFinancialAssumption,
  getPlantScenarios,
  getPlants,
  getScenarioResults,
  runScenarioSimulation,
  saveFinancialAssumption,
  updateScenario,
} from "@/lib/api";
import type { FinancialAssumption, FinancialAssumptionPayload } from "@/types/financial-assumption";
import type { Plant } from "@/types/plant";
import type { BusinessScenario, BusinessScenarioPayload, BusinessScheme } from "@/types/scenario";
import type { ScenarioResult } from "@/types/scenario-result";

const schemeLabels: Record<BusinessScheme, string> = {
  access: "WIZ Access",
  align: "WIZ Align",
  augment: "WIZ Augment",
};

function formatPercent(value: number | null) {
  if (value === null) {
    return "Unknown";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}%`;
}

function formatRatio(value: number | null) {
  if (value === null) {
    return "Unknown";
  }
  return `${(value * 100).toLocaleString("en-US", { maximumFractionDigits: 1 })}%`;
}

export function ScenarioWorkspace() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [selectedPlantId, setSelectedPlantId] = useState<string>("");
  const [scenarios, setScenarios] = useState<BusinessScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("");
  const [financialAssumption, setFinancialAssumption] = useState<FinancialAssumption | null>(null);
  const [scenarioResults, setScenarioResults] = useState<ScenarioResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningSimulation, setRunningSimulation] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const selectedPlant = useMemo(
    () => plants.find((plant) => plant.id === selectedPlantId) ?? null,
    [plants, selectedPlantId],
  );
  const selectedScenario = useMemo(
    () => scenarios.find((scenario) => scenario.id === selectedScenarioId) ?? null,
    [scenarios, selectedScenarioId],
  );
  const latestResult = scenarioResults[0] ?? null;

  async function loadPlants() {
    setLoading(true);
    setErrorMessage(null);
    try {
      const records = await getPlants();
      setPlants(records);
      setSelectedPlantId((current) => current || records[0]?.id || "");
    } catch {
      setErrorMessage("Backend data is not reachable.");
    } finally {
      setLoading(false);
    }
  }

  async function loadScenarios(plantId: string, preferredScenarioId?: string) {
    if (!plantId) {
      setScenarios([]);
      setSelectedScenarioId("");
      return;
    }
    setErrorMessage(null);
    try {
      const records = await getPlantScenarios(plantId);
      setScenarios(records);
      const nextSelected = preferredScenarioId && records.some((item) => item.id === preferredScenarioId)
        ? preferredScenarioId
        : records[0]?.id || "";
      setSelectedScenarioId(nextSelected);
    } catch {
      setErrorMessage("Scenarios could not be loaded.");
      setScenarios([]);
      setSelectedScenarioId("");
    }
  }

  async function loadFinancialAssumption(scenarioId: string) {
    if (!scenarioId) {
      setFinancialAssumption(null);
      return;
    }
    setErrorMessage(null);
    try {
      setFinancialAssumption(await getFinancialAssumption(scenarioId));
    } catch {
      setErrorMessage("Financial assumptions could not be loaded.");
      setFinancialAssumption(null);
    }
  }

  async function loadScenarioResults(scenarioId: string) {
    if (!scenarioId) {
      setScenarioResults([]);
      return;
    }
    setErrorMessage(null);
    try {
      setScenarioResults(await getScenarioResults(scenarioId));
    } catch {
      setErrorMessage("Scenario results could not be loaded.");
      setScenarioResults([]);
    }
  }

  useEffect(() => {
    void loadPlants();
  }, []);

  useEffect(() => {
    void loadScenarios(selectedPlantId, selectedScenarioId);
  }, [selectedPlantId]);

  useEffect(() => {
    void loadFinancialAssumption(selectedScenarioId);
    void loadScenarioResults(selectedScenarioId);
  }, [selectedScenarioId]);

  async function handleCreateScenario(payload: BusinessScenarioPayload) {
    if (!selectedPlantId) {
      return;
    }
    const scenario = await createScenario(selectedPlantId, payload);
    setStatusMessage("Scenario saved.");
    await loadScenarios(selectedPlantId, scenario.id);
  }

  async function handleUpdateScenario(payload: BusinessScenarioPayload) {
    if (!selectedScenario) {
      return;
    }
    const scenario = await updateScenario(selectedScenario.id, payload);
    setScenarios((current) => current.map((item) => (item.id === scenario.id ? scenario : item)));
    setSelectedScenarioId(scenario.id);
    setStatusMessage("Scenario updated.");
  }

  async function handleDeleteScenario() {
    if (!selectedScenario || !selectedPlantId) {
      return;
    }
    await deleteScenario(selectedScenario.id);
    setStatusMessage("Scenario deleted.");
    setScenarioResults([]);
    await loadScenarios(selectedPlantId);
  }

  async function handleSaveFinancialAssumption(payload: FinancialAssumptionPayload) {
    if (!selectedScenario) {
      return;
    }
    const record = await saveFinancialAssumption(selectedScenario.id, payload);
    setFinancialAssumption(record);
    setStatusMessage("Financial assumptions saved.");
  }

  async function handleRunSimulation() {
    if (!selectedScenario) {
      return;
    }
    setRunningSimulation(true);
    setErrorMessage(null);
    try {
      const result = await runScenarioSimulation(selectedScenario.id);
      setScenarioResults((current) => [result, ...current]);
      setStatusMessage("Simulation result saved.");
    } catch {
      setErrorMessage("Simulation failed. Check scenario inputs and financial assumptions.");
    } finally {
      setRunningSimulation(false);
    }
  }

  return (
    <div className="section-stack">
      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="grid two">
        <div className="card">
          <div className="scenario-toolbar">
            <div>
              <h3>Plant Scenarios</h3>
              <p className="muted">WIZ Access, WIZ Align, and WIZ Augment assumptions by unit.</p>
            </div>
            <button className="button secondary" type="button" onClick={() => void loadPlants()}>
              <RefreshCw size={16} aria-hidden="true" />
              Refresh
            </button>
          </div>

          <label className="field">
            <span>Plant</span>
            <select
              disabled={loading || plants.length === 0}
              value={selectedPlantId}
              onChange={(event) => setSelectedPlantId(event.target.value)}
            >
              {plants.map((plant) => (
                <option key={plant.id} value={plant.id}>
                  {plant.plant_name} {plant.unit_name}
                </option>
              ))}
            </select>
          </label>

          {selectedPlant ? (
            <div className="detail-list scenario-plant-summary">
              <div className="detail-row">
                <span>Location</span>
                <span>{[selectedPlant.city, selectedPlant.province].filter(Boolean).join(", ") || "Unknown"}</span>
              </div>
              <div className="detail-row">
                <span>Capacity</span>
                <span>{selectedPlant.capacity_mw?.toLocaleString("en-US") ?? "Unknown"} MW</span>
              </div>
              <div className="detail-row">
                <span>Operating days</span>
                <span>{selectedPlant.operating_days_per_year ?? "Unknown"}</span>
              </div>
            </div>
          ) : null}

          <div className="scenario-list">
            {scenarios.map((scenario) => (
              <button
                className={`scenario-row ${scenario.id === selectedScenarioId ? "active" : ""}`}
                key={scenario.id}
                type="button"
                onClick={() => setSelectedScenarioId(scenario.id)}
              >
                <span>
                  <strong>{scenario.scenario_name}</strong>
                  <small>{schemeLabels[scenario.scheme]}</small>
                </span>
                <span>
                  <small>Capture</small>
                  <strong>{formatRatio(scenario.capture_rate)}</strong>
                </span>
                <span>
                  <small>PLN ownership</small>
                  <strong>{formatPercent(scenario.pln_ownership_percent)}</strong>
                </span>
                <span className="chip">{scenario.confidence_level}</span>
              </button>
            ))}
            {!loading && selectedPlantId && scenarios.length === 0 ? (
              <div className="notice">No scenarios for the selected plant.</div>
            ) : null}
          </div>
        </div>

        <div className="card">
          <div className="scenario-toolbar">
            <div>
              <h3>Create Scenario</h3>
              <p className="muted">New scenario records attach to the selected plant.</p>
            </div>
            <Plus size={20} aria-hidden="true" />
          </div>
          <ScenarioForm mode="create" disabled={!selectedPlantId} onSubmit={handleCreateScenario} />
        </div>
      </section>

      <section className="card">
        <div className="scenario-toolbar">
          <div>
            <h3>{selectedScenario ? selectedScenario.scenario_name : "Selected Scenario"}</h3>
            <p className="muted">
              {selectedScenario ? schemeLabels[selectedScenario.scheme] : "Select a scenario to edit business terms."}
            </p>
          </div>
          <button
            className="button secondary"
            disabled={!selectedScenario || runningSimulation}
            type="button"
            onClick={() => void handleRunSimulation()}
          >
            <PlayCircle size={16} aria-hidden="true" />
            {runningSimulation ? "Running" : "Run Simulation"}
          </button>
        </div>
        <ScenarioForm
          mode="edit"
          disabled={!selectedScenario}
          scenario={selectedScenario}
          onDelete={handleDeleteScenario}
          onSubmit={handleUpdateScenario}
        />
      </section>

      <section className="card">
        <div className="scenario-toolbar">
          <div>
            <h3>Latest Scenario Result</h3>
            <p className="muted">
              {latestResult ? "Stored backend calculation result" : "Run a simulation to persist scenario outputs."}
            </p>
          </div>
          {latestResult ? <span className="chip">{latestResult.confidence_level}</span> : null}
        </div>
        <SimulationResultPanel result={latestResult} />
      </section>

      <section className="card">
        <div className="scenario-toolbar">
          <div>
            <h3>Financial Assumptions</h3>
            <p className="muted">
              {financialAssumption ? "Stored assumption record" : "No stored assumption record for this scenario yet."}
            </p>
          </div>
          {financialAssumption ? <span className="chip">{financialAssumption.data_status}</span> : null}
        </div>
        <FinancialAssumptionsForm
          assumption={financialAssumption}
          disabled={!selectedScenario}
          onSave={handleSaveFinancialAssumption}
        />
      </section>
    </div>
  );
}
