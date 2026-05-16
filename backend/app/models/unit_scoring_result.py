import uuid
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UnitScoringResult(Base):
    __tablename__ = "unit_scoring_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("business_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_result_id: Mapped[str] = mapped_column(
        ForeignKey("scenario_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scoring_run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    co2_availability_score: Mapped[float] = mapped_column(Float, nullable=False)
    methanol_potential_score: Mapped[float] = mapped_column(Float, nullable=False)
    h2_readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    economic_return_score: Mapped[float] = mapped_column(Float, nullable=False)
    infrastructure_score: Mapped[float] = mapped_column(Float, nullable=False)
    land_port_score: Mapped[float] = mapped_column(Float, nullable=False)
    market_access_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_permit_score: Mapped[float] = mapped_column(Float, nullable=False)
    data_completeness_score: Mapped[float] = mapped_column(Float, nullable=False)
    emission_data_quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    land_readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    utility_readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    h2_strategy_clarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    permit_logistic_readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    carbon_credit_potential_score: Mapped[float] = mapped_column(Float, nullable=False)
    strategic_value_score: Mapped[float] = mapped_column(Float, nullable=False)
    utility_advantage_score: Mapped[float] = mapped_column(Float, nullable=False)
    component_scores: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    data_gap_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rank_position: Mapped[int | None] = mapped_column(Integer)
    recommended_scheme: Mapped[str] = mapped_column(String(80), nullable=False)
    key_bottleneck: Mapped[str] = mapped_column(String(240), nullable=False)
    scoring_version: Mapped[str] = mapped_column(String(80), nullable=False, default="phase3-scoring-v1")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="unit_scoring_results")
    scenario: Mapped["BusinessScenario"] = relationship("BusinessScenario", back_populates="unit_scoring_results")
    scenario_result: Mapped["ScenarioResult"] = relationship("ScenarioResult", back_populates="unit_scoring_results")
