import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SiteReadiness(Base):
    __tablename__ = "site_readiness"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), unique=True, nullable=False)
    available_land_ha: Mapped[float | None] = mapped_column(Float)
    land_status: Mapped[str | None] = mapped_column(String(120))
    distance_to_stack_km: Mapped[float | None] = mapped_column(Float)
    has_port_or_jetty: Mapped[bool | None] = mapped_column(Boolean)
    distance_to_port_km: Mapped[float | None] = mapped_column(Float)
    port_capacity_dwt: Mapped[float | None] = mapped_column(Float)
    road_access: Mapped[str | None] = mapped_column(String(160))
    water_availability: Mapped[str | None] = mapped_column(String(160))
    power_availability: Mapped[str | None] = mapped_column(String(160))
    utility_readiness: Mapped[str | None] = mapped_column(String(160))
    permit_risk: Mapped[str | None] = mapped_column(String(80))
    social_risk: Mapped[str | None] = mapped_column(String(80))
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="site_readiness")
