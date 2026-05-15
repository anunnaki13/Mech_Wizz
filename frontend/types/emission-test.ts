import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type EmissionTest = {
  id: string;
  plant_id: string;
  stack_id: string;
  test_date: string | null;
  lab_name: string | null;
  stack_diameter_m: number | null;
  gas_velocity_m_s: number | null;
  flue_gas_temperature_c: number | null;
  co2_percent_dry: number | null;
  o2_percent: number | null;
  moisture_percent: number | null;
  so2_mg_nm3: number | null;
  nox_mg_nm3: number | null;
  particulate_mg_nm3: number | null;
  hg_mg_nm3: number | null;
  compliance_status: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
};
