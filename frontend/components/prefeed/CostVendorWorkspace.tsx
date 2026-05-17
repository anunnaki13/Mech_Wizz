"use client";

import { AlertTriangle, BarChart3, CheckCircle2, Plus, RefreshCw, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  createPreFeedCostItem,
  createPreFeedVendorProposal,
  deletePreFeedCostItem,
  deletePreFeedVendorProposal,
  getPreFeedActiveCostBasis,
  getPreFeedCostSummary,
  getPreFeedVendorComparison,
  getPreFeedVendorGaps,
  listPreFeedCostItems,
  listPreFeedVendorProposals,
  selectPreFeedActiveCostBasis,
} from "@/lib/api";
import type { ProjectDocument } from "@/types/document";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";
import type {
  PreFeedActiveCostBasis,
  PreFeedCostItem,
  PreFeedCostSummary,
  PreFeedCostType,
  PreFeedOpexRecurrence,
  PreFeedSelectionType,
  PreFeedVendorComparison,
  PreFeedVendorGap,
  PreFeedVendorProposal,
} from "@/types/prefeed-cost";

const DATA_STATUS_OPTIONS: DataStatus[] = [
  "actual",
  "estimated",
  "benchmark",
  "user_assumption",
  "partner_supplied",
  "unknown",
];

const CONFIDENCE_OPTIONS: ConfidenceLevel[] = ["high", "medium", "low", "unknown"];
const COST_TYPES: PreFeedCostType[] = ["capex", "opex"];
const CAPEX_COMPONENTS = [
  "capture_package",
  "electrolyzer",
  "methanol_plant",
  "storage_port",
  "grid_power",
  "land",
  "mrv",
  "other",
];
const OPEX_CATEGORIES = [
  "fixed_opex",
  "variable_opex",
  "electricity",
  "water",
  "chemicals",
  "labor",
  "maintenance",
  "transport",
  "mrv",
  "other",
];
const RECURRENCES: PreFeedOpexRecurrence[] = ["annual", "monthly", "quarterly", "weekly", "daily", "one_time"];
const SCOPE_FIELDS = [
  ["scope_capture_package", "Capture package"],
  ["scope_electrolyzer", "Electrolyzer"],
  ["scope_methanol_plant", "Methanol plant"],
  ["scope_storage_port", "Storage/port"],
  ["scope_grid_power", "Grid power"],
  ["scope_land", "Land"],
  ["scope_mrv", "MRV"],
] as const;

