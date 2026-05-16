import type { LlmInsight } from "@/types/llm";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";
import type { PreFeedPackageGap } from "@/types/prefeed";
import type { PreFeedActiveCostBasis, PreFeedCostSummary, PreFeedVendorComparison } from "@/types/prefeed-cost";
import type { PreFeedGap, PreFeedMrvSummary, PreFeedOfftakeSummary } from "@/types/prefeed-market";

export type PreFeedRiskCategory =
  | "technical"
  | "commercial"
  | "legal"
  | "land"
  | "grid"
  | "offtake"
  | "mrv"
  | "financing"
  | "economics"
  | "execution"
  | "other";

export type PreFeedRiskStatus = "open" | "monitoring" | "mitigating" | "escalated" | "closed";
export type PreFeedDecisionGateCategory =
  | "technical"
  | "commercial"
  | "legal"
  | "land"
  | "grid"
  | "offtake"
  | "mrv"
  | "financing"
  | "committee";
export type PreFeedDecisionGateStatus = "not_started" | "in_progress" | "ready" | "blocked" | "waived";
export type PreFeedSeverityBand = "low" | "medium" | "high" | "critical";

export type PreFeedRisk = {
  id: string;
  package_id: string;
  category: PreFeedRiskCategory;
  risk_statement: string;
  likelihood: number;
  impact: number;
  severity_score: number;
  severity_band: PreFeedSeverityBand;
  mitigation: string | null;
  owner_name: string | null;
  due_date: string | null;
  status: PreFeedRiskStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedRiskPayload = {
  category: PreFeedRiskCategory;
  risk_statement: string;
  likelihood: number;
  impact: number;
  mitigation?: string | null;
  owner_name?: string | null;
  due_date?: string | null;
  status: PreFeedRiskStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedDecisionGate = {
  id: string;
  package_id: string;
  category: PreFeedDecisionGateCategory;
  gate_title: string;
  evidence_reference: string | null;
  owner_name: string | null;
  due_date: string | null;
  is_critical: boolean;
  status: PreFeedDecisionGateStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedDecisionGatePayload = {
  category: PreFeedDecisionGateCategory;
  gate_title: string;
  evidence_reference?: string | null;
  owner_name?: string | null;
  due_date?: string | null;
  is_critical: boolean;
  status: PreFeedDecisionGateStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedDecisionBlocker = {
  source_module: string;
  source_id: string | null;
  title: string;
  priority_level: string;
  owner: string | null;
  recommendation: string;
  status: string;
  confidence_level: ConfidenceLevel;
};

export type PreFeedDecisionNextAction = {
  source_module: string;
  source_id: string | null;
  title: string;
  priority_level: string;
  owner: string | null;
  recommendation: string;
  status: string;
};

export type PreFeedRiskSummary = {
  package_id: string;
  risk_count: number;
  open_risk_count: number;
  escalated_risk_count: number;
  severity_distribution: Record<PreFeedSeverityBand, number>;
  top_risks: PreFeedRisk[];
  warnings: string[];
};

export type PreFeedDecisionGateSummary = {
  package_id: string;
  gate_count: number;
  ready_gate_count: number;
  blocked_gate_count: number;
  critical_blocker_count: number;
  readiness_score: number;
  status_distribution: Record<PreFeedDecisionGateStatus, number>;
  gates_by_category: Record<string, { total: number; ready: number; blocked: number }>;
  warnings: string[];
};

export type PreFeedDecisionDashboard = {
  package_id: string;
  plant_id: string;
  scenario_id: string | null;
  package_name: string;
  package_status: string;
  package_confidence_level: ConfidenceLevel;
  package_data_status: DataStatus;
  package_gaps: PreFeedPackageGap[];
  cost_summary: PreFeedCostSummary;
  active_cost_basis: PreFeedActiveCostBasis | null;
  vendor_comparison: PreFeedVendorComparison[];
  offtake_summary: PreFeedOfftakeSummary;
  offtake_gaps: PreFeedGap[];
  mrv_summary: PreFeedMrvSummary;
  mrv_gaps: PreFeedGap[];
  risk_summary: PreFeedRiskSummary;
  decision_gate_summary: PreFeedDecisionGateSummary;
  blockers: PreFeedDecisionBlocker[];
  next_actions: PreFeedDecisionNextAction[];
  warnings: string[];
};

export type PreFeedCommitteeBrief = LlmInsight;
