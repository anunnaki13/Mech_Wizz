from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel
from app.schemas.document import DocumentRead


ValidationEvidenceCategory = Literal["technical", "economics", "logistics", "power_h2", "commercial_mrv"]
ValidationEvidenceStatus = Literal["missing", "requested", "received", "verified", "rejected"]
ValidationEvidencePriority = Literal["high", "medium", "low"]

VALIDATION_EVIDENCE_CATEGORY_VALUES = ("technical", "economics", "logistics", "power_h2", "commercial_mrv")
VALIDATION_EVIDENCE_STATUS_VALUES = ("missing", "requested", "received", "verified", "rejected")
VALIDATION_EVIDENCE_PRIORITY_VALUES = ("high", "medium", "low")


class ValidationEvidenceCreate(BaseModel):
    plant_id: str
    scenario_id: str
    document_id: str | None = None
    category: ValidationEvidenceCategory
    evidence_key: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=220)
    required_evidence: str | None = None
    current_basis: str | None = None
    status: ValidationEvidenceStatus = "missing"
    priority: ValidationEvidencePriority = "high"
    owner_name: str | None = Field(default=None, max_length=160)
    source_organization: str | None = Field(default=None, max_length=160)
    reference_url: str | None = Field(default=None, max_length=500)
    due_date: date | None = None
    received_date: date | None = None
    verified_date: date | None = None
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class ValidationEvidenceUpdate(BaseModel):
    document_id: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=220)
    required_evidence: str | None = None
    current_basis: str | None = None
    status: ValidationEvidenceStatus | None = None
    priority: ValidationEvidencePriority | None = None
    owner_name: str | None = Field(default=None, max_length=160)
    source_organization: str | None = Field(default=None, max_length=160)
    reference_url: str | None = Field(default=None, max_length=500)
    due_date: date | None = None
    received_date: date | None = None
    verified_date: date | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class ValidationEvidenceRead(BaseModel):
    id: str
    plant_id: str
    scenario_id: str
    document_id: str | None
    category: ValidationEvidenceCategory
    evidence_key: str
    title: str
    required_evidence: str | None
    current_basis: str | None
    status: ValidationEvidenceStatus
    priority: ValidationEvidencePriority
    owner_name: str | None
    source_organization: str | None
    reference_url: str | None
    due_date: date | None
    received_date: date | None
    verified_date: date | None
    confidence_level: ConfidenceLevel
    notes: str | None
    supporting_document: DocumentRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ValidationEvidenceRequirement(BaseModel):
    plant_id: str
    scenario_id: str
    category: ValidationEvidenceCategory
    evidence_key: str
    title: str
    required_evidence: str
    current_basis: str
    priority: ValidationEvidencePriority
    source_validation_status: str
    status: ValidationEvidenceStatus
    confidence_level: ConfidenceLevel
    status_score: float
    record: ValidationEvidenceRead | None = None


class ValidationEvidenceCandidate(BaseModel):
    validation_rank: int
    site_name: str
    plant_id: str
    scenario_id: str
    province: str | None
    capacity_mw: float | None
    final_score: float
    methanol_tpy: float | None
    estimated_lcom_usd_ton: float | None
    nearest_port_name: str | None
    evidence_readiness_score: float
    high_priority_open_items: int
    evidence_items: list[ValidationEvidenceRequirement]


class ValidationEvidenceSummary(BaseModel):
    candidate_count: int
    lead_candidate: str | None
    total_items: int
    verified_items: int
    high_priority_open_items: int
    evidence_readiness_score: float
    counts_by_status: dict[str, int]


class ValidationEvidenceWorkspace(BaseModel):
    scheme: str
    limit: int
    summary: ValidationEvidenceSummary
    candidates: list[ValidationEvidenceCandidate]
    warnings: list[str]
