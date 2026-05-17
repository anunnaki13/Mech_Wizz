from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


OpportunityLevel = Literal["low", "medium", "high", "priority"]


class ScoringRecalculateRequest(BaseModel):
    scenario_id: str | None = None
    scheme: str | None = None


class UnitScoringRead(BaseModel):
    id: str
    plant_id: str
    scenario_id: str
    scenario_result_id: str
    scoring_run_id: str
    opportunity_score: float
    readiness_score: float
    confidence_score: float
    composite_score: float
    co2_availability_score: float
    methanol_potential_score: float
    h2_readiness_score: float
    economic_return_score: float
    infrastructure_score: float
    land_port_score: float
    market_access_score: float
    risk_permit_score: float
    data_completeness_score: float
    emission_data_quality_score: float
    land_readiness_score: float
    utility_readiness_score: float
    h2_strategy_clarity_score: float
    permit_logistic_readiness_score: float
    carbon_credit_potential_score: float
    strategic_value_score: float
    utility_advantage_score: float
    component_scores: dict[str, Any] = Field(default_factory=dict)
    data_gap_count: int
    rank_position: int | None
    recommended_scheme: str
    key_bottleneck: str
    scoring_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScoringRecalculateResponse(BaseModel):
    scoring_run_id: str | None
    created_count: int
    results: list[UnitScoringRead]


class UnitRankingRow(BaseModel):
    rank: int
    plant_id: str
    site_id: str
    scenario_id: str
    scenario_result_id: str
    scoring_result_id: str
    scenario_name: str
    scheme: str
    site_name: str
    unit_name: str
    province: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    capacity_mw: float | None
    fuel_type: str | None
    composite_score: float
    opportunity_score: float
    readiness_score: float
    confidence_score: float
    heatmap_weight: float
    co2_tpy: float | None
    captured_co2_tpy: float | None
    methanol_tpy: float | None
    h2_required_tpy: float | None
    electrolyzer_required_mw: float | None
    gross_revenue_usd_per_year: float | None
    estimated_irr: float | None
    estimated_lcom_usd_ton: float | None
    recommended_scheme: str
    key_bottleneck: str
    data_gap_count: int
    data_confidence_label: str
    opportunity_level: OpportunityLevel
    calculation_version: str


class GeoJSONGeometry(BaseModel):
    type: Literal["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon"]
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"]
    id: str
    geometry: GeoJSONGeometry
    properties: dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[GeoJSONFeature]


class UnitProfileRead(BaseModel):
    plant: dict[str, Any]
    scenario: dict[str, Any] | None
    latest_result: dict[str, Any] | None
    latest_scoring: dict[str, Any] | None
    score_breakdown: dict[str, Any]
    data_gaps: list[dict[str, str]]
    confidence_labels: dict[str, str]
