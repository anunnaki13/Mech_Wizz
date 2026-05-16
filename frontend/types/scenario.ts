import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type BusinessScheme = "access" | "align" | "augment";

export type BusinessScenario = {
  id: string;
  plant_id: string;
  scenario_name: string;
  scheme: BusinessScheme;
  pln_ownership_percent: number | null;
  partner_capex_responsibility_percent: number | null;
  pln_capex_responsibility_percent: number | null;
  revenue_model: string | null;
  capture_rate: number | null;
  process_efficiency: number | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
  updated_at: string;
};

export type BusinessScenarioPayload = {
  scenario_name: string;
  scheme: BusinessScheme;
  pln_ownership_percent: number | null;
  partner_capex_responsibility_percent: number | null;
  pln_capex_responsibility_percent: number | null;
  revenue_model: string | null;
  capture_rate: number | null;
  process_efficiency: number | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
};

export type BusinessScenarioUpdatePayload = Partial<BusinessScenarioPayload>;
