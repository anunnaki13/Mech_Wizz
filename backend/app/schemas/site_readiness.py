from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


class SiteReadinessBase(BaseModel):
    available_land_ha: float | None = Field(default=None, ge=0)
    land_status: str | None = None
    distance_to_stack_km: float | None = Field(default=None, ge=0)
    has_port_or_jetty: bool | None = None
    distance_to_port_km: float | None = Field(default=None, ge=0)
    port_capacity_dwt: float | None = Field(default=None, ge=0)
    road_access: str | None = None
    water_availability: str | None = None
    power_availability: str | None = None
    utility_readiness: str | None = None
    permit_risk: str | None = None
    social_risk: str | None = None
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"


class SiteReadinessCreate(SiteReadinessBase):
    pass


class SiteReadinessUpdate(BaseModel):
    available_land_ha: float | None = Field(default=None, ge=0)
    land_status: str | None = None
    distance_to_stack_km: float | None = Field(default=None, ge=0)
    has_port_or_jetty: bool | None = None
    distance_to_port_km: float | None = Field(default=None, ge=0)
    port_capacity_dwt: float | None = Field(default=None, ge=0)
    road_access: str | None = None
    water_availability: str | None = None
    power_availability: str | None = None
    utility_readiness: str | None = None
    permit_risk: str | None = None
    social_risk: str | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class SiteReadinessRead(SiteReadinessBase):
    id: str
    plant_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
