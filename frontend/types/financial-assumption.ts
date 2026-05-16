import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type FinancialAssumption = {
  id: string;
  scenario_id: string;
  methanol_price_usd_per_ton: number | null;
  grey_methanol_price_usd_per_ton: number | null;
  hydrogen_price_usd_per_kg: number | null;
  electricity_price_usd_per_kwh: number | null;
  carbon_credit_price_idr_per_ton: number | null;
  exchange_rate_idr_usd: number | null;
  discount_rate: number | null;
  tax_rate: number | null;
  capex_capture_usd: number | null;
  capex_electrolyzer_usd: number | null;
  capex_methanol_plant_usd: number | null;
  capex_storage_port_usd: number | null;
  opex_percent_capex: number | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
  updated_at: string;
};

export type FinancialAssumptionPayload = Partial<
  Omit<FinancialAssumption, "id" | "scenario_id" | "created_at" | "updated_at">
>;
