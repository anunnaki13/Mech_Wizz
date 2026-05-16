from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DataGapRead(BaseModel):
    id: str
    plant_id: str
    scenario_id: str | None
    source_module: str
    missing_data_name: str
    impact_level: str
    priority_level: str
    recommendation: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DataQualitySummaryRead(BaseModel):
    plant_id: str
    scenario_id: str | None
    input_status: dict[str, str]
    output_confidence: dict[str, str]
    gaps: list[DataGapRead]
