import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type ApplicationSetting = {
  id: string;
  key: string;
  category: string;
  value: Record<string, unknown>;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
  updated_at: string;
};

export type ApplicationSettingPayload = {
  value: Record<string, unknown>;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
};

export type DataGap = {
  id: string;
  plant_id: string;
  scenario_id: string | null;
  source_module: string;
  missing_data_name: string;
  impact_level: string;
  priority_level: string;
  recommendation: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type DataQualitySummary = {
  plant_id: string;
  scenario_id: string | null;
  input_status: Record<string, string>;
  output_confidence: Record<string, string>;
  gaps: DataGap[];
};
