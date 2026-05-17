import uuid
from datetime import date

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ValidationEvidence(Base):
    __tablename__ = "validation_evidence"
    __table_args__ = (
        UniqueConstraint(
            "plant_id",
            "scenario_id",
            "category",
            "evidence_key",
            name="uq_validation_evidence_candidate_key",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("business_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    evidence_key: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    required_evidence: Mapped[str | None] = mapped_column(Text)
    current_basis: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="missing", index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="high", index=True)
    owner_name: Mapped[str | None] = mapped_column(String(160))
    source_organization: Mapped[str | None] = mapped_column(String(160))
    reference_url: Mapped[str | None] = mapped_column(String(500))
    due_date: Mapped[date | None] = mapped_column(Date)
    received_date: Mapped[date | None] = mapped_column(Date)
    verified_date: Mapped[date | None] = mapped_column(Date)
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    plant: Mapped["Plant"] = relationship("Plant")
    scenario: Mapped["BusinessScenario"] = relationship("BusinessScenario")
    supporting_document: Mapped["Document | None"] = relationship("Document")
