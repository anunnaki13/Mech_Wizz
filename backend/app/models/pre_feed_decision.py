import uuid
from datetime import date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def severity_band(score: int) -> str:
    if score >= 20:
        return "critical"
    if score >= 12:
        return "high"
    if score >= 6:
        return "medium"
    return "low"


class PreFeedRisk(Base):
    __tablename__ = "pre_feed_risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    risk_statement: Mapped[str] = mapped_column(Text, nullable=False)
    likelihood: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    mitigation: Mapped[str | None] = mapped_column(Text)
    owner_name: Mapped[str | None] = mapped_column(String(160))
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", index=True)
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

    @property
    def severity_score(self) -> int:
        return self.likelihood * self.impact

    @property
    def severity_band(self) -> str:
        return severity_band(self.severity_score)


class PreFeedDecisionGate(Base):
    __tablename__ = "pre_feed_decision_gates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(ForeignKey("pre_feed_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    gate_title: Mapped[str] = mapped_column(String(160), nullable=False)
    evidence_reference: Mapped[str | None] = mapped_column(Text)
    owner_name: Mapped[str | None] = mapped_column(String(160))
    due_date: Mapped[date | None] = mapped_column(Date)
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="not_started", index=True)
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
