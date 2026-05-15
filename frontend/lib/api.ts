import type { Plant } from "@/types/plant";
import type { EmissionTest } from "@/types/emission-test";
import type { HydrogenStrategy, HydrogenStrategyPayload } from "@/types/hydrogen-strategy";
import type { SiteReadiness, SiteReadinessPayload } from "@/types/site-readiness";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("API request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getPlants(): Promise<Plant[]> {
  return apiFetch<Plant[]>("/plants/");
}

export async function getPlant(id: string): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}`);
}

export async function getEmissionTests(plantId: string): Promise<EmissionTest[]> {
  return apiFetch<EmissionTest[]>(`/plants/${plantId}/emission-tests`);
}

export async function createEmissionTest(
  plantId: string,
  payload: Partial<EmissionTest>,
): Promise<EmissionTest> {
  return apiFetch<EmissionTest>(`/plants/${plantId}/emission-tests`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getSiteReadiness(plantId: string): Promise<SiteReadiness | null> {
  return apiFetch<SiteReadiness | null>(`/plants/${plantId}/site-readiness`);
}

export async function saveSiteReadiness(
  plantId: string,
  payload: SiteReadinessPayload,
  recordId?: string,
): Promise<SiteReadiness> {
  const path = recordId ? `/site-readiness/${recordId}` : `/plants/${plantId}/site-readiness`;
  return apiFetch<SiteReadiness>(path, {
    method: recordId ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });
}

export async function getHydrogenStrategy(plantId: string): Promise<HydrogenStrategy | null> {
  return apiFetch<HydrogenStrategy | null>(`/plants/${plantId}/hydrogen-strategy`);
}

export async function saveHydrogenStrategy(
  plantId: string,
  payload: HydrogenStrategyPayload,
  recordId?: string,
): Promise<HydrogenStrategy> {
  const path = recordId ? `/hydrogen-strategy/${recordId}` : `/plants/${plantId}/hydrogen-strategy`;
  return apiFetch<HydrogenStrategy>(path, {
    method: recordId ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });
}
