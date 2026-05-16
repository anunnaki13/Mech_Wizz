"use client";

import { ClipboardCheck, Gauge, RefreshCw, Save, ShieldAlert, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import {
  createPreFeedDecisionGate,
  createPreFeedRisk,
  deletePreFeedDecisionGate,
  deletePreFeedRisk,
  getPreFeedDecisionDashboard,
  listPreFeedDecisionGates,
  listPreFeedRisks,
  updatePreFeedDecisionGate,
  updatePreFeedRisk,
} from "@/lib/api";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";
import type {
  PreFeedDecisionDashboard,
  PreFeedDecisionGate,
  PreFeedDecisionGateCategory,
  PreFeedDecisionGateStatus,
  PreFeedRisk,
  PreFeedRiskCategory,
  PreFeedRiskStatus,
} from "@/types/prefeed-decision";

const DATA_STATUS_OPTIONS: DataStatus[] = [
  "actual",
  "estimated",
  "benchmark",
  "user_assumption",
  "partner_supplied",
  "unknown",
];
const CONFIDENCE_OPTIONS: ConfidenceLevel[] = ["high", "medium", "low", "unknown"];
const RISK_CATEGORIES: PreFeedRiskCategory[] = [
  "technical",
  "commercial",
  "legal",
  "land",
  "grid",
  "offtake",
  "mrv",
  "financing",
  "economics",
  "execution",
  "other",
];
const RISK_STATUSES: PreFeedRiskStatus[] = ["open", "monitoring", "mitigating", "escalated", "closed"];
const GATE_CATEGORIES: PreFeedDecisionGateCategory[] = [
  "technical",
  "commercial",
  "legal",
  "land",
  "grid",
  "offtake",
  "mrv",
  "financing",
  "committee",
];
const GATE_STATUSES: PreFeedDecisionGateStatus[] = ["not_started", "in_progress", "ready", "blocked", "waived"];
const SCORE_OPTIONS = ["1", "2", "3", "4", "5"];

type RiskDraft = {
  category: PreFeedRiskCategory;
  risk_statement: string;
  likelihood: string;
  impact: string;
  mitigation: string;
  owner_name: string;
  due_date: string;
  status: PreFeedRiskStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

type GateDraft = {
  category: PreFeedDecisionGateCategory;
  gate_title: string;
  evidence_reference: string;
  owner_name: string;
  due_date: string;
  is_critical: boolean;
  status: PreFeedDecisionGateStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

const EMPTY_RISK: RiskDraft = {
  category: "technical",
  risk_statement: "",
  likelihood: "3",
  impact: "3",
  mitigation: "",
  owner_name: "",
  due_date: "",
  status: "open",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

const EMPTY_GATE: GateDraft = {
  category: "technical",
  gate_title: "",
  evidence_reference: "",
  owner_name: "",
  due_date: "",
  is_critical: false,
  status: "not_started",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

function labelFor(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function blankToNull(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `${Math.round(value * 100)}%`;
}

function formatNumber(value: number | null | undefined, digits = 0) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: digits });
}

function formatMoney(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `USD ${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

function formatTotals(values: Record<string, number> | undefined) {
  const entries = Object.entries(values ?? {});
  if (entries.length === 0) {
    return "None";
  }
  return entries.map(([currency, amount]) => `${currency} ${amount.toLocaleString("en-US")}`).join(", ");
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "None";
  }
  return new Date(value).toLocaleDateString("en-US", { dateStyle: "medium" });
}

export function DecisionDashboardWorkspace({ packageId }: { packageId: string | null }) {
  const [dashboard, setDashboard] = useState<PreFeedDecisionDashboard | null>(null);
  const [risks, setRisks] = useState<PreFeedRisk[]>([]);
  const [gates, setGates] = useState<PreFeedDecisionGate[]>([]);
  const [riskDraft, setRiskDraft] = useState<RiskDraft>(EMPTY_RISK);
  const [gateDraft, setGateDraft] = useState<GateDraft>(EMPTY_GATE);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function updateRiskDraft<K extends keyof RiskDraft>(key: K, value: RiskDraft[K]) {
    setRiskDraft((current) => ({ ...current, [key]: value }));
  }

  function updateGateDraft<K extends keyof GateDraft>(key: K, value: GateDraft[K]) {
    setGateDraft((current) => ({ ...current, [key]: value }));
  }

  async function loadAll() {
    if (!packageId) {
      setDashboard(null);
      setRisks([]);
      setGates([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const [dashboardData, riskRows, gateRows] = await Promise.all([
        getPreFeedDecisionDashboard(packageId),
        listPreFeedRisks(packageId),
        listPreFeedDecisionGates(packageId),
      ]);
      setDashboard(dashboardData);
      setRisks(riskRows);
      setGates(gateRows);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Decision dashboard could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveRisk() {
    if (!packageId || !riskDraft.risk_statement.trim()) {
      setErrorMessage("Package and risk statement are required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createPreFeedRisk(packageId, {
        category: riskDraft.category,
        risk_statement: riskDraft.risk_statement.trim(),
        likelihood: Number(riskDraft.likelihood),
        impact: Number(riskDraft.impact),
        mitigation: blankToNull(riskDraft.mitigation),
        owner_name: blankToNull(riskDraft.owner_name),
        due_date: riskDraft.due_date || null,
        status: riskDraft.status,
        data_status: riskDraft.data_status,
        confidence_level: riskDraft.confidence_level,
        notes: blankToNull(riskDraft.notes),
      });
      setRiskDraft(EMPTY_RISK);
      await loadAll();
      setStatusMessage("Risk saved.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Risk could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveGate() {
    if (!packageId || !gateDraft.gate_title.trim()) {
      setErrorMessage("Package and gate title are required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createPreFeedDecisionGate(packageId, {
        category: gateDraft.category,
        gate_title: gateDraft.gate_title.trim(),
        evidence_reference: blankToNull(gateDraft.evidence_reference),
        owner_name: blankToNull(gateDraft.owner_name),
        due_date: gateDraft.due_date || null,
        is_critical: gateDraft.is_critical,
        status: gateDraft.status,
        data_status: gateDraft.data_status,
        confidence_level: gateDraft.confidence_level,
        notes: blankToNull(gateDraft.notes),
      });
      setGateDraft(EMPTY_GATE);
      await loadAll();
      setStatusMessage("Decision gate saved.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Decision gate could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleRiskStatus(risk: PreFeedRisk, status: PreFeedRiskStatus) {
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await updatePreFeedRisk(risk.id, { status });
      await loadAll();
      setStatusMessage("Risk updated.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Risk could not be updated.");
    } finally {
      setBusy(false);
    }
  }

  async function handleGateStatus(gate: PreFeedDecisionGate, status: PreFeedDecisionGateStatus) {
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await updatePreFeedDecisionGate(gate.id, { status });
      await loadAll();
      setStatusMessage("Decision gate updated.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Decision gate could not be updated.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteRisk(riskId: string) {
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedRisk(riskId);
      await loadAll();
      setStatusMessage("Risk deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Risk could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteGate(gateId: string) {
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedDecisionGate(gateId);
      await loadAll();
      setStatusMessage("Decision gate deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Decision gate could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, [packageId]);

  if (!packageId) {
    return (
      <section className="decision-workspace card">
        <div className="setting-card-header">
          <div>
            <h3>Decision Dashboard</h3>
            <span>No package selected</span>
          </div>
          <Gauge size={18} aria-hidden="true" />
        </div>
        <div className="decision-empty muted">Save a package before managing risks and gates.</div>
      </section>
    );
  }

  return (
    <section className="decision-workspace">
      <article className="card decision-panel">
        <div className="setting-card-header">
          <div>
            <h3>Decision Dashboard</h3>
            <span>{loading ? "Refreshing" : dashboard?.package_name ?? "Package"}</span>
          </div>
          <button className="icon-button" type="button" onClick={() => void loadAll()} title="Refresh dashboard">
            <RefreshCw size={16} aria-hidden="true" />
          </button>
        </div>
        {errorMessage ? <div className="notice">{errorMessage}</div> : null}
        {statusMessage ? <div className="status-line">{statusMessage}</div> : null}
        <div className="decision-overview-grid">
          <div>
            <span>Package Confidence</span>
            <strong>{labelFor(dashboard?.package_confidence_level ?? "unknown")}</strong>
          </div>
          <div>
            <span>Risk Count</span>
            <strong>{dashboard?.risk_summary.risk_count ?? 0}</strong>
          </div>
          <div>
            <span>Gate Readiness</span>
            <strong>{formatPercent(dashboard?.decision_gate_summary.readiness_score)}</strong>
          </div>
          <div>
            <span>Blockers</span>
            <strong>{dashboard?.blockers.length ?? 0}</strong>
          </div>
          <div>
            <span>Next Actions</span>
            <strong>{dashboard?.next_actions.length ?? 0}</strong>
          </div>
        </div>
        <div className="decision-snapshot-grid">
          <div>
            <span>CAPEX</span>
            <strong>{formatTotals(dashboard?.cost_summary.capex_total_by_currency)}</strong>
          </div>
          <div>
            <span>OPEX</span>
            <strong>{formatTotals(dashboard?.cost_summary.annual_opex_total_by_currency)}</strong>
          </div>
          <div>
            <span>Vendors</span>
            <strong>{dashboard?.vendor_comparison.length ?? 0}</strong>
          </div>
          <div>
            <span>Offtake Revenue</span>
            <strong>{formatMoney(dashboard?.offtake_summary.gross_revenue_usd_per_year)}</strong>
          </div>
          <div>
            <span>MRV Readiness</span>
            <strong>{formatPercent(dashboard?.mrv_summary.readiness_score)}</strong>
          </div>
          <div>
            <span>Carbon Intensity</span>
            <strong>{formatNumber(dashboard?.mrv_summary.carbon_intensity_tco2e_per_ton_methanol, 3)}</strong>
          </div>
        </div>
        <div className="decision-two-column">
          <div className="decision-list">
            <h4>Blockers</h4>
            {(dashboard?.blockers ?? []).map((blocker) => (
              <div className="decision-list-row" key={`${blocker.source_module}-${blocker.title}`}>
                <strong>{blocker.title}</strong>
                <span>
                  {labelFor(blocker.priority_level)} / {blocker.owner ?? "Unassigned"}
                </span>
                <p>{blocker.recommendation}</p>
              </div>
            ))}
            {dashboard && dashboard.blockers.length === 0 ? <div className="muted">No blockers.</div> : null}
          </div>
          <div className="decision-list">
            <h4>Next Actions</h4>
            {(dashboard?.next_actions ?? []).map((action) => (
              <div className="decision-list-row" key={`${action.source_module}-${action.title}`}>
                <strong>{action.title}</strong>
                <span>
                  {labelFor(action.priority_level)} / {action.owner ?? "Unassigned"}
                </span>
                <p>{action.recommendation}</p>
              </div>
            ))}
            {dashboard && dashboard.next_actions.length === 0 ? <div className="muted">No next actions.</div> : null}
          </div>
        </div>
      </article>

      <div className="decision-grid">
        <article className="card decision-panel">
          <div className="setting-card-header">
            <div>
              <h3>Risk Register</h3>
              <span>{risks.length} risks</span>
            </div>
            <ShieldAlert size={18} aria-hidden="true" />
          </div>
          <div className="decision-form">
            <label className="field">
              <span>Category</span>
              <select
                value={riskDraft.category}
                onChange={(event) => updateRiskDraft("category", event.target.value as PreFeedRiskCategory)}
              >
                {RISK_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {labelFor(category)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Likelihood</span>
              <select value={riskDraft.likelihood} onChange={(event) => updateRiskDraft("likelihood", event.target.value)}>
                {SCORE_OPTIONS.map((score) => (
                  <option key={score} value={score}>
                    {score}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Impact</span>
              <select value={riskDraft.impact} onChange={(event) => updateRiskDraft("impact", event.target.value)}>
                {SCORE_OPTIONS.map((score) => (
                  <option key={score} value={score}>
                    {score}
                  </option>
                ))}
              </select>
            </label>
            <label className="field decision-form-wide">
              <span>Risk statement</span>
              <input
                value={riskDraft.risk_statement}
                onChange={(event) => updateRiskDraft("risk_statement", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Status</span>
              <select
                value={riskDraft.status}
                onChange={(event) => updateRiskDraft("status", event.target.value as PreFeedRiskStatus)}
              >
                {RISK_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {labelFor(status)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Owner</span>
              <input value={riskDraft.owner_name} onChange={(event) => updateRiskDraft("owner_name", event.target.value)} />
            </label>
            <label className="field">
              <span>Due date</span>
              <input type="date" value={riskDraft.due_date} onChange={(event) => updateRiskDraft("due_date", event.target.value)} />
            </label>
            <label className="field">
              <span>Data status</span>
              <select
                value={riskDraft.data_status}
                onChange={(event) => updateRiskDraft("data_status", event.target.value as DataStatus)}
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
                value={riskDraft.confidence_level}
                onChange={(event) => updateRiskDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>
                    {labelFor(level)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field decision-form-wide">
              <span>Mitigation</span>
              <textarea value={riskDraft.mitigation} onChange={(event) => updateRiskDraft("mitigation", event.target.value)} />
            </label>
            <button className="button" type="button" onClick={() => void handleSaveRisk()} disabled={busy}>
              <Save size={16} aria-hidden="true" />
              Save Risk
            </button>
          </div>
          <div className="table-wrap">
            <table className="data-table decision-table">
              <thead>
                <tr>
                  <th>Risk</th>
                  <th>Severity</th>
                  <th>Owner</th>
                  <th>Due</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {risks.map((risk) => (
                  <tr key={risk.id}>
                    <td>
                      <span className="table-link">{risk.risk_statement}</span>
                      <span className="table-subtext">{labelFor(risk.category)}</span>
                    </td>
                    <td>
                      <span className={`severity-chip ${risk.severity_band}`}>{labelFor(risk.severity_band)}</span>
                      <span className="table-subtext">{risk.severity_score}</span>
                    </td>
                    <td>{risk.owner_name ?? "Unassigned"}</td>
                    <td>{formatDate(risk.due_date)}</td>
                    <td>
                      <select
                        value={risk.status}
                        onChange={(event) => void handleRiskStatus(risk, event.target.value as PreFeedRiskStatus)}
                        disabled={busy}
                      >
                        {RISK_STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {labelFor(status)}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete risk"
                        title="Delete risk"
                        onClick={() => void handleDeleteRisk(risk.id)}
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
          {risks.length === 0 ? <div className="muted">No risks recorded.</div> : null}
        </article>

        <article className="card decision-panel">
          <div className="setting-card-header">
            <div>
              <h3>Decision Gates</h3>
              <span>{gates.length} gates</span>
            </div>
            <ClipboardCheck size={18} aria-hidden="true" />
          </div>
          <div className="decision-form">
            <label className="field">
              <span>Category</span>
              <select
                value={gateDraft.category}
                onChange={(event) => updateGateDraft("category", event.target.value as PreFeedDecisionGateCategory)}
              >
                {GATE_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {labelFor(category)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Status</span>
              <select
                value={gateDraft.status}
                onChange={(event) => updateGateDraft("status", event.target.value as PreFeedDecisionGateStatus)}
              >
                {GATE_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {labelFor(status)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field checkbox-field">
              <input
                type="checkbox"
                checked={gateDraft.is_critical}
                onChange={(event) => updateGateDraft("is_critical", event.target.checked)}
              />
              <span>Critical</span>
            </label>
            <label className="field decision-form-wide">
              <span>Gate title</span>
              <input value={gateDraft.gate_title} onChange={(event) => updateGateDraft("gate_title", event.target.value)} />
            </label>
            <label className="field">
              <span>Owner</span>
              <input value={gateDraft.owner_name} onChange={(event) => updateGateDraft("owner_name", event.target.value)} />
            </label>
            <label className="field">
              <span>Due date</span>
              <input type="date" value={gateDraft.due_date} onChange={(event) => updateGateDraft("due_date", event.target.value)} />
            </label>
            <label className="field">
              <span>Data status</span>
              <select
                value={gateDraft.data_status}
                onChange={(event) => updateGateDraft("data_status", event.target.value as DataStatus)}
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
                value={gateDraft.confidence_level}
                onChange={(event) => updateGateDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>
                    {labelFor(level)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field decision-form-wide">
              <span>Evidence</span>
              <textarea
                value={gateDraft.evidence_reference}
                onChange={(event) => updateGateDraft("evidence_reference", event.target.value)}
              />
            </label>
            <button className="button" type="button" onClick={() => void handleSaveGate()} disabled={busy}>
              <Save size={16} aria-hidden="true" />
              Save Gate
            </button>
          </div>
          <div className="table-wrap">
            <table className="data-table decision-table">
              <thead>
                <tr>
                  <th>Gate</th>
                  <th>Critical</th>
                  <th>Owner</th>
                  <th>Due</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {gates.map((gate) => (
                  <tr key={gate.id}>
                    <td>
                      <span className="table-link">{gate.gate_title}</span>
                      <span className="table-subtext">{labelFor(gate.category)}</span>
                    </td>
                    <td>{gate.is_critical ? "Yes" : "No"}</td>
                    <td>{gate.owner_name ?? "Unassigned"}</td>
                    <td>{formatDate(gate.due_date)}</td>
                    <td>
                      <select
                        value={gate.status}
                        onChange={(event) => void handleGateStatus(gate, event.target.value as PreFeedDecisionGateStatus)}
                        disabled={busy}
                      >
                        {GATE_STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {labelFor(status)}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete decision gate"
                        title="Delete decision gate"
                        onClick={() => void handleDeleteGate(gate.id)}
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
          {gates.length === 0 ? <div className="muted">No decision gates recorded.</div> : null}
        </article>
      </div>
    </section>
  );
}
