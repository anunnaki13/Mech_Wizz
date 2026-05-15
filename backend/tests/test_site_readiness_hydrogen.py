import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import models  # noqa: E402,F401
from app.database import Base, get_db
from app.main import app


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
            "plant_name": "PLTU Readiness Test",
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


def test_site_readiness_create_get_update(client: TestClient) -> None:
    plant = create_plant(client)
    payload = {
        "available_land_ha": 12.5,
        "land_status": "inside existing plant boundary",
        "distance_to_stack_km": 0.4,
        "has_port_or_jetty": False,
        "distance_to_port_km": 8.2,
        "road_access": "existing plant road",
        "water_availability": "requires confirmation",
        "power_availability": "available from plant auxiliary supply",
        "utility_readiness": "partial",
        "permit_risk": "medium",
        "social_risk": "low",
        "data_status": "estimated",
        "confidence_level": "low",
    }

    create_response = client.post(f"/api/plants/{plant['id']}/site-readiness", json=payload)
    assert create_response.status_code == 201
    record = create_response.json()
    assert record["available_land_ha"] == 12.5

    get_response = client.get(f"/api/plants/{plant['id']}/site-readiness")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == record["id"]

    update_response = client.put(
        f"/api/site-readiness/{record['id']}",
        json={"available_land_ha": 14.0, "confidence_level": "medium"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["available_land_ha"] == 14.0
    assert update_response.json()["confidence_level"] == "medium"


def test_hydrogen_strategy_create_get_update(client: TestClient) -> None:
    plant = create_plant(client)
    payload = {
        "existing_h2_available": False,
        "h2_strategy": "future green hydrogen partner supply",
        "h2_cost_case": "partner supplied estimate",
        "h2_cost_usd_per_kg": 4.5,
        "h2_readiness_score": 35,
        "data_status": "estimated",
        "confidence_level": "low",
    }

    create_response = client.post(f"/api/plants/{plant['id']}/hydrogen-strategy", json=payload)
    assert create_response.status_code == 201
    record = create_response.json()
    assert record["h2_strategy"] == "future green hydrogen partner supply"

    get_response = client.get(f"/api/plants/{plant['id']}/hydrogen-strategy")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == record["id"]

    update_response = client.put(
        f"/api/hydrogen-strategy/{record['id']}",
        json={"h2_readiness_score": 45, "confidence_level": "medium"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["h2_readiness_score"] == 45
    assert update_response.json()["confidence_level"] == "medium"
