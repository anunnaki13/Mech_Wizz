import uuid
from datetime import date

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PreFeedPackage(Base):
    __tablename__ = "pre_feed_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[str | None] = mapped_column(ForeignKey("business_scenarios.id", ondelete="SET NULL"), index=True)
    package_name: Mapped[str] = mapped_column(String(160), nullable=False)
    package_status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft", index=True)
    owner_name: Mapped[str | None] = mapped_column(String(160))
    source_organization: Mapped[str | None] = mapped_column(String(160))
    received_date: Mapped[date | None] = mapped_column(Date)
    version_label: Mapped[str | None] = mapped_column(String(120))
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

    plant: Mapped["Plant"] = relationship("Plant")
    scenario: Mapped["BusinessScenario | None"] = relationship("BusinessScenario")
    document_links: Mapped[list["PreFeedPackageDocument"]] = relationship(
        "PreFeedPackageDocument",
        back_populates="package",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PreFeedPackageDocument(Base):
    __tablename__ = "pre_feed_package_documents"
    __table_args__ = (
        UniqueConstraint("package_id", "document_id", "document_role", name="uq_pre_feed_package_document_role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(
        ForeignKey("pre_feed_packages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    document_role: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    package: Mapped[PreFeedPackage] = relationship("PreFeedPackage", back_populates="document_links")
    document: Mapped["Document"] = relationship("Document")
