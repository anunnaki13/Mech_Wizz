from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus
from app.schemas.document import DocumentRead


PackageStatus = Literal["draft", "in_review", "validated", "archived"]
DocumentRole = Literal[
    "vendor_proposal",
    "epc_estimate",
    "offtake_document",
    "mrv_document",
    "permit_document",
    "internal_note",
]

PACKAGE_STATUS_VALUES = ("draft", "in_review", "validated", "archived")
DOCUMENT_ROLE_VALUES = (
    "vendor_proposal",
    "epc_estimate",
    "offtake_document",
    "mrv_document",
    "permit_document",
    "internal_note",
)


class PreFeedPackageCreate(BaseModel):
    plant_id: str
    scenario_id: str | None = None
    package_name: str = Field(min_length=1, max_length=160)
    package_status: PackageStatus = "draft"
    owner_name: str | None = Field(default=None, max_length=160)
    source_organization: str | None = Field(default=None, max_length=160)
    received_date: date | None = None
    version_label: str | None = Field(default=None, max_length=120)
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"
    notes: str | None = None


class PreFeedPackageUpdate(BaseModel):
    plant_id: str | None = None
    scenario_id: str | None = None
    package_name: str | None = Field(default=None, min_length=1, max_length=160)
    package_status: PackageStatus | None = None
    owner_name: str | None = Field(default=None, max_length=160)
    source_organization: str | None = Field(default=None, max_length=160)
    received_date: date | None = None
    version_label: str | None = Field(default=None, max_length=120)
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None
    notes: str | None = None


class PreFeedPackageDocumentCreate(BaseModel):
    document_id: str
    document_role: DocumentRole
    notes: str | None = None


class PreFeedPackageDocumentRead(BaseModel):
    id: str
    package_id: str
    document_id: str
    document_role: DocumentRole
    notes: str | None
    document: DocumentRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedPackageRead(BaseModel):
    id: str
    plant_id: str
    scenario_id: str | None
    package_name: str
    package_status: PackageStatus
    owner_name: str | None
    source_organization: str | None
    received_date: date | None
    version_label: str | None
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    notes: str | None
    document_links: list[PreFeedPackageDocumentRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreFeedPackageGapRead(BaseModel):
    package_id: str
    source_module: str
    missing_data_name: str
    impact_level: str
    priority_level: str
    recommendation: str
    status: str
    confidence_level: ConfidenceLevel
