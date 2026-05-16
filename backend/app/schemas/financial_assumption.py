from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ConfidenceLevel, DataStatus


class FinancialAssumptionBase(BaseModel):
    methanol_price_usd_per_ton: float | None = Field(default=None, ge=0)
    grey_methanol_price_usd_per_ton: float | None = Field(default=None, ge=0)
    hydrogen_price_usd_per_kg: float | None = Field(default=None, ge=0)
    electricity_price_usd_per_kwh: float | None = Field(default=None, ge=0)
    carbon_credit_price_idr_per_ton: float | None = Field(default=None, ge=0)
    exchange_rate_idr_usd: float | None = Field(default=None, ge=0)
    discount_rate: float | None = Field(default=None, ge=0)
    tax_rate: float | None = Field(default=None, ge=0, le=1)
    capex_capture_usd: float | None = Field(default=None, ge=0)
    capex_electrolyzer_usd: float | None = Field(default=None, ge=0)
    capex_methanol_plant_usd: float | None = Field(default=None, ge=0)
    capex_storage_port_usd: float | None = Field(default=None, ge=0)
    opex_percent_capex: float | None = Field(default=None, ge=0)
    data_status: DataStatus = "benchmark"
    confidence_level: ConfidenceLevel = "low"


class FinancialAssumptionCreate(FinancialAssumptionBase):
    pass


class FinancialAssumptionUpdate(BaseModel):
    methanol_price_usd_per_ton: float | None = Field(default=None, ge=0)
    grey_methanol_price_usd_per_ton: float | None = Field(default=None, ge=0)
    hydrogen_price_usd_per_kg: float | None = Field(default=None, ge=0)
    electricity_price_usd_per_kwh: float | None = Field(default=None, ge=0)
    carbon_credit_price_idr_per_ton: float | None = Field(default=None, ge=0)
    exchange_rate_idr_usd: float | None = Field(default=None, ge=0)
    discount_rate: float | None = Field(default=None, ge=0)
    tax_rate: float | None = Field(default=None, ge=0, le=1)
    capex_capture_usd: float | None = Field(default=None, ge=0)
    capex_electrolyzer_usd: float | None = Field(default=None, ge=0)
    capex_methanol_plant_usd: float | None = Field(default=None, ge=0)
    capex_storage_port_usd: float | None = Field(default=None, ge=0)
    opex_percent_capex: float | None = Field(default=None, ge=0)
    data_status: DataStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class FinancialAssumptionRead(FinancialAssumptionBase):
    id: str
    scenario_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
