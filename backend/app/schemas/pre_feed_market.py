from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus
from app.schemas.document import DocumentRead


OfftakeProduct = Literal["e_methanol", "carbon_credit", "co2_supply", "hydrogen", "other"]
OfftakeStatus = Literal["lead", "discussion", "loi", "term_sheet", "contracted", "signed", "inactive"]
MrvVerificationStatus = Literal["not_started", "method_selected", "data_collected", "third_party_review", "verified"]
CarbonCreditEligibility = Literal["unknown", "screening", "potentially_eligible", "eligible", "not_eligible"]

OFFTAKE_PRODUCT_VALUES = ("e_methanol", "carbon_credit", "co2_supply", "hydrogen", "other")
OFFTAKE_STATUS_VALUES = ("lead", "discussion", "loi", "term_sheet", "contracted", "signed", "inactive")
MRV_VERIFICATION_STATUS_VALUES = (
    "not_started",
    "method_selected",
    "data_collected",
    "third_party_review",
    "verified",
)
CARBON_CREDIT_ELIGIBILITY_VALUES = ("unknown", "screening", "potentially_eligible", "eligible", "not_eligible")


class PreFeedPriceDeckCreate(BaseModel):
    scenario_id: str | None = None
    deck_name: str = Field(min_length=1, max_length=160)
    is_active: bool = True
    methanol_price_usd_per_ton: float | None = Field(default=None, ge=0)
    carbon_credit_price_usd_per_ton: float | None = Field(default=None, ge=0)
    electricity_price_usd_per_kwh: float | None = Field(default=None, ge=0)
    hydrogen_price_usd_per_kg: float | None = Field(default=None, ge=0)
    exchange_rate_idr_usd: float | None = Field(default=None, ge=0)
    escalation_percent: float | None = Field(default=None, ge=0)
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedPriceDeckUpdate(BaseModel):
    scenario_id: str | None = None
    deck_name: str | None = Field(default=None, min_length=1, max_length=160)
    is_active: bool | None = None
    methanol_price_usd_per_ton: float | None = Field(default=None, ge=0)
    carbon_credit_price_usd_per_ton: float | None = Field(default=None, ge=0)
    electricity_price_usd_per_kwh: float | None = Field(default=None, ge=0)
    hydrogen_price_usd_per_kg: float | None = Field(default=None, ge=0)
    exchange_rate_idr_usd: float | None = Field(default=None, ge=0)
    escalation_percent: float | None = Field(default=None, ge=0)
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedPriceDeckRead(BaseModel):
    id: str
    package_id: str
    scenario_id: str | None
    deck_name: str
    is_active: bool
    methanol_price_usd_per_ton: float | None
    carbon_credit_price_usd_per_ton: float | None
    electricity_price_usd_per_kwh: float | None
    hydrogen_price_usd_per_kg: float | None
    exchange_rate_idr_usd: float | None
    escalation_percent: float | None
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedOfftakeProspectCreate(BaseModel):
    supporting_document_id: str | None = None
    counterparty_name: str = Field(min_length=1, max_length=160)
    product: OfftakeProduct = "e_methanol"
    target_volume_tpy: float | None = Field(default=None, ge=0)
    term_years: float | None = Field(default=None, ge=0)
    pricing_basis: str | None = Field(default=None, max_length=160)
    price_usd_per_ton: float | None = Field(default=None, ge=0)
    status: OfftakeStatus = "lead"
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedOfftakeProspectUpdate(BaseModel):
    supporting_document_id: str | None = None
    counterparty_name: str | None = Field(default=None, min_length=1, max_length=160)
    product: OfftakeProduct | None = None
    target_volume_tpy: float | None = Field(default=None, ge=0)
    term_years: float | None = Field(default=None, ge=0)
    pricing_basis: str | None = Field(default=None, max_length=160)
    price_usd_per_ton: float | None = Field(default=None, ge=0)
    status: OfftakeStatus | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedOfftakeProspectRead(BaseModel):
    id: str
    package_id: str
    supporting_document_id: str | None
    counterparty_name: str
    product: OfftakeProduct
    target_volume_tpy: float | None
    term_years: float | None
    pricing_basis: str | None
    price_usd_per_ton: float | None
    status: OfftakeStatus
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    supporting_document: DocumentRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedGapRead(BaseModel):
    source_module: str
    missing_data_name: str
    impact_level: str
    priority_level: str
    owner: str
    recommendation: str
    status: str
    confidence_level: ConfidenceLevel


