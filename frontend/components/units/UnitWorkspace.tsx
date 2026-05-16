"use client";

import { Plus, Save, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { UnitList } from "@/components/units/UnitList";
import { createPlant } from "@/lib/api";
import type { ConfidenceLevel, DataStatus, Plant, PlantPayload } from "@/types/plant";

type UnitWorkspaceProps = {
  initialPlants: Plant[];
  initialLoadError: boolean;
};

type UnitDraft = {
  plant_name: string;
  unit_name: string;
  province: string;
  city: string;
  latitude: string;
  longitude: string;
  capacity_mw: string;
  fuel_type: string;
  status: string;
  capacity_factor: string;
  operating_days_per_year: string;
  owner: string;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
};

const emptyDraft: UnitDraft = {
  plant_name: "",
  unit_name: "",
  province: "",
  city: "",
  latitude: "",
  longitude: "",
  capacity_mw: "",
  fuel_type: "",
  status: "",
  capacity_factor: "",
  operating_days_per_year: "",
  owner: "",
  data_status: "unknown",
  confidence_level: "unknown",
};

function blankToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function parseOptionalNumber(value: string): number | null {
  const trimmed = value.trim();
  return trimmed === "" ? null : Number(trimmed);
}

function parseOptionalInteger(value: string): number | null {
  const parsed = parseOptionalNumber(value);
  return parsed === null ? null : Math.trunc(parsed);
}

function sortPlants(records: Plant[]): Plant[] {
  return [...records].sort((left, right) =>
    `${left.plant_name} ${left.unit_name}`.localeCompare(`${right.plant_name} ${right.unit_name}`),
  );
}

function buildPayload(draft: UnitDraft): PlantPayload {
  return {
    plant_name: draft.plant_name.trim(),
    unit_name: draft.unit_name.trim(),
    province: blankToNull(draft.province),
    city: blankToNull(draft.city),
    latitude: parseOptionalNumber(draft.latitude),
    longitude: parseOptionalNumber(draft.longitude),
    capacity_mw: parseOptionalNumber(draft.capacity_mw),
    fuel_type: blankToNull(draft.fuel_type),
    status: blankToNull(draft.status),
    capacity_factor: parseOptionalNumber(draft.capacity_factor),
    operating_days_per_year: parseOptionalInteger(draft.operating_days_per_year),
    owner: blankToNull(draft.owner),
    data_status: draft.data_status,
    confidence_level: draft.confidence_level,
  };
}

export function UnitWorkspace({ initialPlants, initialLoadError }: UnitWorkspaceProps) {
  const router = useRouter();
  const [plants, setPlants] = useState(initialPlants);
  const [formOpen, setFormOpen] = useState(false);
  const [draft, setDraft] = useState<UnitDraft>(emptyDraft);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(
    initialLoadError ? "Backend data is not reachable." : null,
  );

  function updateDraft<K extends keyof UnitDraft>(key: K, value: UnitDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatusMessage(null);
    setErrorMessage(null);

    if (!draft.plant_name.trim() || !draft.unit_name.trim()) {
      setErrorMessage("Plant name and unit name are required.");
      return;
    }

    setBusy(true);
    try {
      const created = await createPlant(buildPayload(draft));
      setPlants((current) => sortPlants([...current, created]));
      setDraft(emptyDraft);
      setFormOpen(false);
      setStatusMessage("Unit created.");
      router.push(`/units/${created.id}`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unit could not be created.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="section-stack">
      <section className="page-header">
        <div>
          <h2>Units</h2>
          <p>Candidate power generation units with Phase 1 data quality markers.</p>
        </div>
        <button className="button" type="button" onClick={() => setFormOpen((value) => !value)}>
          {formOpen ? <X size={16} aria-hidden="true" /> : <Plus size={16} aria-hidden="true" />}
          {formOpen ? "Cancel" : "New Unit"}
        </button>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      {formOpen ? (
        <section className="card">
          <div className="setting-card-header">
            <div>
              <h3>New Unit</h3>
              <p className="muted">Create the plant and unit record before adding stack, site, or hydrogen inputs.</p>
            </div>
          </div>
          <form className="unit-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Plant Name</span>
              <input
                required
                value={draft.plant_name}
                onChange={(event) => updateDraft("plant_name", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Unit Name</span>
              <input
                required
                value={draft.unit_name}
                onChange={(event) => updateDraft("unit_name", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Province</span>
              <input value={draft.province} onChange={(event) => updateDraft("province", event.target.value)} />
            </label>
            <label className="field">
              <span>City</span>
              <input value={draft.city} onChange={(event) => updateDraft("city", event.target.value)} />
            </label>
            <label className="field">
              <span>Latitude</span>
              <input
                type="number"
                value={draft.latitude}
                max="90"
                min="-90"
                step="any"
                onChange={(event) => updateDraft("latitude", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Longitude</span>
              <input
                type="number"
                value={draft.longitude}
                max="180"
                min="-180"
                step="any"
                onChange={(event) => updateDraft("longitude", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Capacity MW</span>
              <input
                type="number"
                min="0"
                step="any"
                value={draft.capacity_mw}
                onChange={(event) => updateDraft("capacity_mw", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Fuel Type</span>
              <input value={draft.fuel_type} onChange={(event) => updateDraft("fuel_type", event.target.value)} />
            </label>
            <label className="field">
              <span>Status</span>
              <input value={draft.status} onChange={(event) => updateDraft("status", event.target.value)} />
            </label>
            <label className="field">
              <span>Capacity Factor (0-1)</span>
              <input
                type="number"
                max="1"
                min="0"
                step="0.01"
                value={draft.capacity_factor}
                onChange={(event) => updateDraft("capacity_factor", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Operating Days / Year</span>
              <input
                type="number"
                max="366"
                min="0"
                step="1"
                value={draft.operating_days_per_year}
                onChange={(event) => updateDraft("operating_days_per_year", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Owner</span>
              <input value={draft.owner} onChange={(event) => updateDraft("owner", event.target.value)} />
            </label>
            <label className="field">
              <span>Data Status</span>
              <select
                value={draft.data_status}
                onChange={(event) => updateDraft("data_status", event.target.value as DataStatus)}
              >
                <option value="unknown">Unknown</option>
                <option value="actual">Actual</option>
                <option value="estimated">Estimated</option>
                <option value="benchmark">Benchmark</option>
                <option value="user_assumption">User assumption</option>
                <option value="partner_supplied">Partner supplied</option>
              </select>
            </label>
            <label className="field">
              <span>Confidence</span>
              <select
                value={draft.confidence_level}
                onChange={(event) => updateDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                <option value="unknown">Unknown</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
            <div className="inline-actions unit-form-actions">
              <button className="button" type="submit" disabled={busy}>
                <Save size={16} aria-hidden="true" />
                {busy ? "Saving" : "Save Unit"}
              </button>
              <button className="button secondary" type="button" onClick={() => setFormOpen(false)} disabled={busy}>
                <X size={16} aria-hidden="true" />
                Cancel
              </button>
            </div>
          </form>
        </section>
      ) : null}

      <UnitList plants={plants} />
    </div>
  );
}
