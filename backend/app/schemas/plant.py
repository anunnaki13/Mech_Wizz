from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


class PlantBase(BaseModel):
    plant_name: str = Field(..., min_length=1, max_length=160)
    unit_name: str = Field(..., min_length=1, max_length=120)
    province: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    capacity_mw: float | None = Field(default=None, ge=0)
    fuel_type: str | None = None
    status: str | None = None
    capacity_factor: float | None = Field(default=None, ge=0, le=1)
    operating_days_per_year: int | None = Field(default=None, ge=0, le=366)
    owner: str | None = None
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    plant_name: str | None = Field(default=None, min_length=1, max_length=160)
    unit_name: str | None = Field(default=None, min_length=1, max_length=120)
    province: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    capacity_mw: float | None = Field(default=None, ge=0)
    fuel_type: str | None = None
    status: str | None = None
    capacity_factor: float | None = Field(default=None, ge=0, le=1)
    operating_days_per_year: int | None = Field(default=None, ge=0, le=366)
    owner: str | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class PlantRead(PlantBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
