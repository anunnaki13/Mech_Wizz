from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


class EmissionTestBase(BaseModel):
    stack_id: str = Field(..., min_length=1, max_length=120)
    test_date: date | None = None
    lab_name: str | None = None
    stack_diameter_m: float | None = Field(default=None, ge=0)
    gas_velocity_m_s: float | None = Field(default=None, ge=0)
    flue_gas_temperature_c: float | None = None
    co2_percent_dry: float | None = Field(default=None, ge=0, le=100)
    o2_percent: float | None = Field(default=None, ge=0, le=100)
    moisture_percent: float | None = Field(default=None, ge=0, le=100)
    so2_mg_nm3: float | None = Field(default=None, ge=0)
    nox_mg_nm3: float | None = Field(default=None, ge=0)
    particulate_mg_nm3: float | None = Field(default=None, ge=0)
    hg_mg_nm3: float | None = Field(default=None, ge=0)
    compliance_status: str | None = None
    data_status: DataStatus = "unknown"
    confidence_level: ConfidenceLevel = "unknown"


class EmissionTestCreate(EmissionTestBase):
    pass


class EmissionTestUpdate(BaseModel):
    stack_id: str | None = Field(default=None, min_length=1, max_length=120)
    test_date: date | None = None
    lab_name: str | None = None
    stack_diameter_m: float | None = Field(default=None, ge=0)
    gas_velocity_m_s: float | None = Field(default=None, ge=0)
    flue_gas_temperature_c: float | None = None
    co2_percent_dry: float | None = Field(default=None, ge=0, le=100)
    o2_percent: float | None = Field(default=None, ge=0, le=100)
    moisture_percent: float | None = Field(default=None, ge=0, le=100)
    so2_mg_nm3: float | None = Field(default=None, ge=0)
    nox_mg_nm3: float | None = Field(default=None, ge=0)
    particulate_mg_nm3: float | None = Field(default=None, ge=0)
    hg_mg_nm3: float | None = Field(default=None, ge=0)
    compliance_status: str | None = None
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class EmissionTestRead(EmissionTestBase):
    id: str
    plant_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
