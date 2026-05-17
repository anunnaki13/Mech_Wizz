export type ValidationEvidenceItem = {
  category: string;
  item: string;
  current_basis: string;
  required_evidence: string;
  status: "available" | "needs_validation" | "critical_gap";
  priority: "high" | "medium" | "low";
};

export type ValidationCandidatePack = {
  validation_rank: number;
  site_name: string;
  plant_id: string;
  scenario_id: string;
  province: string | null;
  city: string | null;
  capacity_mw: number | null;
  final_score: number;
  economics_score: number;
  logistics_score: number;
  confidence_score: number;
  captured_co2_tpy: number | null;
  methanol_tpy: number | null;
  h2_required_tpy: number | null;
  electrolyzer_required_mw: number | null;
  gross_revenue_usd_per_year: number | null;
  estimated_lcom_usd_ton: number | null;
  nearest_port_name: string | null;
  nearest_port_distance_km: number | null;
  data_confidence_label: string;
  data_gap_count: number;
  key_bottleneck: string;
  recommendation: string;
  why_shortlisted: string[];
  validation_items: ValidationEvidenceItem[];
  next_actions: string[];
};

export type ValidationComparisonAxis = {
  axis: string;
  leader: string | null;
  notes: string;
};

export type CommitteeMemo = {
  title: string;
  recommendation: string;
  executive_summary: string;
  decision_ask: string;
  top3_summary: string[];
  decision_questions: string[];
  no_go_triggers: string[];
  caveats: string[];
};

export type Top3ValidationPack = {
  scheme: string;
  limit: number;
  summary: {
    candidate_count: number;
    lead_candidate: string | null;
    total_captured_co2_tpy: number;
    total_methanol_tpy: number;
    total_gross_revenue_usd_per_year: number;
    average_lcom_usd_ton: number | null;
    high_priority_evidence_count: number;
  };
  candidates: ValidationCandidatePack[];
  comparison_axes: ValidationComparisonAxis[];
  committee_memo: CommitteeMemo;
  warnings: string[];
};