class PreFeedOfftakeSummaryRead(BaseModel):
    package_id: str
    scenario_id: str | None
    active_price_deck_id: str | None
    prospect_count: int
    methanol_volume_committed_tpy: float
    methanol_volume_coverage: float | None
    methanol_revenue_usd_per_year: float | None
    carbon_credit_revenue_usd_per_year: float | None
    gross_revenue_usd_per_year: float | None
    readiness_score: float
    readiness_components: dict[str, float]
    scenario_ready_assumptions: dict[str, Any]
    warnings: list[str]


class PreFeedMrvAssumptionCreate(BaseModel):
    supporting_document_id: str | None = None
    baseline_emissions_tco2e_per_year: float | None = Field(default=None, ge=0)
    captured_co2_accounting_tpy: float | None = Field(default=None, ge=0)
    product_carbon_intensity_tco2e_per_ton: float | None = Field(default=None, ge=0)
    electricity_source: str | None = Field(default=None, max_length=160)
    electricity_emission_factor_tco2e_per_mwh: float | None = Field(default=None, ge=0)
    methanol_pathway: str | None = Field(default=None, max_length=160)
    carbon_credit_methodology: str | None = Field(default=None, max_length=160)
    verification_status: MrvVerificationStatus = "not_started"
    verifier_name: str | None = Field(default=None, max_length=160)
    carbon_credit_eligibility: CarbonCreditEligibility = "unknown"
    eligibility_basis: str | None = None
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedMrvAssumptionUpdate(BaseModel):
    supporting_document_id: str | None = None
    baseline_emissions_tco2e_per_year: float | None = Field(default=None, ge=0)
    captured_co2_accounting_tpy: float | None = Field(default=None, ge=0)
    product_carbon_intensity_tco2e_per_ton: float | None = Field(default=None, ge=0)
    electricity_source: str | None = Field(default=None, max_length=160)
    electricity_emission_factor_tco2e_per_mwh: float | None = Field(default=None, ge=0)
    methanol_pathway: str | None = Field(default=None, max_length=160)
    carbon_credit_methodology: str | None = Field(default=None, max_length=160)
    verification_status: MrvVerificationStatus | None = None
    verifier_name: str | None = Field(default=None, max_length=160)
    carbon_credit_eligibility: CarbonCreditEligibility | None = None
    eligibility_basis: str | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedMrvAssumptionRead(BaseModel):
    id: str
    package_id: str
    supporting_document_id: str | None
    baseline_emissions_tco2e_per_year: float | None
    captured_co2_accounting_tpy: float | None
    product_carbon_intensity_tco2e_per_ton: float | None
    electricity_source: str | None
    electricity_emission_factor_tco2e_per_mwh: float | None
    methanol_pathway: str | None
    carbon_credit_methodology: str | None
    verification_status: MrvVerificationStatus
    verifier_name: str | None
    carbon_credit_eligibility: CarbonCreditEligibility
    eligibility_basis: str | None
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    supporting_document: DocumentRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedMrvSummaryRead(BaseModel):
    package_id: str
    assumption_id: str | None
    scenario_id: str | None
    carbon_intensity_tco2e_per_ton_methanol: float | None
    abatement_tco2e_per_year: float | None
    baseline_emissions_tco2e_per_year: float | None
    captured_co2_accounting_tpy: float | None
    carbon_credit_eligibility: CarbonCreditEligibility | None
    readiness_score: float
    readiness_components: dict[str, float]
    warnings: list[str]
