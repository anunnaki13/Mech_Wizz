"use client";

import { RefreshCw, RotateCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { MapFilters } from "@/components/dashboard/MapFilters";
import { OpportunityMap } from "@/components/dashboard/OpportunityMap";
import { RankingTable } from "@/components/dashboard/RankingTable";
import { ScoreBreakdownPanel } from "@/components/dashboard/ScoreBreakdownPanel";
import { SensitivityPanel } from "@/components/dashboard/SensitivityPanel";
import {
  getPlantScenarios,
  getPlants,
  getUnitOpportunityGeoJSON,
  getUnitProfile,
  getUnitRanking,
  recalculateScoring,
} from "@/lib/api";
import type { Plant } from "@/types/plant";
import type { BusinessScenario } from "@/types/scenario";
import type { DashboardFilters, UnitOpportunityGeoJSON, UnitProfile, UnitRankingRow } from "@/types/scoring";

type ScenarioOption = BusinessScenario & {
  plant_name: string;
  unit_name: string;
};

const emptyGeoJSON: UnitOpportunityGeoJSON = {
  type: "FeatureCollection",
  features: [],
};

const initialFilters: DashboardFilters = {
  scenarioId: "",
  scheme: "all",
  region: "all",
  fuelType: "all",
  confidence: "all",
  opportunityLevel: "all",
  showHeatmap: true,
  showMarkers: true,
  showLabels: true,
};

function formatCompact(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1, notation: "compact" })}${suffix}`;
}

function formatScore(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 });
}

function uniqueOptions(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value)))).sort();
}

export function MapDashboard() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioOption[]>([]);
  const [filters, setFilters] = useState<DashboardFilters>(initialFilters);
  const [ranking, setRanking] = useState<UnitRankingRow[]>([]);
  const [geojson, setGeojson] = useState<UnitOpportunityGeoJSON>(emptyGeoJSON);
  const [selectedPlantId, setSelectedPlantId] = useState("");
  const [selectedProfile, setSelectedProfile] = useState<UnitProfile | null>(null);
  const [loadingReference, setLoadingReference] = useState(true);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [recalculating, setRecalculating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const selectedRow = useMemo(
    () => ranking.find((row) => row.plant_id === selectedPlantId) ?? ranking[0] ?? null,
    [ranking, selectedPlantId],
  );

  const kpis = useMemo(() => {
    const totalCo2 = ranking.reduce((sum, row) => sum + (row.co2_tpy ?? 0), 0);
    const totalMethanol = ranking.reduce((sum, row) => sum + (row.methanol_tpy ?? 0), 0);
    const highestOpportunity = ranking.reduce((max, row) => Math.max(max, row.opportunity_score), 0);
    const averageConfidence = ranking.length
      ? ranking.reduce((sum, row) => sum + row.confidence_score, 0) / ranking.length
      : 0;
    return {
      bestCandidate: ranking[0] ? `${ranking[0].site_name} ${ranking[0].unit_name}` : "No ranked unit",
      totalCo2,
      totalMethanol,
      highestOpportunity,
      averageConfidence,
      recommendedScheme: ranking[0]?.recommended_scheme ?? "Not calculated",
    };
  }, [ranking]);

  const scenarioOptions = useMemo(
    () =>
      scenarios.map((scenario) => ({
        id: scenario.id,
        label: `${scenario.scenario_name} - ${scenario.plant_name} ${scenario.unit_name}`,
      })),
    [scenarios],
  );
  const regionOptions = useMemo(() => uniqueOptions(plants.map((plant) => plant.province)), [plants]);
  const fuelOptions = useMemo(() => uniqueOptions(plants.map((plant) => plant.fuel_type)), [plants]);

  async function loadProfile(plantId: string, scenarioId: string) {
    if (!plantId) {
      setSelectedProfile(null);
      return;
    }
    try {
      setSelectedProfile(await getUnitProfile(plantId, scenarioId || undefined));
    } catch {
      setSelectedProfile(null);
    }
  }

  async function loadDashboard(nextFilters: DashboardFilters, preferredPlantId?: string) {
    setLoadingDashboard(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const params = {
        scenarioId: nextFilters.scenarioId || undefined,
        scheme: nextFilters.scheme,
        region: nextFilters.region,
        fuelType: nextFilters.fuelType,
        confidence: nextFilters.confidence,
        opportunityLevel: nextFilters.opportunityLevel,
      };
      const [rankingData, geojsonData] = await Promise.all([
        getUnitRanking(params),
        getUnitOpportunityGeoJSON(params),
      ]);
      setRanking(rankingData);
      setGeojson(geojsonData);

      const targetPlantId =
        preferredPlantId && rankingData.some((row) => row.plant_id === preferredPlantId)
          ? preferredPlantId
          : selectedPlantId && rankingData.some((row) => row.plant_id === selectedPlantId)
            ? selectedPlantId
            : rankingData[0]?.plant_id || "";
      setSelectedPlantId(targetPlantId);
      await loadProfile(targetPlantId, nextFilters.scenarioId);
      if (rankingData.length === 0) {
        setStatusMessage("No ranking records for the selected filters.");
      }
    } catch {
      setErrorMessage("Map ranking data is not reachable.");
      setRanking([]);
      setGeojson(emptyGeoJSON);
      setSelectedProfile(null);
    } finally {
      setLoadingDashboard(false);
    }
  }

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
      setFilters((current) => ({
        ...current,
        scenarioId: current.scenarioId || scenarioRecords[0]?.id || "",
      }));
      if (scenarioRecords.length === 0) {
        setStatusMessage("No scenarios are available.");
      }
    } catch {
      setErrorMessage("Backend data is not reachable.");
    } finally {
      setLoadingReference(false);
    }
  }

  useEffect(() => {
    void loadReferenceData();
  }, []);

  useEffect(() => {
    if (!loadingReference) {
      void loadDashboard(filters);
    }
  }, [
    filters.scenarioId,
    filters.scheme,
    filters.region,
    filters.fuelType,
    filters.confidence,
    filters.opportunityLevel,
    loadingReference,
  ]);

  async function handleSelectUnit(plantId: string) {
    setSelectedPlantId(plantId);
    await loadProfile(plantId, filters.scenarioId);
  }

  async function handleRefresh() {
    await loadReferenceData();
    await loadDashboard(filters, selectedPlantId);
  }

  async function handleRecalculate() {
    setRecalculating(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const response = await recalculateScoring({
        scenarioId: filters.scenarioId || undefined,
        scheme: filters.scheme,
      });
      setStatusMessage(`${response.created_count} scoring record${response.created_count === 1 ? "" : "s"} created.`);
      await loadDashboard(filters, selectedPlantId);
    } catch {
      setErrorMessage("Score recalculation failed. Run a scenario simulation first.");
    } finally {
      setRecalculating(false);
    }
  }

  return (
    <div className="map-dashboard">
      <section className="page-header">
        <div>
          <h2>Map & Heatmap Intelligence</h2>
          <p>PLN NP pilot screening - deterministic Phase 3 scoring.</p>
        </div>
        <div className="inline-actions">
          <button className="button secondary" type="button" onClick={() => void handleRefresh()}>
            <RefreshCw size={16} aria-hidden="true" />
            Refresh
          </button>
          <button
            className="button"
            type="button"
            disabled={recalculating || !filters.scenarioId}
            onClick={() => void handleRecalculate()}
          >
            <RotateCw size={16} aria-hidden="true" />
            {recalculating ? "Recalculating" : "Recalculate Scores"}
          </button>
        </div>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="map-kpi-grid" aria-label="Map dashboard KPIs">
        <div className="card">
          <div className="metric-label">Best Candidate Site</div>
          <div className="metric-value">{kpis.bestCandidate}</div>
        </div>
        <div className="card">
          <div className="metric-label">Total CO2 Available</div>
          <div className="metric-value">{formatCompact(kpis.totalCo2, " t/y")}</div>
        </div>
        <div className="card">
          <div className="metric-label">Total E-Methanol Potential</div>
          <div className="metric-value">{formatCompact(kpis.totalMethanol, " t/y")}</div>
        </div>
        <div className="card">
          <div className="metric-label">Highest Opportunity Score</div>
          <div className="metric-value">{formatScore(kpis.highestOpportunity)}</div>
        </div>
        <div className="card">
          <div className="metric-label">Average Confidence Score</div>
          <div className="metric-value">{formatScore(kpis.averageConfidence)}</div>
        </div>
        <div className="card">
          <div className="metric-label">Recommended Business Scheme</div>
          <div className="metric-value">{kpis.recommendedScheme}</div>
        </div>
      </section>

      <MapFilters
        filters={filters}
        fuelOptions={fuelOptions}
        loading={loadingReference || loadingDashboard}
        regionOptions={regionOptions}
        scenarioOptions={scenarioOptions}
        onChange={setFilters}
      />

      <section className="map-workspace">
        <div className="map-main-stack">
          <OpportunityMap
            geojson={geojson}
            loading={loadingDashboard}
            selectedPlantId={selectedRow?.plant_id ?? ""}
            showHeatmap={filters.showHeatmap}
            showLabels={filters.showLabels}
            showMarkers={filters.showMarkers}
            onSelectUnit={(plantId) => void handleSelectUnit(plantId)}
          />
          <RankingTable
            loading={loadingDashboard}
            ranking={ranking}
            selectedPlantId={selectedRow?.plant_id ?? ""}
            onSelectUnit={(plantId) => void handleSelectUnit(plantId)}
          />
        </div>
        <div className="map-side-stack">
          <ScoreBreakdownPanel loading={loadingDashboard} profile={selectedProfile} row={selectedRow} />
          <SensitivityPanel row={selectedRow} scenarioId={filters.scenarioId} />
        </div>
      </section>
    </div>
  );
}
