export type PilotGateStatus = "blocked" | "needs_evidence" | "committee_ready";
export type PilotRecommendation = "do_not_advance" | "continue_validation" | "advance_to_committee";

export type PilotDecisionBlocker = {
  plant_id: string;
  scenario_id: string;
  site_name: string;
  category: string;
  evidence_key: string;
  title: string;
  status: string;
  priority: string;
  recommendation: string;
};

export type PilotDecisionCandidate = {
  validation_rank: number;
  decision_rank: number;
  site_name: string;
  plant_id: string;
  scenario_id: string;
  province: string | null;
  capacity_mw: number | null;
  shortlist_score: number;
  evidence_readiness_score: number;
  evidence_adjusted_score: number;
  gate_status: PilotGateStatus;
  recommendation: PilotRecommendation;
  verified_items: number;
  rejected_items: number;
  high_priority_open_items: number;
  methanol_tpy: number | null;
  estimated_lcom_usd_ton: number | null;
  nearest_port_name: string | null;
  blockers: PilotDecisionBlocker[];
  next_actions: string[];
};

export type PilotDecisionDashboard = {
  scheme: string;
  limit: number;
  summary: {
    candidate_count: number;
    recommended_candidate: string | null;
    recommended_candidate_id: string | null;
    committee_ready_count: number;
    blocked_count: number;
    high_priority_open_items: number;
    average_evidence_readiness_score: number;
    decision_message: string;
  };
  candidates: PilotDecisionCandidate[];
  blockers: PilotDecisionBlocker[];
  action_plan: string[];
  methodology: string[];
  warnings: string[];
};
