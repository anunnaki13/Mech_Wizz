"use client";

import { AlertTriangle, Archive, FileText, Link2, Plus, RefreshCw, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { CostVendorWorkspace } from "@/components/prefeed/CostVendorWorkspace";
import { DecisionDashboardWorkspace } from "@/components/prefeed/DecisionDashboardWorkspace";
import { OfftakeMrvWorkspace } from "@/components/prefeed/OfftakeMrvWorkspace";
import {
  archivePreFeedPackage,
  createPreFeedPackage,
  getDocuments,
  getPlantScenarios,
  getPlants,
  getPreFeedPackage,
  getPreFeedPackageGaps,
  linkPreFeedPackageDocument,
  listPreFeedPackages,
  unlinkPreFeedPackageDocument,
  updatePreFeedPackage,
} from "@/lib/api";
import type { ProjectDocument } from "@/types/document";
import type { ConfidenceLevel, DataStatus, Plant } from "@/types/plant";
import type {
  PreFeedDocumentRole,
  PreFeedPackage,
  PreFeedPackageGap,
  PreFeedPackageStatus,
} from "@/types/prefeed";
import type { BusinessScenario } from "@/types/scenario";

const DATA_STATUS_OPTIONS: DataStatus[] = [
  "actual",
  "estimated",
  "benchmark",
  "user_assumption",
  "partner_supplied",
  "unknown",
];

const CONFIDENCE_OPTIONS: ConfidenceLevel[] = ["high", "medium", "low", "unknown"];
const PACKAGE_STATUS_OPTIONS: PreFeedPackageStatus[] = ["draft", "in_review", "validated", "archived"];
const DOCUMENT_ROLE_OPTIONS: PreFeedDocumentRole[] = [
  "vendor_proposal",
  "epc_estimate",
  "offtake_document",
  "mrv_document",
  "permit_document",
  "internal_note",
];

type ScenarioOption = BusinessScenario & {
  plant_name: string;
  unit_name: string;
};

type PackageDraft = {
  package_name: string;
  package_status: PreFeedPackageStatus;
  owner_name: string;
  source_organization: string;
  received_date: string;
  version_label: string;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

const EMPTY_DRAFT: PackageDraft = {
  package_name: "",
  package_status: "draft",
  owner_name: "",
  source_organization: "",
  received_date: "",
  version_label: "",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

function labelFor(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "Unknown";
  }
  return new Date(value).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function blankToNull(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function packageToDraft(record: PreFeedPackage | null): PackageDraft {
  if (!record) {
    return EMPTY_DRAFT;
  }
  return {
    package_name: record.package_name,
    package_status: record.package_status,
    owner_name: record.owner_name ?? "",
    source_organization: record.source_organization ?? "",
    received_date: record.received_date ?? "",
    version_label: record.version_label ?? "",
    data_status: record.data_status,
    confidence_level: record.confidence_level,
    notes: record.notes ?? "",
  };
}

export function PreFeedWorkspace() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioOption[]>([]);
  const [documents, setDocuments] = useState<ProjectDocument[]>([]);
  const [packages, setPackages] = useState<PreFeedPackage[]>([]);
  const [gaps, setGaps] = useState<PreFeedPackageGap[]>([]);
  const [selectedPlantId, setSelectedPlantId] = useState("");
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [selectedPackageId, setSelectedPackageId] = useState("");
  const [draft, setDraft] = useState<PackageDraft>(EMPTY_DRAFT);
  const [linkDocumentId, setLinkDocumentId] = useState("");
  const [linkRole, setLinkRole] = useState<PreFeedDocumentRole>("vendor_proposal");
  const [linkNotes, setLinkNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const selectedPlant = useMemo(
    () => plants.find((plant) => plant.id === selectedPlantId) ?? null,
    [plants, selectedPlantId],
  );

  const scenarioOptions = useMemo(
    () => scenarios.filter((scenario) => !selectedPlantId || scenario.plant_id === selectedPlantId),
    [scenarios, selectedPlantId],
  );

  const selectedPackage = useMemo(
    () => packages.find((record) => record.id === selectedPackageId) ?? null,
    [packages, selectedPackageId],
  );

  const availableDocuments = useMemo(
    () =>
      documents.filter((document) => {
        const plantMatches = !document.plant_id || !selectedPlantId || document.plant_id === selectedPlantId;
        const scenarioMatches =
          !document.scenario_id || !selectedScenarioId || document.scenario_id === selectedScenarioId;
        return plantMatches && scenarioMatches;
      }),
    [documents, selectedPlantId, selectedScenarioId],
  );

  function updateDraft<K extends keyof PackageDraft>(key: K, value: PackageDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function refreshPackage(packageId: string) {
    const [record, packageGaps] = await Promise.all([getPreFeedPackage(packageId), getPreFeedPackageGaps(packageId)]);
    setPackages((current) => [record, ...current.filter((item) => item.id !== record.id)]);
    setSelectedPackageId(record.id);
    setDraft(packageToDraft(record));
    setGaps(packageGaps);
  }

  async function loadPackagesFor(plantId: string, scenarioId: string, preferredPackageId?: string) {
    if (!plantId) {
      setPackages([]);
      setSelectedPackageId("");
      setDraft(EMPTY_DRAFT);
      setGaps([]);
      return;
    }
    const records = await listPreFeedPackages({
      plantId,
      scenarioId: scenarioId || undefined,
      includeArchived: true,
    });
    const nextPackage = records.find((record) => record.id === preferredPackageId) ?? records[0] ?? null;
    setPackages(records);
    setSelectedPackageId(nextPackage?.id ?? "");
    setDraft(packageToDraft(nextPackage));
    setGaps(nextPackage ? await getPreFeedPackageGaps(nextPackage.id) : []);
  }

  async function loadAll() {
    setLoading(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const [plantRecords, documentRecords] = await Promise.all([getPlants(), getDocuments()]);
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
      const nextPlantId = selectedPlantId || plantRecords[0]?.id || "";
      const nextScenarioId =
        selectedScenarioId && scenarioRecords.some((scenario) => scenario.id === selectedScenarioId)
          ? selectedScenarioId
          : scenarioRecords.find((scenario) => scenario.plant_id === nextPlantId)?.id ?? "";

      setPlants(plantRecords);
      setScenarios(scenarioRecords);
      setDocuments(documentRecords);
      setSelectedPlantId(nextPlantId);
      setSelectedScenarioId(nextScenarioId);
      await loadPackagesFor(nextPlantId, nextScenarioId, selectedPackageId);
      setStatusMessage("Pre-FEED workspace loaded.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Pre-FEED workspace could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePlantChange(plantId: string) {
    setSelectedPlantId(plantId);
    const nextScenarioId = scenarios.find((scenario) => scenario.plant_id === plantId)?.id ?? "";
    setSelectedScenarioId(nextScenarioId);
    setErrorMessage(null);
    try {
      await loadPackagesFor(plantId, nextScenarioId);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Packages could not be loaded.");
    }
  }

  async function handleScenarioChange(scenarioId: string) {
    setSelectedScenarioId(scenarioId);
    setErrorMessage(null);
    try {
      await loadPackagesFor(selectedPlantId, scenarioId);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Packages could not be loaded.");
    }
  }

  async function handlePackageChange(packageId: string) {
    setSelectedPackageId(packageId);
    setErrorMessage(null);
    try {
      const record = packages.find((item) => item.id === packageId) ?? null;
      setDraft(packageToDraft(record));
      setGaps(record ? await getPreFeedPackageGaps(record.id) : []);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Package warnings could not be loaded.");
    }
  }

  function handleNewPackage() {
    setSelectedPackageId("");
    setDraft({
      ...EMPTY_DRAFT,
      package_name: selectedPlant ? `${selectedPlant.plant_name} Pre-FEED Package` : "",
    });
    setGaps([]);
    setStatusMessage("New package draft ready.");
    setErrorMessage(null);
  }

  async function handleSavePackage() {
    if (!selectedPlantId || !draft.package_name.trim()) {
      setErrorMessage("Plant and package name are required.");
      return;
    }
    setBusy(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const payload = {
        plant_id: selectedPlantId,
        scenario_id: selectedScenarioId || null,
        package_name: draft.package_name.trim(),
        package_status: draft.package_status,
        owner_name: blankToNull(draft.owner_name),
        source_organization: blankToNull(draft.source_organization),
        received_date: draft.received_date || null,
        version_label: blankToNull(draft.version_label),
        data_status: draft.data_status,
        confidence_level: draft.confidence_level,
        notes: blankToNull(draft.notes),
      };
      const saved = selectedPackage
        ? await updatePreFeedPackage(selectedPackage.id, payload)
        : await createPreFeedPackage(payload);
      await loadPackagesFor(saved.plant_id, saved.scenario_id ?? "", saved.id);
      setStatusMessage("Package saved. Next: link documents, add cost/vendor and offtake/MRV data, then review Decision Dashboard.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Package could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleArchivePackage() {
    if (!selectedPackage) {
      return;
    }
    const confirmed = window.confirm(`Archive package "${selectedPackage.package_name}"? Archived packages stay in history but should not be used as active working data.`);
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const archived = await archivePreFeedPackage(selectedPackage.id);
      await loadPackagesFor(archived.plant_id, archived.scenario_id ?? "", archived.id);
      setStatusMessage("Package archived.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Package could not be archived.");
    } finally {
      setBusy(false);
    }
  }

  async function handleLinkDocument() {
    if (!selectedPackage || !linkDocumentId) {
      setErrorMessage("Select a package and document before linking.");
      return;
    }
    setBusy(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      await linkPreFeedPackageDocument(selectedPackage.id, {
        document_id: linkDocumentId,
        document_role: linkRole,
        notes: blankToNull(linkNotes),
      });
      await refreshPackage(selectedPackage.id);
      setLinkNotes("");
      setStatusMessage("Document linked.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Document could not be linked.");
    } finally {
      setBusy(false);
    }
  }

  async function handleUnlinkDocument(linkId: string) {
    if (!selectedPackage) {
      return;
    }
    const confirmed = window.confirm("Remove this document link from the package? The original document file will stay in Documents.");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      await unlinkPreFeedPackageDocument(selectedPackage.id, linkId);
      await refreshPackage(selectedPackage.id);
      setStatusMessage("Document unlinked.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Document link could not be removed.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, []);

  return (
    <div className="prefeed-workspace">
      <section className="page-header">
        <div>
          <h2>Pre-FEED Packages</h2>
          <p>Package source, version, evidence, confidence, and readiness warnings.</p>
        </div>
        <div className="inline-actions">
          <button className="button secondary" type="button" onClick={() => void loadAll()} disabled={loading}>
            <RefreshCw size={16} aria-hidden="true" />
            {loading ? "Refreshing" : "Refresh"}
          </button>
          <button className="button" type="button" onClick={handleNewPackage} disabled={!selectedPlantId}>
            <Plus size={16} aria-hidden="true" />
            New Package
          </button>
        </div>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="prefeed-controls">
        <label className="field">
          <span>Plant</span>
          <select value={selectedPlantId} onChange={(event) => void handlePlantChange(event.target.value)}>
            {plants.map((plant) => (
              <option key={plant.id} value={plant.id}>
                {plant.plant_name} {plant.unit_name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Scenario</span>
          <select value={selectedScenarioId} onChange={(event) => void handleScenarioChange(event.target.value)}>
            <option value="">No scenario</option>
            {scenarioOptions.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.scenario_name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Package</span>
          <select value={selectedPackageId} onChange={(event) => void handlePackageChange(event.target.value)}>
            <option value="">New package draft</option>
            {packages.map((record) => (
              <option key={record.id} value={record.id}>
                {record.package_name} ({labelFor(record.package_status)})
              </option>
            ))}
          </select>
        </label>
        <div className="prefeed-selected">
          <span>Selected package</span>
          <strong>{selectedPackage?.package_name ?? "Draft"}</strong>
        </div>
      </section>

      <section className="prefeed-layout">
        <div className="prefeed-main-stack">
          <article className="card prefeed-editor-panel">
            <div className="setting-card-header">
              <div>
                <h3>Package Metadata</h3>
                <span>{selectedPackage ? `Updated ${formatDate(selectedPackage.updated_at)}` : "Unsaved draft"}</span>
              </div>
              <div className="inline-actions">
                <button className="button" type="button" onClick={() => void handleSavePackage()} disabled={busy}>
                  <Save size={16} aria-hidden="true" />
                  {busy ? "Working" : "Save Package"}
                </button>
                <button
                  className="button danger"
                  type="button"
                  onClick={() => void handleArchivePackage()}
                  disabled={!selectedPackage || selectedPackage.package_status === "archived" || busy}
                >
                  <Archive size={16} aria-hidden="true" />
                  Archive
                </button>
              </div>
            </div>

            <div className="prefeed-form">
              <label className="field">
                <span>Package name</span>
                <input
                  value={draft.package_name}
                  onChange={(event) => updateDraft("package_name", event.target.value)}
                />
              </label>
              <label className="field">
                <span>Status</span>
                <select
                  value={draft.package_status}
                  onChange={(event) => updateDraft("package_status", event.target.value as PreFeedPackageStatus)}
                >
                  {PACKAGE_STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {labelFor(status)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Owner</span>
                <input value={draft.owner_name} onChange={(event) => updateDraft("owner_name", event.target.value)} />
              </label>
              <label className="field">
                <span>Source organization</span>
                <input
                  value={draft.source_organization}
                  onChange={(event) => updateDraft("source_organization", event.target.value)}
                />
              </label>
              <label className="field">
                <span>Received date</span>
                <input
                  type="date"
                  value={draft.received_date}
                  onChange={(event) => updateDraft("received_date", event.target.value)}
                />
              </label>
              <label className="field">
                <span>Version</span>
                <input
                  value={draft.version_label}
                  onChange={(event) => updateDraft("version_label", event.target.value)}
                />
              </label>
              <label className="field">
                <span>Data status</span>
                <select
                  value={draft.data_status}
                  onChange={(event) => updateDraft("data_status", event.target.value as DataStatus)}
                >
                  {DATA_STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {labelFor(status)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Confidence</span>
                <select
                  value={draft.confidence_level}
                  onChange={(event) => updateDraft("confidence_level", event.target.value as ConfidenceLevel)}
                >
                  {CONFIDENCE_OPTIONS.map((level) => (
                    <option key={level} value={level}>
                      {labelFor(level)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field prefeed-notes">
                <span>Notes</span>
                <textarea value={draft.notes} onChange={(event) => updateDraft("notes", event.target.value)} />
              </label>
            </div>
          </article>

          <article className="card prefeed-document-panel">
            <div className="setting-card-header">
              <div>
                <h3>Linked Documents</h3>
                <span>{selectedPackage?.document_links.length ?? 0} links</span>
              </div>
            </div>

            <div className="prefeed-link-controls">
              <label className="field">
                <span>Document</span>
                <select value={linkDocumentId} onChange={(event) => setLinkDocumentId(event.target.value)}>
                  <option value="">Select document</option>
                  {availableDocuments.map((document) => (
                    <option key={document.id} value={document.id}>
                      {document.original_filename}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Role</span>
                <select value={linkRole} onChange={(event) => setLinkRole(event.target.value as PreFeedDocumentRole)}>
                  {DOCUMENT_ROLE_OPTIONS.map((role) => (
                    <option key={role} value={role}>
                      {labelFor(role)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Link notes</span>
                <input value={linkNotes} onChange={(event) => setLinkNotes(event.target.value)} />
              </label>
              <button
                className="button"
                type="button"
                onClick={() => void handleLinkDocument()}
                disabled={!selectedPackage || !linkDocumentId || busy}
              >
                <Link2 size={16} aria-hidden="true" />
                Link
              </button>
            </div>

            <div className="table-wrap">
              <table className="data-table prefeed-document-table">
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Notes</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {(selectedPackage?.document_links ?? []).map((link) => (
                    <tr key={link.id}>
                      <td>
                        <span className="table-link">{link.document?.original_filename ?? link.document_id}</span>
                        <span className="table-subtext">{link.document?.document_category ?? "uncategorized"}</span>
                      </td>
                      <td>{labelFor(link.document_role)}</td>
                      <td>{link.document?.extraction_status ?? "Unknown"}</td>
                      <td>{link.notes ?? "None"}</td>
                      <td>
                        <button
                          className="icon-button"
                          type="button"
                          aria-label="Remove document link"
                          title="Remove document link"
                          onClick={() => void handleUnlinkDocument(link.id)}
                          disabled={busy}
                        >
                          <Trash2 size={16} aria-hidden="true" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!selectedPackage ? <div className="muted">Save a package before linking documents.</div> : null}
            {selectedPackage && selectedPackage.document_links.length === 0 ? (
              <div className="muted">No documents linked to this package.</div>
            ) : null}
          </article>

          <DecisionDashboardWorkspace packageId={selectedPackage?.id ?? null} />

          <CostVendorWorkspace
            packageId={selectedPackage?.id ?? null}
            scenarioId={selectedScenarioId || null}
            documents={availableDocuments}
          />

          <OfftakeMrvWorkspace
            packageId={selectedPackage?.id ?? null}
            scenarioId={selectedScenarioId || null}
            documents={availableDocuments}
          />
        </div>

        <aside className="prefeed-side-stack">
          <article className="card prefeed-warning-panel">
            <div className="setting-card-header">
              <div>
                <h3>Warnings</h3>
                <span>{gaps.length} open</span>
              </div>
              <AlertTriangle size={18} aria-hidden="true" />
            </div>
            <div className="prefeed-gap-list">
              {gaps.map((gap) => (
                <div className="data-gap-row" key={`${gap.source_module}-${gap.missing_data_name}`}>
                  <strong>{gap.missing_data_name}</strong>
                  <span>
                    {labelFor(gap.priority_level)} priority / {labelFor(gap.confidence_level)} confidence
                  </span>
                  <p>{gap.recommendation}</p>
                </div>
              ))}
              {gaps.length === 0 ? <div className="muted">No package warnings.</div> : null}
            </div>
          </article>

          <article className="card prefeed-detail-panel">
            <div className="setting-card-header">
              <div>
                <h3>Package Detail</h3>
                <span>{selectedPackage?.id ?? "Unsaved"}</span>
              </div>
              <FileText size={18} aria-hidden="true" />
            </div>
            <div className="detail-list">
              <div className="detail-row">
                <span>Plant</span>
                <span>{selectedPlant ? `${selectedPlant.plant_name} ${selectedPlant.unit_name}` : "Unknown"}</span>
              </div>
              <div className="detail-row">
                <span>Scenario</span>
                <span>
                  {scenarioOptions.find((scenario) => scenario.id === selectedScenarioId)?.scenario_name ?? "None"}
                </span>
              </div>
              <div className="detail-row">
                <span>Status</span>
                <span>{labelFor(draft.package_status)}</span>
              </div>
              <div className="detail-row">
                <span>Data status</span>
                <span>{labelFor(draft.data_status)}</span>
              </div>
              <div className="detail-row">
                <span>Confidence</span>
                <span>{labelFor(draft.confidence_level)}</span>
              </div>
              <div className="detail-row">
                <span>Created</span>
                <span>{formatDate(selectedPackage?.created_at)}</span>
              </div>
            </div>
          </article>
        </aside>
      </section>
    </div>
  );
}
