from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


InsightType = Literal[
    "executive_summary",
    "data_gap_explanation",
    "investor_memo",
    "sensitivity_explanation",
    "document_qa",
]


class LlmGenerateRequest(BaseModel):
    model_name: str | None = None


class LlmInsightRead(BaseModel):
    id: str
    plant_id: str | None
    scenario_id: str | None
    document_id: str | None
    insight_type: InsightType
    model_name: str
    prompt: str
    response_text: str | None
    status: str
    error_message: str | None
    provider_response_id: str | None
    usage: dict[str, Any] | None = Field(default=None)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
