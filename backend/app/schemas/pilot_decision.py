from typing import Literal

from pydantic import BaseModel, Field


PilotGateStatus = Literal["blocked", "needs_evidence", "committee_ready"]
PilotRecommendation = Literal["do_not_advance", "continue_validation", "advance_to_committee"]


class PilotDecisionBlocker(BaseModel):
    plant_id: str
    scenario_id: str
    site_name: str
    category: str
    evidence_key: str
    title: str
    status: str
    priority: str
    recommendation: str


class PilotDecisionCandidate(BaseModel):
    validation_rank: int
    decision_rank: int
    site_name: str
    plant_id: str
    scenario_id: str
    province: str | None
    capacity_mw: float | None
    shortlist_score: float
    evidence_readiness_score: float
    evidence_adjusted_score: float
    gate_status: PilotGateStatus
    recommendation: PilotRecommendation
    verified_items: int
    rejected_items: int
    high_priority_open_items: int
    methanol_tpy: float | None
    estimated_lcom_usd_ton: float | None
    nearest_port_name: str | None
    blockers: list[PilotDecisionBlocker] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class PilotDecisionSummary(BaseModel):
    candidate_count: int
    recommended_candidate: str | None
    recommended_candidate_id: str | None
    committee_ready_count: int
    blocked_count: int
    high_priority_open_items: int
    average_evidence_readiness_score: float
    decision_message: str


class PilotDecisionDashboard(BaseModel):
    scheme: str
    limit: int
    summary: PilotDecisionSummary
    candidates: list[PilotDecisionCandidate]
    blockers: list[PilotDecisionBlocker] = Field(default_factory=list)
    action_plan: list[str] = Field(default_factory=list)
    methodology: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
