export type DataStatus = "actual" | "estimated" | "benchmark" | "user_assumption" | "unknown" | "partner_supplied";
export type ConfidenceLevel = "high" | "medium" | "low" | "unknown";

export type Plant = {
  id: string;
  plant_name: string;
  unit_name: string;
  province: string | null;
  city: string | null;
  latitude: number | null;
  longitude: number | null;
  capacity_mw: number | null;
  fuel_type: string | null;
  status: string | null;
  capacity_factor: number | null;
  operating_days_per_year: number | null;
  owner: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  created_at: string;
  updated_at: string;
};

export type PlantPayload = {
  plant_name: string;
  unit_name: string;
  province?: string | null;
  city?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  capacity_mw?: number | null;
  fuel_type?: string | null;
  status?: string | null;
  capacity_factor?: number | null;
  operating_days_per_year?: number | null;
  owner?: string | null;
  data_status?: DataStatus;
  confidence_level?: ConfidenceLevel;
};
