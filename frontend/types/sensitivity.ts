export type SensitivityVariable =
  | "h2_price"
  | "electricity_price"
  | "methanol_price"
  | "capex"
  | "capture_rate"
  | "plant_availability"
  | "carbon_credit_price"
  | "exchange_rate";

export type SensitivityResult = {
  id: string;
  run_id: string;
  plant_id: string;
  scenario_id: string;
  scenario_result_id: string | null;
  variable_name: SensitivityVariable | string;
  low_input_value: number | null;
  base_input_value: number | null;
  high_input_value: number | null;
  low_irr: number | null;
  base_irr: number | null;
  high_irr: number | null;
  low_npv_usd: number | null;
  base_npv_usd: number | null;
  high_npv_usd: number | null;
  low_lcom_usd_per_ton: number | null;
  base_lcom_usd_per_ton: number | null;
  high_lcom_usd_per_ton: number | null;
  impact_score: number;
  missing_inputs: string[];
  warnings: string[];
  assumption_snapshot: Record<string, unknown>;
  confidence_level: "high" | "medium" | "low" | "unknown";
  created_at: string;
};

export type SensitivityRunResponse = {
  run_id: string;
  plant_id: string;
  scenario_id: string;
  scenario_result_id: string | null;
  results: SensitivityResult[];
};
