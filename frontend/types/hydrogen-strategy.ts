import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type HydrogenStrategy = {
  id: string;
  plant_id: string;
  existing_h2_available: boolean | null;
  h2_strategy: string | null;
  h2_cost_case: string | null;
  h2_cost_usd_per_kg: number | null;
  h2_readiness_score: number | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
};

export type HydrogenStrategyPayload = Partial<Omit<HydrogenStrategy, "id" | "plant_id" | "created_at">>;
