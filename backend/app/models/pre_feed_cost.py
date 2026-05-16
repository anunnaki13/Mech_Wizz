import uuid
from datetime import date

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PreFeedVendorProposal(Base):
    __tablename__ = "pre_feed_vendor_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    supporting_document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    vendor_name: Mapped[str] = mapped_column(String(160), nullable=False)
    proposal_name: Mapped[str] = mapped_column(String(160), nullable=False)
    scope_capture_package: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope_electrolyzer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope_methanol_plant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope_storage_port: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope_grid_power: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope_land: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope_mrv: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    commercial_basis: Mapped[str | None] = mapped_column(Text)
    delivery_assumptions: Mapped[str | None] = mapped_column(Text)
    exclusions: Mapped[str | None] = mapped_column(Text)
    validity_date: Mapped[date | None] = mapped_column(Date)
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
    cost_items: Mapped[list["PreFeedCostItem"]] = relationship("PreFeedCostItem", back_populates="vendor_proposal")


class PreFeedCostItem(Base):
    __tablename__ = "pre_feed_cost_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_proposal_id: Mapped[str | None] = mapped_column(
        ForeignKey("pre_feed_vendor_proposals.id", ondelete="SET NULL"),
        index=True,
    )
    cost_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    cost_component: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    unit_basis: Mapped[str | None] = mapped_column(String(80))
    recurrence: Mapped[str | None] = mapped_column(String(32))
    contingency_percent: Mapped[float | None] = mapped_column(Float)
    escalation_percent: Mapped[float | None] = mapped_column(Float)
    source_label: Mapped[str | None] = mapped_column(String(160))
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
    vendor_proposal: Mapped[PreFeedVendorProposal | None] = relationship("PreFeedVendorProposal", back_populates="cost_items")


class PreFeedCostBasisSelection(Base):
    __tablename__ = "pre_feed_cost_basis_selections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(ForeignKey("business_scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_proposal_id: Mapped[str | None] = mapped_column(
        ForeignKey("pre_feed_vendor_proposals.id", ondelete="SET NULL"),
        index=True,
    )
    selection_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    snapshot_totals: Mapped[dict | None] = mapped_column(JSON)
    scenario_ready_assumptions: Mapped[dict | None] = mapped_column(JSON)
    selected_by: Mapped[str | None] = mapped_column(String(160))
    selection_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    scenario: Mapped["BusinessScenario"] = relationship("BusinessScenario")
    package: Mapped["PreFeedPackage"] = relationship("PreFeedPackage")
    vendor_proposal: Mapped[PreFeedVendorProposal | None] = relationship("PreFeedVendorProposal")
