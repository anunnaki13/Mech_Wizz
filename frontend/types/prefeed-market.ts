import type { ProjectDocument } from "@/types/document";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type PreFeedOfftakeProduct = "e_methanol" | "carbon_credit" | "co2_supply" | "hydrogen" | "other";
export type PreFeedOfftakeStatus = "lead" | "discussion" | "loi" | "term_sheet" | "contracted" | "signed" | "inactive";
export type PreFeedMrvVerificationStatus =
  | "not_started"
  | "method_selected"
  | "data_collected"
  | "third_party_review"
  | "verified";
export type PreFeedCarbonCreditEligibility =
  | "unknown"
  | "screening"
  | "potentially_eligible"
  | "eligible"
  | "not_eligible";

export type PreFeedPriceDeck = {
  id: string;
  package_id: string;
  scenario_id: string | null;
  deck_name: string;
  is_active: boolean;
  methanol_price_usd_per_ton: number | null;
  carbon_credit_price_usd_per_ton: number | null;
  electricity_price_usd_per_kwh: number | null;
  hydrogen_price_usd_per_kg: number | null;
  exchange_rate_idr_usd: number | null;
  escalation_percent: number | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedPriceDeckPayload = {
  scenario_id?: string | null;
  deck_name: string;
  is_active: boolean;
  methanol_price_usd_per_ton?: number | null;
  carbon_credit_price_usd_per_ton?: number | null;
  electricity_price_usd_per_kwh?: number | null;
  hydrogen_price_usd_per_kg?: number | null;
  exchange_rate_idr_usd?: number | null;
  escalation_percent?: number | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedOfftakeProspect = {
  id: string;
  package_id: string;
  supporting_document_id: string | null;
  counterparty_name: string;
  product: PreFeedOfftakeProduct;
  target_volume_tpy: number | null;
  term_years: number | null;
  pricing_basis: string | null;
  price_usd_per_ton: number | null;
  status: PreFeedOfftakeStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  supporting_document: ProjectDocument | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedOfftakeProspectPayload = {
  supporting_document_id?: string | null;
  counterparty_name: string;
  product: PreFeedOfftakeProduct;
  target_volume_tpy?: number | null;
  term_years?: number | null;
  pricing_basis?: string | null;
  price_usd_per_ton?: number | null;
  status: PreFeedOfftakeStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedGap = {
  source_module: string;
  missing_data_name: string;
  impact_level: string;
  priority_level: string;
  owner: string;
  recommendation: string;
  status: string;
  confidence_level: ConfidenceLevel;
};

export type PreFeedOfftakeSummary = {
  package_id: string;
  scenario_id: string | null;
  active_price_deck_id: string | null;
  prospect_count: number;
  methanol_volume_committed_tpy: number;
  methanol_volume_coverage: number | null;
  methanol_revenue_usd_per_year: number | null;
  carbon_credit_revenue_usd_per_year: number | null;
  gross_revenue_usd_per_year: number | null;
  readiness_score: number;
  readiness_components: Record<string, number>;
  scenario_ready_assumptions: Record<string, unknown>;
  warnings: string[];
};

export type PreFeedMrvAssumption = {
  id: string;
  package_id: string;
  supporting_document_id: string | null;
  baseline_emissions_tco2e_per_year: number | null;
  captured_co2_accounting_tpy: number | null;
  product_carbon_intensity_tco2e_per_ton: number | null;
  electricity_source: string | null;
  electricity_emission_factor_tco2e_per_mwh: number | null;
  methanol_pathway: string | null;
  carbon_credit_methodology: string | null;
  verification_status: PreFeedMrvVerificationStatus;
  verifier_name: string | null;
  carbon_credit_eligibility: PreFeedCarbonCreditEligibility;
  eligibility_basis: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  supporting_document: ProjectDocument | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedMrvAssumptionPayload = {
  supporting_document_id?: string | null;
  baseline_emissions_tco2e_per_year?: number | null;
  captured_co2_accounting_tpy?: number | null;
  product_carbon_intensity_tco2e_per_ton?: number | null;
  electricity_source?: string | null;
  electricity_emission_factor_tco2e_per_mwh?: number | null;
  methanol_pathway?: string | null;
  carbon_credit_methodology?: string | null;
  verification_status: PreFeedMrvVerificationStatus;
  verifier_name?: string | null;
  carbon_credit_eligibility: PreFeedCarbonCreditEligibility;
  eligibility_basis?: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedMrvSummary = {
  package_id: string;
  assumption_id: string | null;
  scenario_id: string | null;
  carbon_intensity_tco2e_per_ton_methanol: number | null;
  abatement_tco2e_per_year: number | null;
  baseline_emissions_tco2e_per_year: number | null;
  captured_co2_accounting_tpy: number | null;
  carbon_credit_eligibility: PreFeedCarbonCreditEligibility | null;
  readiness_score: number;
  readiness_components: Record<string, number>;
  warnings: string[];
};
