from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel


SensitivityVariable = Literal[
    "h2_price",
    "electricity_price",
    "methanol_price",
    "capex",
    "capture_rate",
    "plant_availability",
    "carbon_credit_price",
    "exchange_rate",
]


class SensitivityRunRequest(BaseModel):
    scenario_id: str
    plant_id: str | None = None
    variables: list[SensitivityVariable] | None = None
    low_multiplier: float = Field(default=0.80, gt=0)
    high_multiplier: float = Field(default=1.20, gt=0)


class SensitivityResultRead(BaseModel):
    id: str
    run_id: str
    plant_id: str
    scenario_id: str
    scenario_result_id: str | None
    variable_name: str
    low_input_value: float | None
    base_input_value: float | None
    high_input_value: float | None
    low_irr: float | None
    base_irr: float | None
    high_irr: float | None
    low_npv_usd: float | None
    base_npv_usd: float | None
    high_npv_usd: float | None
    low_lcom_usd_per_ton: float | None
    base_lcom_usd_per_ton: float | None
    high_lcom_usd_per_ton: float | None
    impact_score: float
    missing_inputs: list[str]
    warnings: list[str]
    assumption_snapshot: dict
    confidence_level: ConfidenceLevel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SensitivityRunResponse(BaseModel):
    run_id: str
    plant_id: str
    scenario_id: str
    scenario_result_id: str | None
    results: list[SensitivityResultRead]
