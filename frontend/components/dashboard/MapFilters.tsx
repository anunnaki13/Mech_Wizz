"use client";

import { Layers } from "lucide-react";

import type { DashboardFilters } from "@/types/scoring";

type Option = {
  id: string;
  label: string;
};

type MapFiltersProps = {
  filters: DashboardFilters;
  scenarioOptions: Option[];
  regionOptions: string[];
  fuelOptions: string[];
  loading: boolean;
  onChange: (filters: DashboardFilters) => void;
};

function updateFilter(filters: DashboardFilters, changes: Partial<DashboardFilters>) {
  return { ...filters, ...changes };
}

export function MapFilters({
  filters,
  fuelOptions,
  loading,
  regionOptions,
  scenarioOptions,
  onChange,
}: MapFiltersProps) {
  return (
    <section className="map-filterbar" aria-label="Map filters">
      <label className="field">
        <span>Scenario</span>
        <select
          disabled={loading || scenarioOptions.length === 0}
          value={filters.scenarioId}
          onChange={(event) => onChange(updateFilter(filters, { scenarioId: event.target.value }))}
        >
          <option value="">All scenarios</option>
          {scenarioOptions.map((scenario) => (
            <option key={scenario.id} value={scenario.id}>
              {scenario.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Scheme</span>
        <select
          disabled={loading}
          value={filters.scheme}
          onChange={(event) => onChange(updateFilter(filters, { scheme: event.target.value }))}
        >
          <option value="all">Compare All</option>
          <option value="access">WIZ Access</option>
          <option value="align">WIZ Align</option>
          <option value="augment">WIZ Augment</option>
        </select>
      </label>

      <label className="field">
        <span>Region</span>
        <select
          disabled={loading}
          value={filters.region}
          onChange={(event) => onChange(updateFilter(filters, { region: event.target.value }))}
        >
          <option value="all">All</option>
          {regionOptions.map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Fuel Type</span>
        <select
          disabled={loading}
          value={filters.fuelType}
          onChange={(event) => onChange(updateFilter(filters, { fuelType: event.target.value }))}
        >
          <option value="all">All</option>
          {fuelOptions.map((fuelType) => (
            <option key={fuelType} value={fuelType}>
              {fuelType}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Data Confidence</span>
        <select
          disabled={loading}
          value={filters.confidence}
          onChange={(event) => onChange(updateFilter(filters, { confidence: event.target.value }))}
        >
          <option value="all">All</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="unknown">Unknown</option>
        </select>
      </label>

      <label className="field">
        <span>Opportunity Level</span>
        <select
          disabled={loading}
          value={filters.opportunityLevel}
          onChange={(event) => onChange(updateFilter(filters, { opportunityLevel: event.target.value }))}
        >
          <option value="all">All</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="priority">Priority</option>
        </select>
      </label>

      <div className="map-layer-toggles" aria-label="Visible layers">
        <span>
          <Layers size={15} aria-hidden="true" />
          Layers
        </span>
        <label>
          <input
            checked={filters.showHeatmap}
            type="checkbox"
            onChange={(event) => onChange(updateFilter(filters, { showHeatmap: event.target.checked }))}
          />
          Heatmap
        </label>
        <label>
          <input
            checked={filters.showMarkers}
            type="checkbox"
            onChange={(event) => onChange(updateFilter(filters, { showMarkers: event.target.checked }))}
          />
          Marker
        </label>
        <label>
          <input
            checked={filters.showLabels}
            type="checkbox"
            onChange={(event) => onChange(updateFilter(filters, { showLabels: event.target.checked }))}
          />
          Label
        </label>
        <label>
          <input
            checked={filters.showEconomicZones}
            type="checkbox"
            onChange={(event) => onChange(updateFilter(filters, { showEconomicZones: event.target.checked }))}
          />
          Economic Area
        </label>
        <label>
          <input
            checked={filters.showPorts}
            type="checkbox"
            onChange={(event) => onChange(updateFilter(filters, { showPorts: event.target.checked }))}
          />
          Ports
        </label>
        <label>
          <input
            checked={filters.showExportCorridors}
            type="checkbox"
            onChange={(event) => onChange(updateFilter(filters, { showExportCorridors: event.target.checked }))}
          />
          SG Route
        </label>
      </div>
    </section>
  );
}
