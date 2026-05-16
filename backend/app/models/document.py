import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str | None] = mapped_column(ForeignKey("plants.id", ondelete="SET NULL"), index=True)
    scenario_id: Mapped[str | None] = mapped_column(ForeignKey("business_scenarios.id", ondelete="SET NULL"), index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    document_category: Mapped[str | None] = mapped_column(String(120))
    upload_status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    extraction_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    extracted_text: Mapped[str | None] = mapped_column(Text)
    extraction_error: Mapped[str | None] = mapped_column(Text)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    insights: Mapped[list["LlmInsight"]] = relationship("LlmInsight", back_populates="document")
