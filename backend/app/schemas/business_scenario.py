from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


BusinessScheme = Literal["access", "align", "augment"]


class BusinessScenarioBase(BaseModel):
    scenario_name: str = Field(..., min_length=1, max_length=160)
    scheme: BusinessScheme
    pln_ownership_percent: float | None = Field(default=None, ge=0, le=100)
    partner_capex_responsibility_percent: float | None = Field(default=None, ge=0, le=100)
    pln_capex_responsibility_percent: float | None = Field(default=None, ge=0, le=100)
    revenue_model: str | None = Field(default=None, max_length=160)
    capture_rate: float | None = Field(default=0.85, ge=0, le=1)
    process_efficiency: float | None = Field(default=0.60, ge=0, le=1)
    data_status: DataStatus = "user_assumption"
    confidence_level: ConfidenceLevel = "medium"


class BusinessScenarioCreate(BusinessScenarioBase):
    pass


class BusinessScenarioUpdate(BaseModel):
    scenario_name: str | None = Field(default=None, min_length=1, max_length=160)
    scheme: BusinessScheme | None = None
    pln_ownership_percent: float | None = Field(default=None, ge=0, le=100)
    partner_capex_responsibility_percent: float | None = Field(default=None, ge=0, le=100)
    pln_capex_responsibility_percent: float | None = Field(default=None, ge=0, le=100)
    revenue_model: str | None = Field(default=None, max_length=160)
    capture_rate: float | None = Field(default=None, ge=0, le=1)
    process_efficiency: float | None = Field(default=None, ge=0, le=1)
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class BusinessScenarioRead(BusinessScenarioBase):
    id: str
    plant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
