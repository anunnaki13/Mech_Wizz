import type { BusinessScenario } from "@/types/scenario";

export type OpportunityLevel = "low" | "medium" | "high" | "priority";

export type UnitScoringResult = {
  id: string;
  plant_id: string;
  scenario_id: string;
  scenario_result_id: string;
  scoring_run_id: string;
  opportunity_score: number;
  readiness_score: number;
  confidence_score: number;
  composite_score: number;
  co2_availability_score: number;
  methanol_potential_score: number;
  h2_readiness_score: number;
  economic_return_score: number;
  infrastructure_score: number;
  land_port_score: number;
  market_access_score: number;
  risk_permit_score: number;
  data_completeness_score: number;
  emission_data_quality_score: number;
  land_readiness_score: number;
  utility_readiness_score: number;
  h2_strategy_clarity_score: number;
  permit_logistic_readiness_score: number;
  carbon_credit_potential_score: number;
  strategic_value_score: number;
  utility_advantage_score: number;
  component_scores: Record<string, unknown>;
  data_gap_count: number;
  rank_position: number | null;
  recommended_scheme: string;
  key_bottleneck: string;
  scoring_version: string;
  created_at: string;
};

export type ScoringRecalculateResponse = {
  scoring_run_id: string | null;
  created_count: number;
  results: UnitScoringResult[];
};

export type UnitRankingRow = {
  rank: number;
  plant_id: string;
  site_id: string;
  scenario_id: string;
  scenario_result_id: string;
  scoring_result_id: string;
  scenario_name: string;
  scheme: string;
  site_name: string;
  unit_name: string;
  province: string | null;
  city: string | null;
  latitude: number | null;
  longitude: number | null;
  capacity_mw: number | null;
  fuel_type: string | null;
  composite_score: number;
  opportunity_score: number;
  readiness_score: number;
  confidence_score: number;
  heatmap_weight: number;
  co2_tpy: number | null;
  captured_co2_tpy: number | null;
  methanol_tpy: number | null;
  h2_required_tpy: number | null;
  estimated_irr: number | null;
  estimated_lcom_usd_ton: number | null;
  recommended_scheme: string;
  key_bottleneck: string;
  data_gap_count: number;
  data_confidence_label: string;
  opportunity_level: OpportunityLevel;
  calculation_version: string;
};

export type UnitOpportunityFeature = {
  type: "Feature";
  id: string;
  geometry: {
    type: "Point";
    coordinates: [number, number];
  };
  properties: {
    site_id: string;
    site_name: string;
    unit_name: string;
    province: string | null;
    city: string | null;
    capacity_mw: number | null;
    fuel_type: string | null;
    scenario_id: string;
    scenario_name: string;
    scheme: string;
    opportunity_score: number;
    readiness_score: number;
    confidence_score: number;
    composite_score: number;
    co2_tpy: number | null;
    captured_co2_tpy: number | null;
    methanol_tpy: number | null;
    h2_required_tpy: number | null;
    estimated_irr: number | null;
    estimated_lcom_usd_ton: number | null;
    rank_position: number;
    data_confidence_label: string;
    heatmap_weight: number;
    recommended_scheme: string;
    key_bottleneck: string;
    data_gap_count: number;
    opportunity_level: OpportunityLevel;
    status: string;
  };
};

export type UnitOpportunityGeoJSON = {
  type: "FeatureCollection";
  features: UnitOpportunityFeature[];
};

export type UnitProfile = {
  plant: Record<string, unknown>;
  scenario: Partial<BusinessScenario> | null;
  latest_result: Record<string, unknown> | null;
  latest_scoring: Record<string, unknown> | null;
  score_breakdown: Record<string, unknown>;
  data_gaps: Array<{
    module: string;
    name: string;
    impact: string;
    priority: string;
  }>;
  confidence_labels: Record<string, string>;
};

export type DashboardFilters = {
  scenarioId: string;
  scheme: string;
  region: string;
  fuelType: string;
  confidence: string;
  opportunityLevel: string;
  showHeatmap: boolean;
  showMarkers: boolean;
  showLabels: boolean;
};
