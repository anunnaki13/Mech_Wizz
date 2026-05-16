export type InsightType =
  | "executive_summary"
  | "data_gap_explanation"
  | "investor_memo"
  | "sensitivity_explanation"
  | "document_qa"
  | "prefeed_committee_brief";

export type LlmInsight = {
  id: string;
  plant_id: string | null;
  scenario_id: string | null;
  document_id: string | null;
  insight_type: InsightType;
  model_name: string;
  prompt: string;
  response_text: string | null;
  status: string;
  error_message: string | null;
  provider_response_id: string | null;
  usage: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type LlmGeneratePayload = {
  model_name?: string | null;
};
