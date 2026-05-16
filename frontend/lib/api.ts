import type { Plant } from "@/types/plant";
import type { EmissionTest } from "@/types/emission-test";
import type { FinancialAssumption, FinancialAssumptionPayload } from "@/types/financial-assumption";
import type { HydrogenStrategy, HydrogenStrategyPayload } from "@/types/hydrogen-strategy";
import type { InvestorCase } from "@/types/investor";
import type { LlmGeneratePayload, LlmInsight } from "@/types/llm";
import type { DocumentAskPayload, ProjectDocument } from "@/types/document";
import type {
  PreFeedPackage,
  PreFeedPackageDocument,
  PreFeedPackageDocumentPayload,
  PreFeedPackageGap,
  PreFeedPackagePayload,
  PreFeedPackageUpdatePayload,
} from "@/types/prefeed";
import type {
  PreFeedActiveCostBasis,
  PreFeedActiveCostBasisPayload,
  PreFeedCostItem,
  PreFeedCostItemPayload,
  PreFeedCostSummary,
  PreFeedVendorComparison,
  PreFeedVendorGap,
  PreFeedVendorProposal,
  PreFeedVendorProposalPayload,
} from "@/types/prefeed-cost";
import type {
  PreFeedDecisionDashboard,
  PreFeedDecisionGate,
  PreFeedDecisionGatePayload,
  PreFeedDecisionGateSummary,
  PreFeedDecisionNextAction,
  PreFeedDecisionBlocker,
  PreFeedRisk,
  PreFeedRiskPayload,
  PreFeedRiskSummary,
} from "@/types/prefeed-decision";
import type {
  PreFeedGap,
  PreFeedMrvAssumption,
  PreFeedMrvAssumptionPayload,
  PreFeedMrvSummary,
  PreFeedOfftakeProspect,
  PreFeedOfftakeProspectPayload,
  PreFeedOfftakeSummary,
  PreFeedPriceDeck,
  PreFeedPriceDeckPayload,
} from "@/types/prefeed-market";
import type { BusinessScenario, BusinessScenarioPayload, BusinessScenarioUpdatePayload } from "@/types/scenario";
import type { ScenarioResult } from "@/types/scenario-result";
import type { SensitivityResult, SensitivityRunResponse, SensitivityVariable } from "@/types/sensitivity";
import type { ApplicationSetting, ApplicationSettingPayload, DataQualitySummary } from "@/types/settings";
import type {
  ScoringRecalculateResponse,
  UnitOpportunityGeoJSON,
  UnitProfile,
  UnitRankingRow,
} from "@/types/scoring";
import type { SiteReadiness, SiteReadinessPayload } from "@/types/site-readiness";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body && !isFormData ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let message = "API request failed";
    try {
      const errorPayload = (await response.json()) as { detail?: unknown };
      if (typeof errorPayload.detail === "string") {
        message = errorPayload.detail;
      }
    } catch {
      // Keep the generic message when the backend did not return JSON.
    }
    throw new Error(message);
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

function buildQuery(params: Record<string, string | undefined | null>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value && value !== "all") {
      query.set(key, value);
    }
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function recalculateScoring(params: {
  scenarioId?: string;
  scheme?: string;
}): Promise<ScoringRecalculateResponse> {
  return apiFetch<ScoringRecalculateResponse>("/scoring/recalculate", {
    method: "POST",
    body: JSON.stringify({
      scenario_id: params.scenarioId || null,
      scheme: params.scheme && params.scheme !== "all" ? params.scheme : null,
    }),
  });
}

export async function getUnitRanking(params: {
  scenarioId?: string;
  scheme?: string;
  region?: string;
  fuelType?: string;
  confidence?: string;
  opportunityLevel?: string;
} = {}): Promise<UnitRankingRow[]> {
  return apiFetch<UnitRankingRow[]>(
    `/scoring/unit-ranking${buildQuery({
      scenario_id: params.scenarioId,
      scheme: params.scheme,
      region: params.region,
      fuel_type: params.fuelType,
      confidence: params.confidence,
      opportunity_level: params.opportunityLevel,
    })}`,
  );
}

