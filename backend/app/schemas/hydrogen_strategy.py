from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


class HydrogenStrategyBase(BaseModel):
    existing_h2_available: bool | None = None
    h2_strategy: str | None = None
    h2_cost_case: str | None = None
    h2_cost_usd_per_kg: float | None = Field(default=None, ge=0)
    h2_readiness_score: float | None = Field(default=None, ge=0, le=100)
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"


class HydrogenStrategyCreate(HydrogenStrategyBase):
    pass


class HydrogenStrategyUpdate(BaseModel):
    existing_h2_available: bool | None = None
    h2_strategy: str | None = None
    h2_cost_case: str | None = None
    h2_cost_usd_per_kg: float | None = Field(default=None, ge=0)
    h2_readiness_score: float | None = Field(default=None, ge=0, le=100)
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class HydrogenStrategyRead(HydrogenStrategyBase):
    id: str
    plant_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
