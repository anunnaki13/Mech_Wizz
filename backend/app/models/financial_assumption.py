import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FinancialAssumption(Base):
    __tablename__ = "financial_assumptions"
    __table_args__ = (UniqueConstraint("scenario_id", name="uq_financial_assumptions_scenario"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("business_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    methanol_price_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    grey_methanol_price_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    hydrogen_price_usd_per_kg: Mapped[float | None] = mapped_column(Float)
    electricity_price_usd_per_kwh: Mapped[float | None] = mapped_column(Float)
    carbon_credit_price_idr_per_ton: Mapped[float | None] = mapped_column(Float)
    exchange_rate_idr_usd: Mapped[float | None] = mapped_column(Float)
    discount_rate: Mapped[float | None] = mapped_column(Float)
    tax_rate: Mapped[float | None] = mapped_column(Float)
    capex_capture_usd: Mapped[float | None] = mapped_column(Float)
    capex_electrolyzer_usd: Mapped[float | None] = mapped_column(Float)
    capex_methanol_plant_usd: Mapped[float | None] = mapped_column(Float)
    capex_storage_port_usd: Mapped[float | None] = mapped_column(Float)
    opex_percent_capex: Mapped[float | None] = mapped_column(Float)
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="benchmark")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="low")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    scenario: Mapped["BusinessScenario"] = relationship("BusinessScenario", back_populates="financial_assumption")
