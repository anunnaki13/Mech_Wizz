import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HydrogenStrategy(Base):
    __tablename__ = "hydrogen_strategies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), unique=True, nullable=False)
    existing_h2_available: Mapped[bool | None] = mapped_column(Boolean)
    h2_strategy: Mapped[str | None] = mapped_column(String(180))
    h2_cost_case: Mapped[str | None] = mapped_column(String(120))
    h2_cost_usd_per_kg: Mapped[float | None] = mapped_column(Float)
    h2_readiness_score: Mapped[float | None] = mapped_column(Float)
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="hydrogen_strategy")
