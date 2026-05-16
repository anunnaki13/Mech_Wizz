export type InvestorCase = {
  plant: Record<string, unknown>;
  scenario: Record<string, unknown>;
  kpis: {
    project_irr: number | null;
    estimated_npv_usd: number | null;
    lcom_usd_per_ton: number | null;
    payback_years: number | null;
    e_methanol_capacity_tpy: number | null;
    co2_abatement_tpy: number | null;
    total_co2_tpy: number | null;
    composite_score: number | null;
    opportunity_score: number | null;
    readiness_score: number | null;
    confidence_score: number | null;
    rank_position: number | null;
  };
  capex_structure: {
    total_capex_usd: number | null;
    components: Array<{
      key: string;
      label: string;
      amount_usd: number | null;
      data_status: string;
    }>;
    pln_responsibility_percent: number | null;
    partner_responsibility_percent: number | null;
    model: string;
    is_complete: boolean;
  };
  revenue_mix: Array<{
    label: string;
    value_usd_per_year: number | null;
    share: number | null;
  }>;
  scenario_comparison: Array<{
    scheme: string;
    scenario_id: string | null;
    scenario_name: string | null;
    available: boolean;
    irr: number | null;
    npv_usd: number | null;
    lcom_usd_per_ton: number | null;
    payback_years: number | null;
    composite_score: number | null;
    confidence_level: string;
  }>;
  thesis_flow: Array<{
    section: string;
    stage: string;
    summary: string;
  }>;
  risks: Array<{
    risk: string;
    impact: string;
    priority: string;
    mitigation: string;
    source: string;
  }>;
  roadmap: Array<{
    step: string;
    title: string;
    description: string;
  }>;
  why_this_wins: string[];
  data_gaps: Array<{
    module: string;
    name: string;
    missing_data: string;
    impact: string;
    priority: string;
    recommendation: string;
    status: string;
  }>;
  sensitivity: {
    run_id: string;
    dominant_driver: string;
    impact_score: number;
    confidence_level: string;
  } | null;
  confidence_level: "high" | "medium" | "low" | "unknown";
  warnings: string[];
  data_quality: Record<string, unknown>;
};
