import uuid
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LlmInsight(Base):
    __tablename__ = "llm_insights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str | None] = mapped_column(ForeignKey("plants.id", ondelete="SET NULL"), index=True)
    scenario_id: Mapped[str | None] = mapped_column(ForeignKey("business_scenarios.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    insight_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    provider_response_id: Mapped[str | None] = mapped_column(String(160))
    usage: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    document: Mapped["Document | None"] = relationship("Document", back_populates="insights")
