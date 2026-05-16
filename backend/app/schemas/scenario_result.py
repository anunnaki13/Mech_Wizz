from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel


class ScenarioResultRead(BaseModel):
    id: str
    scenario_id: str
    total_co2_ton_per_year: float | None
    captured_co2_ton_per_year: float | None
    vented_co2_ton_per_year: float | None
    methanol_ton_per_year: float | None
    h2_required_ton_per_year: float | None
    electrolyzer_required_mw: float | None
    gross_revenue_usd_per_year: float | None
    lcom_usd_per_ton: float | None
    npv_usd: float | None
    irr: float | None
    payback_years: float | None
    missing_inputs: list[str] = Field(default_factory=list)
    assumption_snapshot: dict[str, Any] = Field(default_factory=dict)
    calculation_version: str
    confidence_level: ConfidenceLevel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
