import type { Plant } from "@/types/plant";
import type { EmissionTest } from "@/types/emission-test";

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
