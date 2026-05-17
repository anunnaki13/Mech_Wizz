from typing import Literal

from pydantic import BaseModel, Field


ValidationStatus = Literal["available", "needs_validation", "critical_gap"]
Priority = Literal["high", "medium", "low"]


class ValidationEvidenceItem(BaseModel):
    category: str
    item: str
    current_basis: str
    required_evidence: str
    status: ValidationStatus
    priority: Priority


class ValidationCandidatePack(BaseModel):
    validation_rank: int
    site_name: str
    plant_id: str
    scenario_id: str
    province: str | None
    city: str | None
    capacity_mw: float | None
    final_score: float
    economics_score: float
    logistics_score: float
    confidence_score: float
    captured_co2_tpy: float | None
    methanol_tpy: float | None
    h2_required_tpy: float | None
    electrolyzer_required_mw: float | None
    gross_revenue_usd_per_year: float | None
    estimated_lcom_usd_ton: float | None
    nearest_port_name: str | None
    nearest_port_distance_km: float | None
    data_confidence_label: str
    data_gap_count: int
    key_bottleneck: str
    recommendation: str
    why_shortlisted: list[str] = Field(default_factory=list)
    validation_items: list[ValidationEvidenceItem] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class ValidationComparisonAxis(BaseModel):
    axis: str
    leader: str | None
    notes: str


class CommitteeMemo(BaseModel):
    title: str
    recommendation: str
    executive_summary: str
    decision_ask: str
    top3_summary: list[str] = Field(default_factory=list)
    decision_questions: list[str] = Field(default_factory=list)
    no_go_triggers: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class ValidationPackSummary(BaseModel):
    candidate_count: int
    lead_candidate: str | None
    total_captured_co2_tpy: float
    total_methanol_tpy: float
    total_gross_revenue_usd_per_year: float
    average_lcom_usd_ton: float | None
    high_priority_evidence_count: int


class Top3ValidationPack(BaseModel):
    scheme: str
    limit: int
    summary: ValidationPackSummary
    candidates: list[ValidationCandidatePack]
    comparison_axes: list[ValidationComparisonAxis] = Field(default_factory=list)
    committee_memo: CommitteeMemo
    warnings: list[str] = Field(default_factory=list)
