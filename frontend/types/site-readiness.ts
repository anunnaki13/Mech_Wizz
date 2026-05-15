import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type SiteReadiness = {
  id: string;
  plant_id: string;
  available_land_ha: number | null;
  land_status: string | null;
  distance_to_stack_km: number | null;
  has_port_or_jetty: boolean | null;
  distance_to_port_km: number | null;
  port_capacity_dwt: number | null;
  road_access: string | null;
  water_availability: string | null;
  power_availability: string | null;
  utility_readiness: string | null;
  permit_risk: string | null;
  social_risk: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
};

export type SiteReadinessPayload = Partial<Omit<SiteReadiness, "id" | "plant_id" | "created_at">>;
