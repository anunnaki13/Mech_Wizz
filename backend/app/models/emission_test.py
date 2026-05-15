import uuid
from datetime import date

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmissionTest(Base):
    __tablename__ = "emission_tests"
    __table_args__ = (UniqueConstraint("plant_id", "stack_id", name="uq_emission_tests_plant_stack"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id: Mapped[str] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    stack_id: Mapped[str] = mapped_column(String(120), nullable=False)
    test_date: Mapped[date | None] = mapped_column(Date)
    lab_name: Mapped[str | None] = mapped_column(String(160))
    stack_diameter_m: Mapped[float | None] = mapped_column(Float)
    gas_velocity_m_s: Mapped[float | None] = mapped_column(Float)
    flue_gas_temperature_c: Mapped[float | None] = mapped_column(Float)
    co2_percent_dry: Mapped[float | None] = mapped_column(Float)
    o2_percent: Mapped[float | None] = mapped_column(Float)
    moisture_percent: Mapped[float | None] = mapped_column(Float)
    so2_mg_nm3: Mapped[float | None] = mapped_column(Float)
    nox_mg_nm3: Mapped[float | None] = mapped_column(Float)
    particulate_mg_nm3: Mapped[float | None] = mapped_column(Float)
    hg_mg_nm3: Mapped[float | None] = mapped_column(Float)
    compliance_status: Mapped[str | None] = mapped_column(String(80))
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="emission_tests")