export async function getUnitOpportunityGeoJSON(params: {
  scenarioId?: string;
  scheme?: string;
  region?: string;
  fuelType?: string;
  confidence?: string;
  opportunityLevel?: string;
} = {}): Promise<UnitOpportunityGeoJSON> {
  return apiFetch<UnitOpportunityGeoJSON>(
    `/map/unit-opportunity${buildQuery({
      scenario_id: params.scenarioId,
      scheme: params.scheme,
      region: params.region,
      fuel_type: params.fuelType,
      confidence: params.confidence,
      opportunity_level: params.opportunityLevel,
    })}`,
  );
}

export async function getUnitProfile(plantId: string, scenarioId?: string): Promise<UnitProfile> {
  return apiFetch<UnitProfile>(
    `/units/${plantId}/profile${buildQuery({
      scenario_id: scenarioId,
    })}`,
  );
}

export async function runSensitivity(params: {
  scenarioId: string;
  plantId?: string;
  variables?: SensitivityVariable[];
}): Promise<SensitivityRunResponse> {
  return apiFetch<SensitivityRunResponse>("/sensitivity/run", {
    method: "POST",
    body: JSON.stringify({
      scenario_id: params.scenarioId,
      plant_id: params.plantId || null,
      variables: params.variables || null,
    }),
  });
}

export async function getScenarioSensitivity(
  scenarioId: string,
  plantId?: string,
): Promise<SensitivityResult[]> {
  return apiFetch<SensitivityResult[]>(
    `/scenarios/${scenarioId}/sensitivity${buildQuery({
      plant_id: plantId,
    })}`,
  );
}

export async function getInvestorCase(params: {
  plantId?: string;
  scenarioId?: string;
} = {}): Promise<InvestorCase> {
  return apiFetch<InvestorCase>(
    `/investor-case${buildQuery({
      plant_id: params.plantId,
      scenario_id: params.scenarioId,
    })}`,
  );
}

export async function getSettings(category?: string): Promise<ApplicationSetting[]> {
  return apiFetch<ApplicationSetting[]>(
    `/settings${buildQuery({
      category,
    })}`,
  );
}

