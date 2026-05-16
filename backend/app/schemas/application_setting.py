from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


class ApplicationSettingRead(BaseModel):
    id: str
    key: str
    category: str
    value: dict[str, Any]
    data_status: DataStatus
    confidence_level: ConfidenceLevel
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationSettingUpdate(BaseModel):
    value: dict[str, Any] = Field(default_factory=dict)
    data_status: DataStatus = "user_assumption"
    confidence_level: ConfidenceLevel = "medium"


class OpenRouterSettingsRead(BaseModel):
    has_api_key: bool
    api_key_masked: str | None = None
    api_key_source: str
    base_url: str
    model: str
    site_url: str
    app_name: str


class OpenRouterSettingsUpdate(BaseModel):
    api_key: str | None = None
    clear_api_key: bool = False
    base_url: str | None = None
    model: str | None = None
    site_url: str | None = None
    app_name: str | None = None
