import uuid

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DataGap(Base):
    __tablename__ = "data_gaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[str | None] = mapped_column(ForeignKey("business_scenarios.id", ondelete="CASCADE"), index=True)
    source_module: Mapped[str] = mapped_column(String(100), nullable=False)
    missing_data_name: Mapped[str] = mapped_column(String(255), nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False)
    priority_level: Mapped[str] = mapped_column(String(50), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    plant: Mapped["Plant"] = relationship("Plant", back_populates="data_gaps")
    scenario: Mapped["BusinessScenario | None"] = relationship("BusinessScenario", back_populates="data_gaps")
