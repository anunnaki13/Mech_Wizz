import type { ProjectDocument } from "@/types/document";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type PreFeedCostType = "capex" | "opex";
export type PreFeedOpexRecurrence = "annual" | "monthly" | "quarterly" | "weekly" | "daily" | "one_time";
export type PreFeedSelectionType = "blended_package" | "vendor_proposal";

export type PreFeedCostItem = {
  id: string;
  package_id: string;
  vendor_proposal_id: string | null;
  cost_type: PreFeedCostType;
  cost_component: string;
  amount: number;
  currency: string;
  unit_basis: string | null;
  recurrence: PreFeedOpexRecurrence | null;
  contingency_percent: number | null;
  escalation_percent: number | null;
  source_label: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedCostItemPayload = {
  vendor_proposal_id?: string | null;
  cost_type: PreFeedCostType;
  cost_component: string;
  amount: number;
  currency: string;
  unit_basis?: string | null;
  recurrence?: PreFeedOpexRecurrence | null;
  contingency_percent?: number | null;
  escalation_percent?: number | null;
  source_label?: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedCostSummary = {
  package_id: string;
  vendor_proposal_id: string | null;
  item_count: number;
  capex_total_by_currency: Record<string, number>;
  annual_opex_total_by_currency: Record<string, number>;
  scenario_ready_assumptions: Record<string, number>;
  warnings: string[];
};

export type PreFeedVendorProposal = {
  id: string;
  package_id: string;
  supporting_document_id: string | null;
  vendor_name: string;
  proposal_name: string;
  scope_capture_package: boolean;
  scope_electrolyzer: boolean;
  scope_methanol_plant: boolean;
  scope_storage_port: boolean;
  scope_grid_power: boolean;
  scope_land: boolean;
  scope_mrv: boolean;
  commercial_basis: string | null;
  delivery_assumptions: string | null;
  exclusions: string | null;
  validity_date: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  supporting_document: ProjectDocument | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedVendorProposalPayload = {
  supporting_document_id?: string | null;
  vendor_name: string;
  proposal_name: string;
  scope_capture_package: boolean;
  scope_electrolyzer: boolean;
  scope_methanol_plant: boolean;
  scope_storage_port: boolean;
  scope_grid_power: boolean;
  scope_land: boolean;
  scope_mrv: boolean;
  commercial_basis?: string | null;
  delivery_assumptions?: string | null;
  exclusions?: string | null;
  validity_date?: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedVendorGap = {
  proposal_id: string;
  source_module: string;
  missing_data_name: string;
  impact_level: string;
  priority_level: string;
  recommendation: string;
  status: string;
  confidence_level: ConfidenceLevel;
};

export type PreFeedVendorComparison = {
  proposal_id: string;
  vendor_name: string;
  proposal_name: string;
  capex_total_by_currency: Record<string, number>;
  annual_opex_total_by_currency: Record<string, number>;
  scope_completeness_score: number;
  missing_scopes: string[];
  gap_count: number;
  confidence_level: ConfidenceLevel;
  validity_date: string | null;
};

export type PreFeedActiveCostBasis = {
  id: string;
  scenario_id: string;
  package_id: string;
  vendor_proposal_id: string | null;
  selection_type: PreFeedSelectionType;
  is_active: boolean;
  snapshot_totals: Record<string, unknown> | null;
  scenario_ready_assumptions: Record<string, unknown> | null;
  selected_by: string | null;
  selection_notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedActiveCostBasisPayload = {
  package_id: string;
  vendor_proposal_id?: string | null;
  selection_type: PreFeedSelectionType;
  selected_by?: string | null;
  selection_notes?: string | null;
};
