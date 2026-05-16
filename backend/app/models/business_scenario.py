import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusinessScenario(Base):
    __tablename__ = "business_scenarios"
    __table_args__ = (UniqueConstraint("plant_id", "scenario_name", name="uq_business_scenarios_plant_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_name: Mapped[str] = mapped_column(String(160), nullable=False)
    scheme: Mapped[str] = mapped_column(String(32), nullable=False)
    pln_ownership_percent: Mapped[float | None] = mapped_column(Float)
    partner_capex_responsibility_percent: Mapped[float | None] = mapped_column(Float)
    pln_capex_responsibility_percent: Mapped[float | None] = mapped_column(Float)
    revenue_model: Mapped[str | None] = mapped_column(String(160))
    capture_rate: Mapped[float | None] = mapped_column(Float)
    process_efficiency: Mapped[float | None] = mapped_column(Float)
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="user_assumption")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    plant: Mapped["Plant"] = relationship("Plant", back_populates="business_scenarios")
    financial_assumption: Mapped["FinancialAssumption | None"] = relationship(
        "FinancialAssumption",
        back_populates="scenario",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    results: Mapped[list["ScenarioResult"]] = relationship(
        "ScenarioResult",
        back_populates="scenario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    unit_scoring_results: Mapped[list["UnitScoringResult"]] = relationship(
        "UnitScoringResult",
        back_populates="scenario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sensitivity_results: Mapped[list["SensitivityResult"]] = relationship(
        "SensitivityResult",
        back_populates="scenario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
