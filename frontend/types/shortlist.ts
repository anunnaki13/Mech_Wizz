export type ShortlistWeights = {
  screening: number;
  economics: number;
  logistics: number;
  confidence: number;
};

export type ShortlistScoreBreakdown = {
  screening_score: number;
  economics_score: number;
  logistics_score: number;
  confidence_score: number;
  final_score: number;
};

export type ShortlistCandidate = {
  shortlist_rank: number;
  recommendation: string;
  readiness_label: string;
  plant_id: string;
  scenario_id: string;
  scenario_result_id: string;
  site_name: string;
  unit_name: string;
  province: string | null;
  city: string | null;
  capacity_mw: number | null;
  screening_rank: number;
  composite_score: number;
  co2_tpy: number | null;
  captured_co2_tpy: number | null;
  methanol_tpy: number | null;
  h2_required_tpy: number | null;
  electrolyzer_required_mw: number | null;
  gross_revenue_usd_per_year: number | null;
  estimated_lcom_usd_ton: number | null;
  nearest_port_name: string | null;
  nearest_port_distance_km: number | null;
  nearest_port_readiness_score: number;
  port_proximity_score: number;
  score_breakdown: ShortlistScoreBreakdown;
  data_confidence_label: string;
  data_gap_count: number;
  key_bottleneck: string;
  decision_rationale: string[];
  next_actions: string[];
};

export type ShortlistDecisionMatrix = {
  scheme: string;
  top_n: number;
  method: string;
  weights: ShortlistWeights;
  summary: {
    candidate_count: number;
    shortlist_count: number;
    top_candidate: string | null;
    top_score: number | null;
    shortlist_captured_co2_tpy: number;
    shortlist_methanol_tpy: number;
    shortlist_gross_revenue_usd_per_year: number;
    average_shortlist_lcom_usd_ton: number | null;
  };
  candidates: ShortlistCandidate[];
  warnings: string[];
};
