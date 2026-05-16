from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


RiskCategory = Literal[
    "technical",
    "commercial",
    "legal",
    "land",
    "grid",
    "offtake",
    "mrv",
    "financing",
    "economics",
    "execution",
    "other",
]
RiskStatus = Literal["open", "monitoring", "mitigating", "escalated", "closed"]
GateCategory = Literal["technical", "commercial", "legal", "land", "grid", "offtake", "mrv", "financing", "committee"]
GateStatus = Literal["not_started", "in_progress", "ready", "blocked", "waived"]
SeverityBand = Literal["low", "medium", "high", "critical"]

RISK_CATEGORY_VALUES = (
    "technical",
    "commercial",
    "legal",
    "land",
    "grid",
    "offtake",
    "mrv",
    "financing",
    "economics",
    "execution",
    "other",
)
RISK_STATUS_VALUES = ("open", "monitoring", "mitigating", "escalated", "closed")
GATE_CATEGORY_VALUES = ("technical", "commercial", "legal", "land", "grid", "offtake", "mrv", "financing", "committee")
GATE_STATUS_VALUES = ("not_started", "in_progress", "ready", "blocked", "waived")


class PreFeedRiskCreate(BaseModel):
    category: RiskCategory = "technical"
    risk_statement: str = Field(min_length=1)
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    mitigation: str | None = None
    owner_name: str | None = Field(default=None, max_length=160)
    due_date: date | None = None
    status: RiskStatus = "open"
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedRiskUpdate(BaseModel):
    category: RiskCategory | None = None
    risk_statement: str | None = Field(default=None, min_length=1)
    likelihood: int | None = Field(default=None, ge=1, le=5)
    impact: int | None = Field(default=None, ge=1, le=5)
    mitigation: str | None = None
    owner_name: str | None = Field(default=None, max_length=160)
    due_date: date | None = None
    status: RiskStatus | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedRiskRead(BaseModel):
    id: str
    package_id: str
    category: RiskCategory
    risk_statement: str
    likelihood: int
    impact: int
    severity_score: int
    severity_band: SeverityBand
    mitigation: str | None
    owner_name: str | None
    due_date: date | None
    status: RiskStatus
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedDecisionGateCreate(BaseModel):
    category: GateCategory = "technical"
    gate_title: str = Field(min_length=1, max_length=160)
    evidence_reference: str | None = None
    owner_name: str | None = Field(default=None, max_length=160)
    due_date: date | None = None
    is_critical: bool = False
    status: GateStatus = "not_started"
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedDecisionGateUpdate(BaseModel):
    category: GateCategory | None = None
    gate_title: str | None = Field(default=None, min_length=1, max_length=160)
    evidence_reference: str | None = None
    owner_name: str | None = Field(default=None, max_length=160)
    due_date: date | None = None
    is_critical: bool | None = None
    status: GateStatus | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedDecisionGateRead(BaseModel):
    id: str
    package_id: str
    category: GateCategory
    gate_title: str
    evidence_reference: str | None
    owner_name: str | None
    due_date: date | None
    is_critical: bool
    status: GateStatus
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedDecisionBlockerRead(BaseModel):
    source_module: str
    source_id: str | None = None
    title: str
    priority_level: str
    owner: str | None = None
    recommendation: str
    status: str
    confidence_level: ConfidenceLevel


class PreFeedDecisionNextActionRead(BaseModel):
    source_module: str
    source_id: str | None = None
    title: str
    priority_level: str
    owner: str | None = None
    recommendation: str
    status: str


class PreFeedRiskSummaryRead(BaseModel):
    package_id: str
    risk_count: int
    open_risk_count: int
    escalated_risk_count: int
    severity_distribution: dict[SeverityBand, int]
    top_risks: list[PreFeedRiskRead]
    warnings: list[str]


class PreFeedDecisionGateSummaryRead(BaseModel):
    package_id: str
    gate_count: int
    ready_gate_count: int
    blocked_gate_count: int
    critical_blocker_count: int
    readiness_score: float
    status_distribution: dict[GateStatus, int]
    gates_by_category: dict[str, dict[str, int]]
    warnings: list[str]


class PreFeedDecisionDashboardRead(BaseModel):
    package_id: str
    plant_id: str
    scenario_id: str | None
    package_name: str
    package_status: str
    package_confidence_level: ConfidenceLevel
    package_data_status: DataStatus
    package_gaps: list[dict[str, Any]]
    cost_summary: dict[str, Any]
    active_cost_basis: dict[str, Any] | None
    vendor_comparison: list[dict[str, Any]]
    offtake_summary: dict[str, Any]
    offtake_gaps: list[dict[str, Any]]
    mrv_summary: dict[str, Any]
    mrv_gaps: list[dict[str, Any]]
    risk_summary: PreFeedRiskSummaryRead
    decision_gate_summary: PreFeedDecisionGateSummaryRead
    blockers: list[PreFeedDecisionBlockerRead]
    next_actions: list[PreFeedDecisionNextActionRead]
    warnings: list[str]
