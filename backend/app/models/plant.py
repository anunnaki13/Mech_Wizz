import uuid

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Plant(Base):
    __tablename__ = "plants"
    __table_args__ = (UniqueConstraint("plant_name", "unit_name", name="uq_plants_name_unit"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_name: Mapped[str] = mapped_column(String(160), nullable=False)
    unit_name: Mapped[str] = mapped_column(String(120), nullable=False)
    province: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    capacity_mw: Mapped[float | None] = mapped_column(Float)
    fuel_type: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str | None] = mapped_column(String(80))
    capacity_factor: Mapped[float | None] = mapped_column(Float)
    operating_days_per_year: Mapped[int | None] = mapped_column(Integer)
    owner: Mapped[str | None] = mapped_column(String(160))
    data_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    confidence_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    emission_tests: Mapped[list["EmissionTest"]] = relationship(
        "EmissionTest",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    site_readiness: Mapped["SiteReadiness | None"] = relationship(
        "SiteReadiness",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    hydrogen_strategy: Mapped["HydrogenStrategy | None"] = relationship(
        "HydrogenStrategy",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    business_scenarios: Mapped[list["BusinessScenario"]] = relationship(
        "BusinessScenario",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    unit_scoring_results: Mapped[list["UnitScoringResult"]] = relationship(
        "UnitScoringResult",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