export async function updateSetting(key: string, payload: ApplicationSettingPayload): Promise<ApplicationSetting> {
  return apiFetch<ApplicationSetting>(`/settings/${key}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function getDataQualitySummary(params: {
  plantId: string;
  scenarioId?: string;
}): Promise<DataQualitySummary> {
  return apiFetch<DataQualitySummary>(
    `/data-quality/summary${buildQuery({
      plant_id: params.plantId,
      scenario_id: params.scenarioId,
    })}`,
  );
}

export async function getLlmInsights(params: {
  scenarioId?: string;
  plantId?: string;
  documentId?: string;
  insightType?: string;
} = {}): Promise<LlmInsight[]> {
  return apiFetch<LlmInsight[]>(
    `/llm/insights${buildQuery({
      scenario_id: params.scenarioId,
      plant_id: params.plantId,
      document_id: params.documentId,
      insight_type: params.insightType,
    })}`,
  );
}

async function generateLlmInsight(path: string, payload: LlmGeneratePayload = {}): Promise<LlmInsight> {
  return apiFetch<LlmInsight>(path, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function generateExecutiveSummary(
  scenarioId: string,
  payload: LlmGeneratePayload = {},
): Promise<LlmInsight> {
  return generateLlmInsight(`/llm/summary/${scenarioId}`, payload);
}

export async function generateInvestorMemo(
  scenarioId: string,
  payload: LlmGeneratePayload = {},
): Promise<LlmInsight> {
  return generateLlmInsight(`/llm/investor-memo/${scenarioId}`, payload);
}

export async function generateDataGapExplanation(params: {
  plantId: string;
  scenarioId?: string;
  payload?: LlmGeneratePayload;
}): Promise<LlmInsight> {
  return generateLlmInsight(
    `/llm/data-gap/${params.plantId}${buildQuery({
      scenario_id: params.scenarioId,
    })}`,
    params.payload,
  );
}

export async function generateSensitivityExplanation(
  scenarioId: string,
  payload: LlmGeneratePayload = {},
): Promise<LlmInsight> {
  return generateLlmInsight(`/llm/explain-sensitivity/${scenarioId}`, payload);
}

export async function getDocuments(params: {
  plantId?: string;
  scenarioId?: string;
} = {}): Promise<ProjectDocument[]> {
  return apiFetch<ProjectDocument[]>(
    `/documents${buildQuery({
      plant_id: params.plantId,
      scenario_id: params.scenarioId,
    })}`,
  );
}

export async function getDocument(documentId: string): Promise<ProjectDocument> {
  return apiFetch<ProjectDocument>(`/documents/${documentId}`);
}

export async function uploadDocument(payload: {
  file: File;
  plantId?: string;
  scenarioId?: string;
  documentCategory?: string;
}): Promise<ProjectDocument> {
  const formData = new FormData();
  formData.set("file", payload.file);
  if (payload.plantId) {
    formData.set("plant_id", payload.plantId);
  }
  if (payload.scenarioId) {
    formData.set("scenario_id", payload.scenarioId);
  }
  if (payload.documentCategory) {
    formData.set("document_category", payload.documentCategory);
  }
  return apiFetch<ProjectDocument>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function extractDocument(documentId: string): Promise<ProjectDocument> {
  return apiFetch<ProjectDocument>(`/documents/${documentId}/extract`, {
    method: "POST",
  });
}

export async function askDocument(documentId: string, payload: DocumentAskPayload): Promise<LlmInsight> {
  return apiFetch<LlmInsight>(`/documents/${documentId}/ask`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listPreFeedPackages(params: {
  plantId?: string;
  scenarioId?: string;
  includeArchived?: boolean;
} = {}): Promise<PreFeedPackage[]> {
  return apiFetch<PreFeedPackage[]>(
    `/prefeed/packages${buildQuery({
      plant_id: params.plantId,
      scenario_id: params.scenarioId,
      include_archived: params.includeArchived ? "true" : undefined,
    })}`,
  );
}

export async function getPreFeedPackage(packageId: string): Promise<PreFeedPackage> {
  return apiFetch<PreFeedPackage>(`/prefeed/packages/${packageId}`);
}

export async function createPreFeedPackage(payload: PreFeedPackagePayload): Promise<PreFeedPackage> {
  return apiFetch<PreFeedPackage>("/prefeed/packages", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedPackage(
  packageId: string,
  payload: PreFeedPackageUpdatePayload,
): Promise<PreFeedPackage> {
  return apiFetch<PreFeedPackage>(`/prefeed/packages/${packageId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function archivePreFeedPackage(packageId: string): Promise<PreFeedPackage> {
  return apiFetch<PreFeedPackage>(`/prefeed/packages/${packageId}/archive`, {
    method: "POST",
  });
}

export async function listPreFeedPackageDocuments(packageId: string): Promise<PreFeedPackageDocument[]> {
  return apiFetch<PreFeedPackageDocument[]>(`/prefeed/packages/${packageId}/documents`);
}

export async function linkPreFeedPackageDocument(
  packageId: string,
  payload: PreFeedPackageDocumentPayload,
): Promise<PreFeedPackageDocument> {
  return apiFetch<PreFeedPackageDocument>(`/prefeed/packages/${packageId}/documents`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function unlinkPreFeedPackageDocument(packageId: string, linkId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/packages/${packageId}/documents/${linkId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedPackageGaps(packageId: string): Promise<PreFeedPackageGap[]> {
  return apiFetch<PreFeedPackageGap[]>(`/prefeed/packages/${packageId}/gaps`);
}

export async function listPreFeedCostItems(params: {
  packageId: string;
  vendorProposalId?: string;
}): Promise<PreFeedCostItem[]> {
  return apiFetch<PreFeedCostItem[]>(
    `/prefeed/packages/${params.packageId}/cost-items${buildQuery({
      vendor_proposal_id: params.vendorProposalId,
    })}`,
  );
}

export async function createPreFeedCostItem(
  packageId: string,
  payload: PreFeedCostItemPayload,
): Promise<PreFeedCostItem> {
  return apiFetch<PreFeedCostItem>(`/prefeed/packages/${packageId}/cost-items`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedCostItem(
  costItemId: string,
  payload: Partial<PreFeedCostItemPayload>,
): Promise<PreFeedCostItem> {
  return apiFetch<PreFeedCostItem>(`/prefeed/cost-items/${costItemId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletePreFeedCostItem(costItemId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/cost-items/${costItemId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedCostSummary(params: {
  packageId: string;
  vendorProposalId?: string;
}): Promise<PreFeedCostSummary> {
  return apiFetch<PreFeedCostSummary>(
    `/prefeed/packages/${params.packageId}/cost-summary${buildQuery({
      vendor_proposal_id: params.vendorProposalId,
    })}`,
  );
}

export async function listPreFeedVendorProposals(packageId: string): Promise<PreFeedVendorProposal[]> {
  return apiFetch<PreFeedVendorProposal[]>(`/prefeed/packages/${packageId}/vendor-proposals`);
}

export async function createPreFeedVendorProposal(
  packageId: string,
  payload: PreFeedVendorProposalPayload,
): Promise<PreFeedVendorProposal> {
  return apiFetch<PreFeedVendorProposal>(`/prefeed/packages/${packageId}/vendor-proposals`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedVendorProposal(
  proposalId: string,
  payload: Partial<PreFeedVendorProposalPayload>,
): Promise<PreFeedVendorProposal> {
  return apiFetch<PreFeedVendorProposal>(`/prefeed/vendor-proposals/${proposalId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletePreFeedVendorProposal(proposalId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/vendor-proposals/${proposalId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedVendorComparison(packageId: string): Promise<PreFeedVendorComparison[]> {
  return apiFetch<PreFeedVendorComparison[]>(`/prefeed/packages/${packageId}/vendor-comparison`);
}

export async function getPreFeedVendorGaps(proposalId: string): Promise<PreFeedVendorGap[]> {
  return apiFetch<PreFeedVendorGap[]>(`/prefeed/vendor-proposals/${proposalId}/gaps`);
}

export async function getPreFeedActiveCostBasis(scenarioId: string): Promise<PreFeedActiveCostBasis | null> {
  return apiFetch<PreFeedActiveCostBasis | null>(`/prefeed/scenarios/${scenarioId}/active-cost-basis`);
}

export async function selectPreFeedActiveCostBasis(
  scenarioId: string,
  payload: PreFeedActiveCostBasisPayload,
): Promise<PreFeedActiveCostBasis> {
  return apiFetch<PreFeedActiveCostBasis>(`/prefeed/scenarios/${scenarioId}/active-cost-basis`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listPreFeedPriceDecks(packageId: string): Promise<PreFeedPriceDeck[]> {
  return apiFetch<PreFeedPriceDeck[]>(`/prefeed/packages/${packageId}/price-decks`);
}

export async function createPreFeedPriceDeck(
  packageId: string,
  payload: PreFeedPriceDeckPayload,
): Promise<PreFeedPriceDeck> {
  return apiFetch<PreFeedPriceDeck>(`/prefeed/packages/${packageId}/price-decks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedPriceDeck(
  deckId: string,
  payload: Partial<PreFeedPriceDeckPayload>,
): Promise<PreFeedPriceDeck> {
  return apiFetch<PreFeedPriceDeck>(`/prefeed/price-decks/${deckId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function activatePreFeedPriceDeck(deckId: string): Promise<PreFeedPriceDeck> {
  return apiFetch<PreFeedPriceDeck>(`/prefeed/price-decks/${deckId}/activate`, {
    method: "POST",
  });
}

export async function deletePreFeedPriceDeck(deckId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/price-decks/${deckId}`, {
    method: "DELETE",
  });
}

export async function listPreFeedOfftakeProspects(packageId: string): Promise<PreFeedOfftakeProspect[]> {
  return apiFetch<PreFeedOfftakeProspect[]>(`/prefeed/packages/${packageId}/offtake-prospects`);
}

export async function createPreFeedOfftakeProspect(
  packageId: string,
  payload: PreFeedOfftakeProspectPayload,
): Promise<PreFeedOfftakeProspect> {
  return apiFetch<PreFeedOfftakeProspect>(`/prefeed/packages/${packageId}/offtake-prospects`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedOfftakeProspect(
  prospectId: string,
  payload: Partial<PreFeedOfftakeProspectPayload>,
): Promise<PreFeedOfftakeProspect> {
  return apiFetch<PreFeedOfftakeProspect>(`/prefeed/offtake-prospects/${prospectId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletePreFeedOfftakeProspect(prospectId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/offtake-prospects/${prospectId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedOfftakeSummary(packageId: string): Promise<PreFeedOfftakeSummary> {
  return apiFetch<PreFeedOfftakeSummary>(`/prefeed/packages/${packageId}/offtake-summary`);
}

export async function getPreFeedOfftakeGaps(packageId: string): Promise<PreFeedGap[]> {
  return apiFetch<PreFeedGap[]>(`/prefeed/packages/${packageId}/offtake-gaps`);
}

export async function listPreFeedMrvAssumptions(packageId: string): Promise<PreFeedMrvAssumption[]> {
  return apiFetch<PreFeedMrvAssumption[]>(`/prefeed/packages/${packageId}/mrv-assumptions`);
}

export async function createPreFeedMrvAssumption(
  packageId: string,
  payload: PreFeedMrvAssumptionPayload,
): Promise<PreFeedMrvAssumption> {
  return apiFetch<PreFeedMrvAssumption>(`/prefeed/packages/${packageId}/mrv-assumptions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedMrvAssumption(
  assumptionId: string,
  payload: Partial<PreFeedMrvAssumptionPayload>,
): Promise<PreFeedMrvAssumption> {
  return apiFetch<PreFeedMrvAssumption>(`/prefeed/mrv-assumptions/${assumptionId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletePreFeedMrvAssumption(assumptionId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/mrv-assumptions/${assumptionId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedMrvSummary(packageId: string): Promise<PreFeedMrvSummary> {
  return apiFetch<PreFeedMrvSummary>(`/prefeed/packages/${packageId}/mrv-summary`);
}

export async function getPreFeedMrvGaps(packageId: string): Promise<PreFeedGap[]> {
  return apiFetch<PreFeedGap[]>(`/prefeed/packages/${packageId}/mrv-gaps`);
}

export async function listPreFeedRisks(packageId: string): Promise<PreFeedRisk[]> {
  return apiFetch<PreFeedRisk[]>(`/prefeed/packages/${packageId}/risks`);
}

export async function createPreFeedRisk(
  packageId: string,
  payload: PreFeedRiskPayload,
): Promise<PreFeedRisk> {
  return apiFetch<PreFeedRisk>(`/prefeed/packages/${packageId}/risks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedRisk(
  riskId: string,
  payload: Partial<PreFeedRiskPayload>,
): Promise<PreFeedRisk> {
  return apiFetch<PreFeedRisk>(`/prefeed/risks/${riskId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletePreFeedRisk(riskId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/risks/${riskId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedRiskSummary(packageId: string): Promise<PreFeedRiskSummary> {
  return apiFetch<PreFeedRiskSummary>(`/prefeed/packages/${packageId}/risk-summary`);
}

export async function listPreFeedDecisionGates(packageId: string): Promise<PreFeedDecisionGate[]> {
  return apiFetch<PreFeedDecisionGate[]>(`/prefeed/packages/${packageId}/decision-gates`);
}

export async function createPreFeedDecisionGate(
  packageId: string,
  payload: PreFeedDecisionGatePayload,
): Promise<PreFeedDecisionGate> {
  return apiFetch<PreFeedDecisionGate>(`/prefeed/packages/${packageId}/decision-gates`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePreFeedDecisionGate(
  gateId: string,
  payload: Partial<PreFeedDecisionGatePayload>,
): Promise<PreFeedDecisionGate> {
  return apiFetch<PreFeedDecisionGate>(`/prefeed/decision-gates/${gateId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletePreFeedDecisionGate(gateId: string): Promise<void> {
  return apiFetch<void>(`/prefeed/decision-gates/${gateId}`, {
    method: "DELETE",
  });
}

export async function getPreFeedDecisionGateSummary(packageId: string): Promise<PreFeedDecisionGateSummary> {
  return apiFetch<PreFeedDecisionGateSummary>(`/prefeed/packages/${packageId}/decision-gate-summary`);
}

export async function getPreFeedDecisionBlockers(packageId: string): Promise<PreFeedDecisionBlocker[]> {
  return apiFetch<PreFeedDecisionBlocker[]>(`/prefeed/packages/${packageId}/decision-blockers`);
}

export async function getPreFeedDecisionNextActions(packageId: string): Promise<PreFeedDecisionNextAction[]> {
  return apiFetch<PreFeedDecisionNextAction[]>(`/prefeed/packages/${packageId}/decision-next-actions`);
}

export async function getPreFeedDecisionDashboard(packageId: string): Promise<PreFeedDecisionDashboard> {
  return apiFetch<PreFeedDecisionDashboard>(`/prefeed/packages/${packageId}/decision-dashboard`);
}

export async function generatePreFeedCommitteeBrief(
  packageId: string,
  payload: LlmGeneratePayload = {},
): Promise<LlmInsight> {
  return generateLlmInsight(`/prefeed/packages/${packageId}/committee-brief`, payload);
}
