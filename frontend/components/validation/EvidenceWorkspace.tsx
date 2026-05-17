"use client";

import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  FileSearch,
  Link2,
  RefreshCw,
  Save,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  createValidationEvidence,
  getEvidenceWorkspace,
  updateValidationEvidence,
} from "@/lib/api";
import type {
  ValidationEvidenceConfidence,
  ValidationEvidencePayload,
  ValidationEvidencePriority,
  ValidationEvidenceRequirement,
  ValidationEvidenceStatus,
  ValidationEvidenceWorkspace as Workspace,
} from "@/types/validation-evidence";

const STATUS_OPTIONS: ValidationEvidenceStatus[] = ["missing", "requested", "received", "verified", "rejected"];
const PRIORITY_OPTIONS: ValidationEvidencePriority[] = ["high", "medium", "low"];
const CONFIDENCE_OPTIONS: ValidationEvidenceConfidence[] = ["high", "medium", "low", "unknown"];

type EvidenceDraft = {
  title: string;
  required_evidence: string;
  current_basis: string;
  status: ValidationEvidenceStatus;
  priority: ValidationEvidencePriority;
  owner_name: string;
  source_organization: string;
  reference_url: string;
  due_date: string;
  received_date: string;
  verified_date: string;
  confidence_level: ValidationEvidenceConfidence;
  notes: string;
};

const EMPTY_DRAFT: EvidenceDraft = {
  title: "",
  required_evidence: "",
  current_basis: "",
  status: "missing",
  priority: "high",
  owner_name: "",
  source_organization: "",
  reference_url: "",
  due_date: "",
  received_date: "",
  verified_date: "",
  confidence_level: "unknown",
  notes: "",
};

