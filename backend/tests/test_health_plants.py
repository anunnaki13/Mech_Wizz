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
from app.models import Plant
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


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_list_read_update_delete_plant(client: TestClient) -> None:
    payload = {
        "plant_name": "PLTU Test",
        "unit_name": "Unit A",
        "province": "Riau",
        "city": "Pekanbaru",
        "capacity_mw": 100,
        "fuel_type": "coal",
        "status": "active",
        "capacity_factor": 0.72,
        "operating_days_per_year": 300,
        "owner": "PLN NP",
        "data_status": "actual",
        "confidence_level": "high",
    }

    create_response = client.post("/api/plants/", json=payload)
    assert create_response.status_code == 201
    plant = create_response.json()
    assert plant["data_status"] == "actual"

    list_response = client.get("/api/plants/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    read_response = client.get(f"/api/plants/{plant['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["plant_name"] == "PLTU Test"

    update_response = client.put(f"/api/plants/{plant['id']}", json={"confidence_level": "medium"})
    assert update_response.status_code == 200
    assert update_response.json()["confidence_level"] == "medium"

    delete_response = client.delete(f"/api/plants/{plant['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/plants/{plant['id']}").status_code == 404


def test_seed_tenayan(db_session: Session) -> None:
    first = seed_tenayan(db_session)
    second = seed_tenayan(db_session)

    plants = list(db_session.scalars(select(Plant)))
    assert len(plants) == 1
    assert first.id == second.id
    assert second.plant_name == "PLTU Tenayan"
    assert second.unit_name == "Unit 1-2"
    assert second.capacity_mw == 220
    assert second.data_status == "actual"
    assert second.confidence_level == "medium"
