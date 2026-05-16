import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PreFeedPriceDeck(Base):
    __tablename__ = "pre_feed_price_decks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[str | None] = mapped_column(ForeignKey("business_scenarios.id", ondelete="SET NULL"), index=True)
    deck_name: Mapped[str] = mapped_column(String(160), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    methanol_price_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    carbon_credit_price_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    electricity_price_usd_per_kwh: Mapped[float | None] = mapped_column(Float)
    hydrogen_price_usd_per_kg: Mapped[float | None] = mapped_column(Float)
    exchange_rate_idr_usd: Mapped[float | None] = mapped_column(Float)
    escalation_percent: Mapped[float | None] = mapped_column(Float)
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    package: Mapped["PreFeedPackage"] = relationship("PreFeedPackage")
    scenario: Mapped["BusinessScenario | None"] = relationship("BusinessScenario")


class PreFeedOfftakeProspect(Base):
    __tablename__ = "pre_feed_offtake_prospects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    supporting_document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    counterparty_name: Mapped[str] = mapped_column(String(160), nullable=False)
    product: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_volume_tpy: Mapped[float | None] = mapped_column(Float)
    term_years: Mapped[float | None] = mapped_column(Float)
    pricing_basis: Mapped[str | None] = mapped_column(String(160))
    price_usd_per_ton: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="lead", index=True)
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    package: Mapped["PreFeedPackage"] = relationship("PreFeedPackage")
    supporting_document: Mapped["Document | None"] = relationship("Document")


class PreFeedMrvAssumption(Base):
    __tablename__ = "pre_feed_mrv_assumptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    supporting_document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    baseline_emissions_tco2e_per_year: Mapped[float | None] = mapped_column(Float)
    captured_co2_accounting_tpy: Mapped[float | None] = mapped_column(Float)
    product_carbon_intensity_tco2e_per_ton: Mapped[float | None] = mapped_column(Float)
    electricity_source: Mapped[str | None] = mapped_column(String(160))
    electricity_emission_factor_tco2e_per_mwh: Mapped[float | None] = mapped_column(Float)
    methanol_pathway: Mapped[str | None] = mapped_column(String(160))
    carbon_credit_methodology: Mapped[str | None] = mapped_column(String(160))
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="not_started")
    verifier_name: Mapped[str | None] = mapped_column(String(160))
    carbon_credit_eligibility: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    eligibility_basis: Mapped[str | None] = mapped_column(Text)
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    package: Mapped["PreFeedPackage"] = relationship("PreFeedPackage")
    supporting_document: Mapped["Document | None"] = relationship("Document")
