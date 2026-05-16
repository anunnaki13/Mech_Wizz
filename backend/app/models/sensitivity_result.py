import uuid
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SensitivityResult(Base):
    __tablename__ = "sensitivity_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("business_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_result_id: Mapped[str | None] = mapped_column(
        ForeignKey("scenario_results.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    variable_name: Mapped[str] = mapped_column(String(80), nullable=False)
    low_input_value: Mapped[float | None] = mapped_column(Float)
    base_input_value: Mapped[float | None] = mapped_column(Float)
    high_input_value: Mapped[float | None] = mapped_column(Float)
    low_irr: Mapped[float | None] = mapped_column(Float)
    base_irr: Mapped[float | None] = mapped_column(Float)
    high_irr: Mapped[float | None] = mapped_column(Float)
    low_npv_usd: Mapped[float | None] = mapped_column(Float)
    base_npv_usd: Mapped[float | None] = mapped_column(Float)
    high_npv_usd: Mapped[float | None] = mapped_column(Float)
    low_lcom_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    base_lcom_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    high_lcom_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    missing_inputs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    assumption_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="low")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="sensitivity_results")
    scenario: Mapped["BusinessScenario"] = relationship("BusinessScenario", back_populates="sensitivity_results")
    scenario_result: Mapped["ScenarioResult | None"] = relationship(
        "ScenarioResult",
        back_populates="sensitivity_results",
    )
