import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import models  # noqa: E402,F401
from app.database import Base, get_db
from app.main import app
from app.models import EmissionTest, Plant
from app.seed import seed_tenayan


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


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_plant(client: TestClient) -> dict:
    response = client.post(
        "/api/plants/",
        json={
            "plant_name": "PLTU Test",
            "unit_name": "Unit A",
            "province": "Riau",
            "city": "Pekanbaru",
            "capacity_mw": 100,
            "fuel_type": "coal",
            "status": "active",
            "data_status": "actual",
            "confidence_level": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_list_update_delete_emission_test(client: TestClient) -> None:
    plant = create_plant(client)
    payload = {
        "stack_id": "Chimney Test",
        "test_date": "2026-05-01",
        "lab_name": "Internal Lab",
        "stack_diameter_m": 3.0,
        "gas_velocity_m_s": 14.2,
        "flue_gas_temperature_c": 121,
        "co2_percent_dry": 8.1,
        "o2_percent": 10.2,
        "moisture_percent": 5.9,
        "so2_mg_nm3": 210,
        "nox_mg_nm3": 250,
        "particulate_mg_nm3": 50,
        "data_status": "actual",
        "confidence_level": "medium",
    }

    create_response = client.post(f"/api/plants/{plant['id']}/emission-tests", json=payload)
    assert create_response.status_code == 201
    emission_test = create_response.json()
    assert emission_test["co2_percent_dry"] == 8.1
    assert emission_test["confidence_level"] == "medium"

    list_response = client.get(f"/api/plants/{plant['id']}/emission-tests")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.put(
        f"/api/emission-tests/{emission_test['id']}",
        json={"co2_percent_dry": 8.4, "confidence_level": "high"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["co2_percent_dry"] == 8.4
    assert update_response.json()["confidence_level"] == "high"

    delete_response = client.delete(f"/api/emission-tests/{emission_test['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/plants/{plant['id']}/emission-tests").json() == []


def test_seed_tenayan_emission_tests_idempotent(db_session: Session) -> None:
    seed_tenayan(db_session)
    seed_tenayan(db_session)

    plant = db_session.scalar(select(Plant).where(Plant.plant_name == "PLTU Tenayan"))
    assert plant is not None

    emission_tests = list(
        db_session.scalars(
            select(EmissionTest).where(EmissionTest.plant_id == plant.id).order_by(EmissionTest.stack_id)
        )
    )
    assert len(emission_tests) == 2
    assert [record.stack_id for record in emission_tests] == ["Chimney #1", "Chimney #2"]
    assert emission_tests[0].co2_percent_dry == 8.48
    assert emission_tests[1].co2_percent_dry == 3.54
    assert all(record.data_status == "actual" for record in emission_tests)
