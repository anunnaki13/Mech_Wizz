import type { ConfidenceLevel } from "@/types/plant";

export type ScenarioResult = {
  id: string;
  scenario_id: string;
  total_co2_ton_per_year: number | null;
  captured_co2_ton_per_year: number | null;
  vented_co2_ton_per_year: number | null;
  methanol_ton_per_year: number | null;
  h2_required_ton_per_year: number | null;
  electrolyzer_required_mw: number | null;
  gross_revenue_usd_per_year: number | null;
  lcom_usd_per_ton: number | null;
  npv_usd: number | null;
  irr: number | null;
  payback_years: number | null;
  missing_inputs: string[];
  assumption_snapshot: Record<string, unknown>;
  calculation_version: string;
  confidence_level: ConfidenceLevel;
  created_at: string;
};
