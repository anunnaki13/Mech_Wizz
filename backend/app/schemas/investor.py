from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ConfidenceLevel


class InvestorCaseRead(BaseModel):
    plant: dict[str, Any]
    scenario: dict[str, Any]
    kpis: dict[str, Any]
    capex_structure: dict[str, Any]
    revenue_mix: list[dict[str, Any]]
    scenario_comparison: list[dict[str, Any]]
    thesis_flow: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    roadmap: list[dict[str, Any]]
    why_this_wins: list[str]
    data_gaps: list[dict[str, str]]
    sensitivity: dict[str, Any] | None = None
    confidence_level: ConfidenceLevel
    warnings: list[str] = Field(default_factory=list)
    data_quality: dict[str, Any] = Field(default_factory=dict)
