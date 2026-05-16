import type { Plant } from "@/types/plant";
import type { EmissionTest } from "@/types/emission-test";
import type { FinancialAssumption, FinancialAssumptionPayload } from "@/types/financial-assumption";
import type { HydrogenStrategy, HydrogenStrategyPayload } from "@/types/hydrogen-strategy";
import type { BusinessScenario, BusinessScenarioPayload, BusinessScenarioUpdatePayload } from "@/types/scenario";
import type { ScenarioResult } from "@/types/scenario-result";
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

export async function getPlantScenarios(plantId: string): Promise<BusinessScenario[]> {
  return apiFetch<BusinessScenario[]>(`/plants/${plantId}/scenarios`);
}

export async function createScenario(
  plantId: string,
  payload: BusinessScenarioPayload,
): Promise<BusinessScenario> {
  return apiFetch<BusinessScenario>(`/plants/${plantId}/scenarios`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateScenario(
  scenarioId: string,
  payload: BusinessScenarioUpdatePayload,
): Promise<BusinessScenario> {
  return apiFetch<BusinessScenario>(`/scenarios/${scenarioId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteScenario(scenarioId: string): Promise<void> {
  return apiFetch<void>(`/scenarios/${scenarioId}`, {
    method: "DELETE",
  });
}

export async function getFinancialAssumption(scenarioId: string): Promise<FinancialAssumption | null> {
  return apiFetch<FinancialAssumption | null>(`/scenarios/${scenarioId}/financial-assumptions`);
}

export async function saveFinancialAssumption(
  scenarioId: string,
  payload: FinancialAssumptionPayload,
): Promise<FinancialAssumption> {
  return apiFetch<FinancialAssumption>(`/scenarios/${scenarioId}/financial-assumptions`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function runScenarioSimulation(scenarioId: string): Promise<ScenarioResult> {
  return apiFetch<ScenarioResult>(`/scenarios/${scenarioId}/simulate`, {
    method: "POST",
  });
}

export async function getScenarioResults(scenarioId: string): Promise<ScenarioResult[]> {
  return apiFetch<ScenarioResult[]>(`/scenarios/${scenarioId}/results`);
}

export async function getScenarioResult(resultId: string): Promise<ScenarioResult> {
  return apiFetch<ScenarioResult>(`/scenario-results/${resultId}`);
}
