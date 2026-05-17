from pydantic import BaseModel, Field


class ShortlistWeights(BaseModel):
    screening: float
    economics: float
    logistics: float
    confidence: float


class ShortlistScoreBreakdown(BaseModel):
    screening_score: float
    economics_score: float
    logistics_score: float
    confidence_score: float
    final_score: float


class ShortlistCandidate(BaseModel):
    shortlist_rank: int
    recommendation: str
    readiness_label: str
    plant_id: str
    scenario_id: str
    scenario_result_id: str
    site_name: str
    unit_name: str
    province: str | None
    city: str | None
    capacity_mw: float | None
    screening_rank: int
    composite_score: float
    co2_tpy: float | None
    captured_co2_tpy: float | None
    methanol_tpy: float | None
    h2_required_tpy: float | None
    electrolyzer_required_mw: float | None
    gross_revenue_usd_per_year: float | None
    estimated_lcom_usd_ton: float | None
    nearest_port_name: str | None
    nearest_port_distance_km: float | None
    nearest_port_readiness_score: float
    port_proximity_score: float
    score_breakdown: ShortlistScoreBreakdown
    data_confidence_label: str
    data_gap_count: int
    key_bottleneck: str
    decision_rationale: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class ShortlistSummary(BaseModel):
    candidate_count: int
    shortlist_count: int
    top_candidate: str | None
    top_score: float | None
    shortlist_captured_co2_tpy: float
    shortlist_methanol_tpy: float
    shortlist_gross_revenue_usd_per_year: float
    average_shortlist_lcom_usd_ton: float | None


class ShortlistDecisionMatrix(BaseModel):
    scheme: str
    top_n: int
    method: str
    weights: ShortlistWeights
    summary: ShortlistSummary
    candidates: list[ShortlistCandidate]
    warnings: list[str] = Field(default_factory=list)