function labelFor(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value: number | null | undefined, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

function formatCompact(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1, notation: "compact" })}${suffix}`;
}

function evidenceItemId(item: ValidationEvidenceRequirement) {
  return `${item.plant_id}:${item.scenario_id}:${item.category}:${item.evidence_key}`;
}

function blankToNull(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function itemToDraft(item: ValidationEvidenceRequirement | null): EvidenceDraft {
  if (!item) {
    return EMPTY_DRAFT;
  }
  return {
    title: item.record?.title ?? item.title,
    required_evidence: item.record?.required_evidence ?? item.required_evidence,
    current_basis: item.record?.current_basis ?? item.current_basis,
    status: item.record?.status ?? item.status,
    priority: item.record?.priority ?? item.priority,
    owner_name: item.record?.owner_name ?? "",
    source_organization: item.record?.source_organization ?? "",
    reference_url: item.record?.reference_url ?? "",
    due_date: item.record?.due_date ?? "",
    received_date: item.record?.received_date ?? "",
    verified_date: item.record?.verified_date ?? "",
    confidence_level: item.record?.confidence_level ?? item.confidence_level,
    notes: item.record?.notes ?? "",
  };
}

function readinessClass(score: number) {
  if (score >= 80) {
    return "good";
  }
  if (score >= 45) {
    return "watch";
  }
  return "weak";
}

function payloadFromDraft(draft: EvidenceDraft): ValidationEvidencePayload {
  return {
    title: draft.title.trim(),
    required_evidence: blankToNull(draft.required_evidence),
    current_basis: blankToNull(draft.current_basis),
    status: draft.status,
    priority: draft.priority,
    owner_name: blankToNull(draft.owner_name),
    source_organization: blankToNull(draft.source_organization),
    reference_url: blankToNull(draft.reference_url),
    due_date: blankToNull(draft.due_date),
    received_date: blankToNull(draft.received_date),
    verified_date: blankToNull(draft.verified_date),
    confidence_level: draft.confidence_level,
    notes: blankToNull(draft.notes),
  };
}

export function EvidenceWorkspace({
  initialWorkspace,
  initialLoadError = false,
}: {
  initialWorkspace: Workspace | null;
  initialLoadError?: boolean;
}) {
  const [workspace, setWorkspace] = useState<Workspace | null>(initialWorkspace);
  const [selectedItemId, setSelectedItemId] = useState("");
  const [draft, setDraft] = useState<EvidenceDraft>(EMPTY_DRAFT);
  const [loading, setLoading] = useState(!initialWorkspace);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(
    initialLoadError ? "Evidence workspace data is not reachable." : null,
  );

  const evidenceItems = useMemo(
    () => workspace?.candidates.flatMap((candidate) => candidate.evidence_items) ?? [],
    [workspace],
  );

  const selectedItem = useMemo(
    () => evidenceItems.find((item) => evidenceItemId(item) === selectedItemId) ?? evidenceItems[0] ?? null,
    [evidenceItems, selectedItemId],
  );

  useEffect(() => {
    if (!selectedItemId && selectedItem) {
      setSelectedItemId(evidenceItemId(selectedItem));
      setDraft(itemToDraft(selectedItem));
    }
  }, [selectedItem, selectedItemId]);

  useEffect(() => {
    if (selectedItem) {
      setDraft(itemToDraft(selectedItem));
    }
  }, [selectedItemId, selectedItem]);

  async function loadWorkspace(preferredItemId = selectedItemId) {
    setLoading(true);
    setErrorMessage(null);
    try {
      const nextWorkspace = await getEvidenceWorkspace({ scheme: "align", limit: 3 });
      setWorkspace(nextWorkspace);
      const nextItems = nextWorkspace.candidates.flatMap((candidate) => candidate.evidence_items);
      const nextItem =
        nextItems.find((item) => evidenceItemId(item) === preferredItemId) ??
        nextItems.find((item) => item.status !== "verified") ??
        nextItems[0] ??
        null;
      setSelectedItemId(nextItem ? evidenceItemId(nextItem) : "");
      setDraft(itemToDraft(nextItem));
      setStatusMessage("Evidence workspace refreshed.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Evidence workspace could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  function updateDraft<K extends keyof EvidenceDraft>(key: K, value: EvidenceDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function selectItem(item: ValidationEvidenceRequirement) {
    setSelectedItemId(evidenceItemId(item));
    setDraft(itemToDraft(item));
    setStatusMessage(null);
    setErrorMessage(null);
  }

  async function handleSave() {
    if (!selectedItem) {
      setErrorMessage("Select an evidence item first.");
      return;
    }
    if (!draft.title.trim()) {
      setErrorMessage("Evidence title is required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    try {
      const payload = payloadFromDraft(draft);
      if (selectedItem.record) {
        await updateValidationEvidence(selectedItem.record.id, payload);
      } else {
        await createValidationEvidence({
          ...payload,
          plant_id: selectedItem.plant_id,
          scenario_id: selectedItem.scenario_id,
          category: selectedItem.category,
          evidence_key: selectedItem.evidence_key,
        });
      }
      await loadWorkspace(evidenceItemId(selectedItem));
      setStatusMessage("Evidence saved. Next: open Pilot Decision to see whether readiness, blockers, or gate status changed.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Evidence could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  const summary = workspace?.summary;

  return (
    <div className="evidence-page">
      <section className="evidence-hero">
        <div>
          <div className="eyebrow">Phase 12 evidence workspace</div>
          <h2>Top 3 Evidence Collection</h2>
          <p>
            Ruang kerja untuk mengubah checklist validasi menjadi status bukti yang bisa disimpan,
            dilacak, dan dibawa ke keputusan pilot.
          </p>
        </div>
        <div className="hero-actions">
          <button className="button secondary" type="button" onClick={() => loadWorkspace()} disabled={loading || busy}>
            <RefreshCw size={16} aria-hidden="true" />
            Refresh
          </button>
          <Link className="button secondary" href="/validation-pack">
            <ClipboardList size={16} aria-hidden="true" />
            Validation Pack
          </Link>
          <Link className="button secondary" href="/pilot-decision">
            <CheckCircle2 size={16} aria-hidden="true" />
            Pilot Decision
          </Link>
        </div>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="operator-flow-strip" aria-label="Evidence operating flow">
        <span>Alur evidence</span>
        <strong>1 Pilih item bukti</strong>
        <strong>2 Ubah status dan confidence</strong>
        <strong>3 Save Evidence</strong>
        <strong>4 Review Pilot Decision</strong>
      </section>

      <section className="summary-grid" aria-label="Evidence summary">
        <div className="summary-card primary">
          <span>Readiness</span>
          <strong>{formatNumber(summary?.evidence_readiness_score, 1)}%</strong>
          <small>Weighted by validation status</small>
        </div>
        <div className="summary-card">
          <span>Lead candidate</span>
          <strong>{summary?.lead_candidate ?? "-"}</strong>
          <small>{summary?.candidate_count ?? 0} Top 3 candidates</small>
        </div>
        <div className="summary-card">
          <span>Evidence items</span>
          <strong>{summary?.total_items ?? 0}</strong>
          <small>Across technical, economics, logistics, H2, MRV</small>
        </div>
        <div className="summary-card">
          <span>Verified</span>
          <strong>{summary?.verified_items ?? 0}</strong>
          <small>Committee-ready evidence</small>
        </div>
        <div className="summary-card">
          <span>High gaps</span>
          <strong>{summary?.high_priority_open_items ?? 0}</strong>
          <small>High-priority not verified</small>
        </div>
        <div className="summary-card">
          <span>Rejected</span>
          <strong>{summary?.counts_by_status.rejected ?? 0}</strong>
          <small>No-go evidence signals</small>
        </div>
      </section>

      <section className="evidence-layout">
        <div className="evidence-main-stack">
          <section className="card report-panel">
            <div className="section-title-row">
              <div>
                <h3>Candidate Evidence Board</h3>
                <p>Status disimpan per kandidat dan item bukti, bukan hanya checklist statis.</p>
              </div>
            </div>
            <div className="evidence-candidate-grid">
              {(workspace?.candidates ?? []).map((candidate) => (
                <article className="evidence-candidate-card" key={candidate.plant_id}>
                  <div className="evidence-candidate-head">
                    <div>
                      <span>#{candidate.validation_rank} candidate</span>
                      <h3>{candidate.site_name}</h3>
                      <p>{candidate.province ?? "Unknown"} · {formatNumber(candidate.capacity_mw, 1)} MW</p>
                    </div>
                    <strong>{formatNumber(candidate.evidence_readiness_score, 1)}%</strong>
                  </div>
                  <div className={`readiness-meter ${readinessClass(candidate.evidence_readiness_score)}`}>
                    <i style={{ width: `${Math.max(0, Math.min(100, candidate.evidence_readiness_score))}%` }} />
                  </div>
                  <div className="evidence-mini-metrics">
                    <div><span>Methanol</span><strong>{formatCompact(candidate.methanol_tpy, " t/y")}</strong></div>
                    <div><span>LCOM</span><strong>{formatNumber(candidate.estimated_lcom_usd_ton, 0)} USD/t</strong></div>
                    <div><span>Port</span><strong>{candidate.nearest_port_name ?? "-"}</strong></div>
                    <div><span>High open</span><strong>{candidate.high_priority_open_items}</strong></div>
                  </div>
                  <div className="evidence-item-list">
                    {candidate.evidence_items.map((item) => {
                      const itemId = evidenceItemId(item);
                      return (
                        <button
                          className={`evidence-item-button ${item.status} ${selectedItemId === itemId ? "active" : ""}`}
                          type="button"
                          key={itemId}
                          onClick={() => selectItem(item)}
                        >
                          <span>{labelFor(item.category)} · {item.priority}</span>
                          <strong>{item.title}</strong>
                          <small>{item.required_evidence}</small>
                          <em>{labelFor(item.status)}</em>
                        </button>
                      );
                    })}
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="card report-panel">
            <h3>Status Mix</h3>
            <div className="evidence-status-grid">
              {STATUS_OPTIONS.map((status) => (
                <div className={`evidence-status-cell ${status}`} key={status}>
                  <span>{labelFor(status)}</span>
                  <strong>{summary?.counts_by_status[status] ?? 0}</strong>
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="evidence-side-stack">
          <section className="card report-panel evidence-editor-card">
            <FileSearch size={18} aria-hidden="true" />
            <div>
              <h3>Evidence Record</h3>
              <p>{selectedItem ? `${labelFor(selectedItem.category)} evidence for selected candidate.` : "No item selected."}</p>
            </div>
            <div className="form-grid evidence-form-grid">
              <label className="field">
                <span>Status</span>
                <select value={draft.status} onChange={(event) => updateDraft("status", event.target.value as ValidationEvidenceStatus)}>
                  {STATUS_OPTIONS.map((status) => (
                    <option value={status} key={status}>{labelFor(status)}</option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Priority</span>
                <select value={draft.priority} onChange={(event) => updateDraft("priority", event.target.value as ValidationEvidencePriority)}>
                  {PRIORITY_OPTIONS.map((priority) => (
                    <option value={priority} key={priority}>{labelFor(priority)}</option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Confidence</span>
                <select value={draft.confidence_level} onChange={(event) => updateDraft("confidence_level", event.target.value as ValidationEvidenceConfidence)}>
                  {CONFIDENCE_OPTIONS.map((confidence) => (
                    <option value={confidence} key={confidence}>{labelFor(confidence)}</option>
                  ))}
                </select>
              </label>
              <label className="field wide">
                <span>Title</span>
                <input value={draft.title} onChange={(event) => updateDraft("title", event.target.value)} />
              </label>
              <label className="field wide">
                <span>Required Evidence</span>
                <textarea value={draft.required_evidence} onChange={(event) => updateDraft("required_evidence", event.target.value)} rows={3} />
              </label>
              <label className="field wide">
                <span>Current Basis</span>
                <textarea value={draft.current_basis} onChange={(event) => updateDraft("current_basis", event.target.value)} rows={3} />
              </label>
              <label className="field">
                <span>Owner</span>
                <input value={draft.owner_name} onChange={(event) => updateDraft("owner_name", event.target.value)} />
              </label>
              <label className="field">
                <span>Source Org</span>
                <input value={draft.source_organization} onChange={(event) => updateDraft("source_organization", event.target.value)} />
              </label>
              <label className="field">
                <span>Due Date</span>
                <input type="date" value={draft.due_date} onChange={(event) => updateDraft("due_date", event.target.value)} />
              </label>
              <label className="field">
                <span>Received</span>
                <input type="date" value={draft.received_date} onChange={(event) => updateDraft("received_date", event.target.value)} />
              </label>
              <label className="field">
                <span>Verified</span>
                <input type="date" value={draft.verified_date} onChange={(event) => updateDraft("verified_date", event.target.value)} />
              </label>
              <label className="field wide">
                <span>Reference URL</span>
                <input value={draft.reference_url} onChange={(event) => updateDraft("reference_url", event.target.value)} />
              </label>
              <label className="field wide">
                <span>Notes</span>
                <textarea value={draft.notes} onChange={(event) => updateDraft("notes", event.target.value)} rows={4} />
              </label>
            </div>
            <button className="button" type="button" onClick={handleSave} disabled={busy || loading || !selectedItem}>
              <Save size={16} aria-hidden="true" />
              Save Evidence
            </button>
          </section>

          <section className="card report-panel">
            <h3>Selected Evidence</h3>
            {selectedItem ? (
              <div className="evidence-selected">
                <span>{labelFor(selectedItem.category)}</span>
                <strong>{selectedItem.title}</strong>
                <p>{selectedItem.current_basis}</p>
                <div className={`evidence-status-chip ${selectedItem.status}`}>
                  <CheckCircle2 size={14} aria-hidden="true" />
                  {labelFor(selectedItem.status)}
                </div>
                {selectedItem.record?.reference_url ? (
                  <a className="section-link" href={selectedItem.record.reference_url} target="_blank" rel="noreferrer">
                    <Link2 size={14} aria-hidden="true" />
                    Reference
                  </a>
                ) : null}
              </div>
            ) : (
              <p>No evidence item selected.</p>
            )}
          </section>

          <section className="card report-panel">
            <h3>Decision Warnings</h3>
            <div className="validation-list warning">
              {(workspace?.warnings ?? []).map((warning) => (
                <div key={warning}><AlertTriangle size={15} aria-hidden="true" /><span>{warning}</span></div>
              ))}
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}
