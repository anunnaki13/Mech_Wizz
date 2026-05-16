import uuid
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScenarioResult(Base):
    __tablename__ = "scenario_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(ForeignKey("business_scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    total_co2_ton_per_year: Mapped[float | None] = mapped_column(Float)
    captured_co2_ton_per_year: Mapped[float | None] = mapped_column(Float)
    vented_co2_ton_per_year: Mapped[float | None] = mapped_column(Float)
    methanol_ton_per_year: Mapped[float | None] = mapped_column(Float)
    h2_required_ton_per_year: Mapped[float | None] = mapped_column(Float)
    electrolyzer_required_mw: Mapped[float | None] = mapped_column(Float)
    gross_revenue_usd_per_year: Mapped[float | None] = mapped_column(Float)
    lcom_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    npv_usd: Mapped[float | None] = mapped_column(Float)
    irr: Mapped[float | None] = mapped_column(Float)
    payback_years: Mapped[float | None] = mapped_column(Float)
    missing_inputs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    assumption_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    calculation_version: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="low")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scenario: Mapped["BusinessScenario"] = relationship("BusinessScenario", back_populates="results")
    unit_scoring_results: Mapped[list["UnitScoringResult"]] = relationship(
        "UnitScoringResult",
        back_populates="scenario_result",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
