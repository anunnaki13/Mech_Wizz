import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import models  # noqa: E402,F401
from app.database import Base
from app.import_target_pltu import TARGET_PLTU_SITES, import_curated_pltu_dataset
from app.models import (
    BusinessScenario,
    EmissionTest,
    Plant,
    ScenarioResult,
    SiteReadiness,
    UnitScoringResult,
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _plant_by_name(db: Session, name: str) -> Plant:
    plant = db.scalar(select(Plant).where(Plant.plant_name == name))
    assert plant is not None
    return plant


def test_curated_import_replaces_dataset_with_target_pltu_sites(db_session: Session) -> None:
    db_session.add(
        Plant(
            plant_name="Old PLTU Suralaya",
            unit_name="Unit old",
            capacity_mw=400,
            data_status="estimated",
            confidence_level="low",
        )
    )
    db_session.commit()

    result = import_curated_pltu_dataset(db_session, clear_existing=True)

    plants = list(db_session.scalars(select(Plant)))
    assert result["plants_deleted"] == 1
    assert result["plants_created"] == 26
    assert len(plants) == 26
    assert {plant.plant_name for plant in plants} == {site.plant_name for site in TARGET_PLTU_SITES}
    assert all(plant.unit_name == "Site aggregate" for plant in plants)
    assert not any("Suralaya" in plant.plant_name for plant in plants)
    assert sum(plant.capacity_mw or 0 for plant in plants) == pytest.approx(6503.8)


def test_curated_import_creates_simulation_and_scoring_inputs(db_session: Session) -> None:
    result = import_curated_pltu_dataset(db_session, clear_existing=True)

    assert result["failed_simulations"] == []
    assert len(list(db_session.scalars(select(BusinessScenario)))) == 26
    assert len(list(db_session.scalars(select(EmissionTest)))) == 26
    assert len(list(db_session.scalars(select(SiteReadiness)))) == 26
    assert len(list(db_session.scalars(select(ScenarioResult)))) == 26
    assert len(list(db_session.scalars(select(UnitScoringResult)))) == 26
    assert result["scoring_records_created"] == 26

    tenayan = _plant_by_name(db_session, "UP Tenayan")
    assert tenayan.latitude == pytest.approx(0.56437)
    assert tenayan.longitude == pytest.approx(101.52345)

    paiton = _plant_by_name(db_session, "UP Paiton")
    assert paiton.capacity_mw == 1460
    assert paiton.latitude == pytest.approx(-7.713041)
    assert paiton.longitude == pytest.approx(113.578536)

    suge = _plant_by_name(db_session, "PLTU Belitung / Suge")
    assert suge.latitude == pytest.approx(-2.8932592)
    assert suge.longitude == pytest.approx(107.5638809)

    ampana = _plant_by_name(db_session, "PLTU Ampana")
    assert ampana.confidence_level == "low"


def test_curated_import_uses_regulatory_bme_benchmark(db_session: Session) -> None:
    import_curated_pltu_dataset(db_session, clear_existing=True)

    emission = db_session.scalar(select(EmissionTest).join(Plant).where(Plant.plant_name == "UP Tenayan"))
    assert emission is not None
    assert emission.so2_mg_nm3 == 550
    assert emission.nox_mg_nm3 == 550
    assert emission.particulate_mg_nm3 == 100
    assert emission.hg_mg_nm3 == pytest.approx(0.03)
    assert emission.data_status == "benchmark"
    assert emission.compliance_status == "Permen LHK P.15/2019 existing-coal BME"
