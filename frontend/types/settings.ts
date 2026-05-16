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

export type OpenRouterSettings = {
  has_api_key: boolean;
  api_key_masked: string | null;
  api_key_source: "stored" | "environment" | "missing" | string;
  base_url: string;
  model: string;
  site_url: string;
  app_name: string;
};

export type OpenRouterSettingsPayload = {
  api_key?: string | null;
  clear_api_key?: boolean;
  base_url?: string | null;
  model?: string | null;
  site_url?: string | null;
  app_name?: string | null;
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