type CostDraft = {
  vendor_proposal_id: string;
  cost_type: PreFeedCostType;
  cost_component: string;
  amount: string;
  currency: string;
  unit_basis: string;
  recurrence: PreFeedOpexRecurrence;
  contingency_percent: string;
  escalation_percent: string;
  source_label: string;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

type ProposalDraft = {
  supporting_document_id: string;
  vendor_name: string;
  proposal_name: string;
  scope_capture_package: boolean;
  scope_electrolyzer: boolean;
  scope_methanol_plant: boolean;
  scope_storage_port: boolean;
  scope_grid_power: boolean;
  scope_land: boolean;
  scope_mrv: boolean;
  commercial_basis: string;
  delivery_assumptions: string;
  exclusions: string;
  validity_date: string;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

const EMPTY_COST_DRAFT: CostDraft = {
  vendor_proposal_id: "",
  cost_type: "capex",
  cost_component: "capture_package",
  amount: "",
  currency: "USD",
  unit_basis: "",
  recurrence: "annual",
  contingency_percent: "",
  escalation_percent: "",
  source_label: "",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

const EMPTY_PROPOSAL_DRAFT: ProposalDraft = {
  supporting_document_id: "",
  vendor_name: "",
  proposal_name: "",
  scope_capture_package: false,
  scope_electrolyzer: false,
  scope_methanol_plant: false,
  scope_storage_port: false,
  scope_grid_power: false,
  scope_land: false,
  scope_mrv: false,
  commercial_basis: "",
  delivery_assumptions: "",
  exclusions: "",
  validity_date: "",
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

function numberOrNull(value: string) {
  return value.trim() ? Number(value) : null;
}

function formatTotals(values: Record<string, number> | undefined) {
  const entries = Object.entries(values ?? {});
  if (entries.length === 0) {
    return "None";
  }
  return entries.map(([currency, amount]) => `${currency} ${amount.toLocaleString("en-US")}`).join(", ");
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function CostVendorWorkspace({
  packageId,
  scenarioId,
  documents,
}: {
  packageId: string | null;
  scenarioId: string | null;
  documents: ProjectDocument[];
}) {
  const [costItems, setCostItems] = useState<PreFeedCostItem[]>([]);
  const [summary, setSummary] = useState<PreFeedCostSummary | null>(null);
  const [proposals, setProposals] = useState<PreFeedVendorProposal[]>([]);
  const [comparison, setComparison] = useState<PreFeedVendorComparison[]>([]);
  const [vendorGaps, setVendorGaps] = useState<PreFeedVendorGap[]>([]);
  const [activeBasis, setActiveBasis] = useState<PreFeedActiveCostBasis | null>(null);
  const [selectedProposalId, setSelectedProposalId] = useState("");
  const [selectionType, setSelectionType] = useState<PreFeedSelectionType>("blended_package");
  const [selectionNotes, setSelectionNotes] = useState("");
  const [selectedBy, setSelectedBy] = useState("");
  const [costDraft, setCostDraft] = useState<CostDraft>(EMPTY_COST_DRAFT);
  const [proposalDraft, setProposalDraft] = useState<ProposalDraft>(EMPTY_PROPOSAL_DRAFT);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const costComponents = costDraft.cost_type === "capex" ? CAPEX_COMPONENTS : OPEX_CATEGORIES;

  const proposalOptions = useMemo(
    () => proposals.map((proposal) => ({ id: proposal.id, label: `${proposal.vendor_name} - ${proposal.proposal_name}` })),
    [proposals],
  );

  function updateCostDraft<K extends keyof CostDraft>(key: K, value: CostDraft[K]) {
    setCostDraft((current) => ({ ...current, [key]: value }));
  }

  function updateProposalDraft<K extends keyof ProposalDraft>(key: K, value: ProposalDraft[K]) {
    setProposalDraft((current) => ({ ...current, [key]: value }));
  }

  async function loadAll(preferredProposalId = selectedProposalId) {
    if (!packageId) {
      setCostItems([]);
      setSummary(null);
      setProposals([]);
      setComparison([]);
      setVendorGaps([]);
      setActiveBasis(null);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const [costRecords, costSummary, proposalRecords, comparisonRows, active] = await Promise.all([
        listPreFeedCostItems({ packageId }),
        getPreFeedCostSummary({ packageId }),
        listPreFeedVendorProposals(packageId),
        getPreFeedVendorComparison(packageId),
        scenarioId ? getPreFeedActiveCostBasis(scenarioId) : Promise.resolve(null),
      ]);
      const nextProposalId =
        proposalRecords.find((proposal) => proposal.id === preferredProposalId)?.id ?? proposalRecords[0]?.id ?? "";
      const gaps = nextProposalId ? await getPreFeedVendorGaps(nextProposalId) : [];
      setCostItems(costRecords);
      setSummary(costSummary);
      setProposals(proposalRecords);
      setComparison(comparisonRows);
      setActiveBasis(active);
      setSelectedProposalId(nextProposalId);
      setVendorGaps(gaps);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Cost/vendor data could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveCostItem() {
    if (!packageId || !costDraft.amount.trim()) {
      setErrorMessage("Package and amount are required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createPreFeedCostItem(packageId, {
        vendor_proposal_id: blankToNull(costDraft.vendor_proposal_id),
        cost_type: costDraft.cost_type,
        cost_component: costDraft.cost_component,
        amount: Number(costDraft.amount),
        currency: costDraft.currency.trim().toUpperCase(),
        unit_basis: blankToNull(costDraft.unit_basis),
        recurrence: costDraft.cost_type === "opex" ? costDraft.recurrence : null,
        contingency_percent: costDraft.cost_type === "capex" ? numberOrNull(costDraft.contingency_percent) : null,
        escalation_percent: costDraft.cost_type === "capex" ? numberOrNull(costDraft.escalation_percent) : null,
        source_label: blankToNull(costDraft.source_label),
        data_status: costDraft.data_status,
        confidence_level: costDraft.confidence_level,
        notes: blankToNull(costDraft.notes),
      });
      setCostDraft(EMPTY_COST_DRAFT);
      await loadAll();
      setStatusMessage("Cost item saved. Next: review cost summary and save active cost basis if this should feed scenarios.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Cost item could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteCostItem(costItemId: string) {
    const confirmed = window.confirm("Delete this cost item? This cannot be undone.");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedCostItem(costItemId);
      await loadAll();
      setStatusMessage("Cost item deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Cost item could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveProposal() {
    if (!packageId || !proposalDraft.vendor_name.trim() || !proposalDraft.proposal_name.trim()) {
      setErrorMessage("Package, vendor name, and proposal name are required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const saved = await createPreFeedVendorProposal(packageId, {
        ...proposalDraft,
        supporting_document_id: blankToNull(proposalDraft.supporting_document_id),
        vendor_name: proposalDraft.vendor_name.trim(),
        proposal_name: proposalDraft.proposal_name.trim(),
        commercial_basis: blankToNull(proposalDraft.commercial_basis),
        delivery_assumptions: blankToNull(proposalDraft.delivery_assumptions),
        exclusions: blankToNull(proposalDraft.exclusions),
        validity_date: proposalDraft.validity_date || null,
        notes: blankToNull(proposalDraft.notes),
      });
      setProposalDraft(EMPTY_PROPOSAL_DRAFT);
      await loadAll(saved.id);
      setStatusMessage("Vendor proposal saved. Next: check proposal gaps and select active cost basis when ready.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Vendor proposal could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteProposal(proposalId: string) {
    const confirmed = window.confirm("Delete this vendor proposal? Related comparison and cost basis context may change.");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedVendorProposal(proposalId);
      await loadAll("");
      setStatusMessage("Vendor proposal deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Vendor proposal could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  async function handleProposalSelection(proposalId: string) {
    setSelectedProposalId(proposalId);
    setErrorMessage(null);
    try {
      setVendorGaps(proposalId ? await getPreFeedVendorGaps(proposalId) : []);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Vendor gaps could not be loaded.");
    }
  }

  async function handleSelectActiveBasis() {
    if (!packageId || !scenarioId) {
      setErrorMessage("Select a scenario and package before saving active cost basis.");
      return;
    }
    if (selectionType === "vendor_proposal" && !selectedProposalId) {
      setErrorMessage("Select a vendor proposal for vendor proposal cost basis.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const saved = await selectPreFeedActiveCostBasis(scenarioId, {
        package_id: packageId,
        vendor_proposal_id: selectionType === "vendor_proposal" ? selectedProposalId : null,
        selection_type: selectionType,
        selected_by: blankToNull(selectedBy),
        selection_notes: blankToNull(selectionNotes),
      });
      setActiveBasis(saved);
      await loadAll(selectedProposalId);
      setStatusMessage("Active cost basis saved. Next: run or review the scenario simulation that uses this basis.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Active cost basis could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void loadAll("");
  }, [packageId, scenarioId]);

  if (!packageId) {
    return (
      <article className="card cost-vendor-empty">
        <h3>Cost & Vendor Proposals</h3>
        <p className="muted">Save or select a Pre-FEED package before adding cost and vendor proposal data.</p>
      </article>
    );
  }

  return (
    <section className="cost-vendor-workspace">
      <div className="setting-card-header">
        <div>
          <h3>Cost & Vendor Proposals</h3>
          <span>{loading ? "Loading" : `${costItems.length} cost items / ${proposals.length} proposals`}</span>
        </div>
        <button className="button secondary" type="button" onClick={() => void loadAll()} disabled={loading}>
          <RefreshCw size={16} aria-hidden="true" />
          Refresh
        </button>
      </div>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <div className="cost-vendor-grid">
        <article className="card cost-item-panel">
          <div className="setting-card-header">
            <div>
              <h3>Cost Items</h3>
              <span>{summary?.item_count ?? 0} line items</span>
            </div>
            <BarChart3 size={18} aria-hidden="true" />
          </div>
          <div className="cost-item-form">
            <label className="field">
              <span>Type</span>
              <select
                value={costDraft.cost_type}
                onChange={(event) => {
                  const nextType = event.target.value as PreFeedCostType;
                  updateCostDraft("cost_type", nextType);
                  updateCostDraft("cost_component", nextType === "capex" ? "capture_package" : "fixed_opex");
                }}
              >
                {COST_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {labelFor(type)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Component</span>
              <select value={costDraft.cost_component} onChange={(event) => updateCostDraft("cost_component", event.target.value)}>
                {costComponents.map((component) => (
                  <option key={component} value={component}>
                    {labelFor(component)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Amount</span>
              <input type="number" min="0" value={costDraft.amount} onChange={(event) => updateCostDraft("amount", event.target.value)} />
            </label>
            <label className="field">
              <span>Currency</span>
              <input value={costDraft.currency} onChange={(event) => updateCostDraft("currency", event.target.value)} />
            </label>
            <label className="field">
              <span>Vendor proposal</span>
              <select value={costDraft.vendor_proposal_id} onChange={(event) => updateCostDraft("vendor_proposal_id", event.target.value)}>
                <option value="">Package blended</option>
                {proposalOptions.map((proposal) => (
                  <option key={proposal.id} value={proposal.id}>
                    {proposal.label}
                  </option>
                ))}
              </select>
            </label>
            {costDraft.cost_type === "capex" ? (
              <>
                <label className="field">
                  <span>Contingency %</span>
                  <input
                    type="number"
                    min="0"
                    value={costDraft.contingency_percent}
                    onChange={(event) => updateCostDraft("contingency_percent", event.target.value)}
                  />
                </label>
                <label className="field">
                  <span>Escalation %</span>
                  <input
                    type="number"
                    min="0"
                    value={costDraft.escalation_percent}
                    onChange={(event) => updateCostDraft("escalation_percent", event.target.value)}
                  />
                </label>
              </>
            ) : (
              <>
                <label className="field">
                  <span>Unit basis</span>
                  <input value={costDraft.unit_basis} onChange={(event) => updateCostDraft("unit_basis", event.target.value)} />
                </label>
                <label className="field">
                  <span>Recurrence</span>
                  <select value={costDraft.recurrence} onChange={(event) => updateCostDraft("recurrence", event.target.value as PreFeedOpexRecurrence)}>
                    {RECURRENCES.map((recurrence) => (
                      <option key={recurrence} value={recurrence}>
                        {labelFor(recurrence)}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            )}
            <label className="field">
              <span>Source</span>
              <input value={costDraft.source_label} onChange={(event) => updateCostDraft("source_label", event.target.value)} />
            </label>
            <label className="field">
              <span>Data status</span>
              <select value={costDraft.data_status} onChange={(event) => updateCostDraft("data_status", event.target.value as DataStatus)}>
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
                value={costDraft.confidence_level}
                onChange={(event) => updateCostDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>
                    {labelFor(level)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field cost-form-wide">
              <span>Notes</span>
              <input value={costDraft.notes} onChange={(event) => updateCostDraft("notes", event.target.value)} />
            </label>
            <button className="button" type="button" onClick={() => void handleSaveCostItem()} disabled={busy}>
              <Plus size={16} aria-hidden="true" />
              Add Cost
            </button>
          </div>
          <div className="cost-summary-grid">
            <div>
              <span>CAPEX</span>
              <strong>{formatTotals(summary?.capex_total_by_currency)}</strong>
            </div>
            <div>
              <span>Annual OPEX</span>
              <strong>{formatTotals(summary?.annual_opex_total_by_currency)}</strong>
            </div>
            <div>
              <span>Scenario patch</span>
              <strong>{Object.keys(summary?.scenario_ready_assumptions ?? {}).length} fields</strong>
            </div>
          </div>
          <div className="table-wrap">
            <table className="data-table cost-item-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Amount</th>
                  <th>Source</th>
                  <th>Confidence</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {costItems.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{labelFor(item.cost_component)}</strong>
                      <span className="table-subtext">{labelFor(item.cost_type)}</span>
                    </td>
                    <td>
                      {item.currency} {item.amount.toLocaleString("en-US")}
                    </td>
                    <td>{item.source_label ?? "None"}</td>
                    <td>{labelFor(item.confidence_level)}</td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete cost item"
                        title="Delete cost item"
                        onClick={() => void handleDeleteCostItem(item.id)}
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
          {summary?.warnings.map((warning) => (
            <div className="notice" key={warning}>{warning}</div>
          ))}
        </article>

        <article className="card vendor-panel">
          <div className="setting-card-header">
            <div>
              <h3>Vendor Proposals</h3>
              <span>{proposals.length} records</span>
            </div>
            <CheckCircle2 size={18} aria-hidden="true" />
          </div>
          <div className="vendor-form">
            <label className="field">
              <span>Vendor</span>
              <input value={proposalDraft.vendor_name} onChange={(event) => updateProposalDraft("vendor_name", event.target.value)} />
            </label>
            <label className="field">
              <span>Proposal</span>
              <input value={proposalDraft.proposal_name} onChange={(event) => updateProposalDraft("proposal_name", event.target.value)} />
            </label>
            <label className="field">
              <span>Supporting document</span>
              <select
                value={proposalDraft.supporting_document_id}
                onChange={(event) => updateProposalDraft("supporting_document_id", event.target.value)}
              >
                <option value="">None</option>
                {documents.map((document) => (
                  <option key={document.id} value={document.id}>
                    {document.original_filename}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Validity</span>
              <input
                type="date"
                value={proposalDraft.validity_date}
                onChange={(event) => updateProposalDraft("validity_date", event.target.value)}
              />
            </label>
            <div className="scope-grid">
              {SCOPE_FIELDS.map(([key, label]) => (
                <label key={key}>
                  <input
                    type="checkbox"
                    checked={proposalDraft[key]}
                    onChange={(event) => updateProposalDraft(key, event.target.checked)}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
            <label className="field">
              <span>Commercial basis</span>
              <input
                value={proposalDraft.commercial_basis}
                onChange={(event) => updateProposalDraft("commercial_basis", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Delivery assumptions</span>
              <input
                value={proposalDraft.delivery_assumptions}
                onChange={(event) => updateProposalDraft("delivery_assumptions", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Exclusions</span>
              <input value={proposalDraft.exclusions} onChange={(event) => updateProposalDraft("exclusions", event.target.value)} />
            </label>
            <label className="field">
              <span>Confidence</span>
              <select
                value={proposalDraft.confidence_level}
                onChange={(event) => updateProposalDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>
                    {labelFor(level)}
                  </option>
                ))}
              </select>
            </label>
            <button className="button" type="button" onClick={() => void handleSaveProposal()} disabled={busy}>
              <Save size={16} aria-hidden="true" />
              Save Proposal
            </button>
          </div>
          <div className="table-wrap">
            <table className="data-table vendor-table">
              <thead>
                <tr>
                  <th>Proposal</th>
                  <th>Validity</th>
                  <th>Confidence</th>
                  <th>Document</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {proposals.map((proposal) => (
                  <tr className={proposal.id === selectedProposalId ? "active" : ""} key={proposal.id}>
                    <td>
                      <button className="table-link" type="button" onClick={() => void handleProposalSelection(proposal.id)}>
                        {proposal.vendor_name}
                      </button>
                      <span className="table-subtext">{proposal.proposal_name}</span>
                    </td>
                    <td>{proposal.validity_date ?? "Unknown"}</td>
                    <td>{labelFor(proposal.confidence_level)}</td>
                    <td>{proposal.supporting_document?.original_filename ?? "None"}</td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete proposal"
                        title="Delete proposal"
                        onClick={() => void handleDeleteProposal(proposal.id)}
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
        </article>
      </div>

      <div className="cost-vendor-grid">
        <article className="card comparison-panel">
          <h3>Vendor Comparison</h3>
          <div className="table-wrap">
            <table className="data-table comparison-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>CAPEX</th>
                  <th>Annual OPEX</th>
                  <th>Scope</th>
                  <th>Gaps</th>
                  <th>Missing</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row) => (
                  <tr key={row.proposal_id}>
                    <td>
                      <strong>{row.vendor_name}</strong>
                      <span className="table-subtext">{row.proposal_name}</span>
                    </td>
                    <td>{formatTotals(row.capex_total_by_currency)}</td>
                    <td>{formatTotals(row.annual_opex_total_by_currency)}</td>
                    <td>{formatPercent(row.scope_completeness_score)}</td>
                    <td>{row.gap_count}</td>
                    <td>{row.missing_scopes.length ? row.missing_scopes.map(labelFor).join(", ") : "None"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {comparison.length === 0 ? <p className="muted">No vendor proposals to compare.</p> : null}
        </article>

        <aside className="cost-vendor-side">
          <article className="card active-basis-panel">
            <h3>Active Cost Basis</h3>
            <div className="active-basis-form">
              <label className="field">
                <span>Selection type</span>
                <select value={selectionType} onChange={(event) => setSelectionType(event.target.value as PreFeedSelectionType)}>
                  <option value="blended_package">Blended package</option>
                  <option value="vendor_proposal">Vendor proposal</option>
                </select>
              </label>
              <label className="field">
                <span>Proposal</span>
                <select
                  value={selectedProposalId}
                  onChange={(event) => void handleProposalSelection(event.target.value)}
                  disabled={selectionType !== "vendor_proposal"}
                >
                  <option value="">Select proposal</option>
                  {proposalOptions.map((proposal) => (
                    <option key={proposal.id} value={proposal.id}>
                      {proposal.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Selected by</span>
                <input value={selectedBy} onChange={(event) => setSelectedBy(event.target.value)} />
              </label>
              <label className="field">
                <span>Notes</span>
                <input value={selectionNotes} onChange={(event) => setSelectionNotes(event.target.value)} />
              </label>
              <button className="button" type="button" onClick={() => void handleSelectActiveBasis()} disabled={!scenarioId || busy}>
                <Save size={16} aria-hidden="true" />
                Save Basis
              </button>
            </div>
            <div className="detail-list">
              <div className="detail-row">
                <span>Current type</span>
                <span>{activeBasis ? labelFor(activeBasis.selection_type) : "None"}</span>
              </div>
              <div className="detail-row">
                <span>Selected by</span>
                <span>{activeBasis?.selected_by ?? "Unknown"}</span>
              </div>
              <div className="detail-row">
                <span>Patch fields</span>
                <span>{Object.keys(activeBasis?.scenario_ready_assumptions ?? {}).length}</span>
              </div>
            </div>
          </article>

          <article className="card vendor-gap-panel">
            <div className="setting-card-header">
              <div>
                <h3>Proposal Gaps</h3>
                <span>{vendorGaps.length} open</span>
              </div>
              <AlertTriangle size={18} aria-hidden="true" />
            </div>
            <div className="prefeed-gap-list">
              {vendorGaps.map((gap) => (
                <div className="data-gap-row" key={`${gap.proposal_id}-${gap.missing_data_name}`}>
                  <strong>{gap.missing_data_name}</strong>
                  <span>
                    {labelFor(gap.priority_level)} priority / {labelFor(gap.confidence_level)} confidence
                  </span>
                  <p>{gap.recommendation}</p>
                </div>
              ))}
              {vendorGaps.length === 0 ? <p className="muted">No proposal gaps selected.</p> : null}
            </div>
          </article>
        </aside>
      </div>
    </section>
  );
}
