from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus
from app.schemas.document import DocumentRead


CostType = Literal["capex", "opex"]
CostComponent = Literal[
    "capture_package",
    "electrolyzer",
    "methanol_plant",
    "storage_port",
    "grid_power",
    "land",
    "mrv",
    "other",
]
OpexRecurrence = Literal["annual", "monthly", "quarterly", "weekly", "daily", "one_time"]
SelectionType = Literal["blended_package", "vendor_proposal"]

COST_TYPE_VALUES = ("capex", "opex")
COST_COMPONENT_VALUES = (
    "capture_package",
    "electrolyzer",
    "methanol_plant",
    "storage_port",
    "grid_power",
    "land",
    "mrv",
    "other",
)
OPEX_CATEGORY_VALUES = (
    "fixed_opex",
    "variable_opex",
    "electricity",
    "water",
    "chemicals",
    "labor",
    "maintenance",
    "transport",
    "mrv",
    "other",
)
RECURRENCE_VALUES = ("annual", "monthly", "quarterly", "weekly", "daily", "one_time")
SELECTION_TYPE_VALUES = ("blended_package", "vendor_proposal")


class PreFeedCostItemCreate(BaseModel):
    vendor_proposal_id: str | None = None
    cost_type: CostType
    cost_component: str = Field(min_length=1, max_length=80)
    amount: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    unit_basis: str | None = Field(default=None, max_length=80)
    recurrence: OpexRecurrence | None = None
    contingency_percent: float | None = Field(default=None, ge=0)
    escalation_percent: float | None = Field(default=None, ge=0)
    source_label: str | None = Field(default=None, max_length=160)
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedCostItemUpdate(BaseModel):
    vendor_proposal_id: str | None = None
    cost_type: CostType | None = None
    cost_component: str | None = Field(default=None, min_length=1, max_length=80)
    amount: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    unit_basis: str | None = Field(default=None, max_length=80)
    recurrence: OpexRecurrence | None = None
    contingency_percent: float | None = Field(default=None, ge=0)
    escalation_percent: float | None = Field(default=None, ge=0)
    source_label: str | None = Field(default=None, max_length=160)
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedCostItemRead(BaseModel):
    id: str
    package_id: str
    vendor_proposal_id: str | None
    cost_type: CostType
    cost_component: str
    amount: float
    currency: str
    unit_basis: str | None
    recurrence: OpexRecurrence | None
    contingency_percent: float | None
    escalation_percent: float | None
    source_label: str | None
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedCostSummaryRead(BaseModel):
    package_id: str
    vendor_proposal_id: str | None = None
    item_count: int
    capex_total_by_currency: dict[str, float]
    annual_opex_total_by_currency: dict[str, float]
    scenario_ready_assumptions: dict[str, float]
    warnings: list[str]


class PreFeedVendorProposalCreate(BaseModel):
    supporting_document_id: str | None = None
    vendor_name: str = Field(min_length=1, max_length=160)
    proposal_name: str = Field(min_length=1, max_length=160)
    scope_capture_package: bool = False
    scope_electrolyzer: bool = False
    scope_methanol_plant: bool = False
    scope_storage_port: bool = False
    scope_grid_power: bool = False
    scope_land: bool = False
    scope_mrv: bool = False
    commercial_basis: str | None = None
    delivery_assumptions: str | None = None
    exclusions: str | None = None
    validity_date: date | None = None
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedVendorProposalUpdate(BaseModel):
    supporting_document_id: str | None = None
    vendor_name: str | None = Field(default=None, min_length=1, max_length=160)
    proposal_name: str | None = Field(default=None, min_length=1, max_length=160)
    scope_capture_package: bool | None = None
    scope_electrolyzer: bool | None = None
    scope_methanol_plant: bool | None = None
    scope_storage_port: bool | None = None
    scope_grid_power: bool | None = None
    scope_land: bool | None = None
    scope_mrv: bool | None = None
    commercial_basis: str | None = None
    delivery_assumptions: str | None = None
    exclusions: str | None = None
    validity_date: date | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedVendorProposalRead(BaseModel):
    id: str
    package_id: str
    supporting_document_id: str | None
    vendor_name: str
    proposal_name: str
    scope_capture_package: bool
    scope_electrolyzer: bool
    scope_methanol_plant: bool
    scope_storage_port: bool
    scope_grid_power: bool
    scope_land: bool
    scope_mrv: bool
    commercial_basis: str | None
    delivery_assumptions: str | None
    exclusions: str | None
    validity_date: date | None
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    supporting_document: DocumentRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedVendorGapRead(BaseModel):
    proposal_id: str
    source_module: str
    missing_data_name: str
    impact_level: str
    priority_level: str
    recommendation: str
    status: str
    confidence_level: ConfidenceLevel


class PreFeedVendorComparisonRead(BaseModel):
    proposal_id: str
    vendor_name: str
    proposal_name: str
    capex_total_by_currency: dict[str, float]
    annual_opex_total_by_currency: dict[str, float]
    scope_completeness_score: float
    missing_scopes: list[str]
    gap_count: int
    confidence_level: ConfidenceLevel
    validity_date: date | None


class PreFeedCostBasisSelectionCreate(BaseModel):
    package_id: str
    vendor_proposal_id: str | None = None
    selection_type: SelectionType
    selected_by: str | None = Field(default=None, max_length=160)
    selection_notes: str | None = None


class PreFeedCostBasisSelectionRead(BaseModel):
    id: str
    scenario_id: str
    package_id: str
    vendor_proposal_id: str | None
    selection_type: SelectionType
    is_active: bool
    snapshot_totals: dict[str, Any] | None
    scenario_ready_assumptions: dict[str, Any] | None
    selected_by: str | None
    selection_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
