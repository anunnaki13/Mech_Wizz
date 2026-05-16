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
from app.models import BusinessScenario, FinancialAssumption, Plant
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
            "plant_name": "PLTU Scenario Test",
            "unit_name": "Unit A",
            "province": "Riau",
            "city": "Pekanbaru",
            "capacity_mw": 100,
            "fuel_type": "coal",
            "status": "active",
            "capacity_factor": 0.70,
            "operating_days_per_year": 300,
            "owner": "PLN NP",
            "data_status": "actual",
            "confidence_level": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()


def scenario_payload(name: str = "WIZ Align Test") -> dict:
    return {
        "scenario_name": name,
        "scheme": "align",
        "pln_ownership_percent": 25,
        "partner_capex_responsibility_percent": 100,
        "pln_capex_responsibility_percent": 0,
        "revenue_model": "equity_share_plus_asset_revenue",
        "capture_rate": 0.85,
        "process_efficiency": 0.60,
        "data_status": "user_assumption",
        "confidence_level": "medium",
    }


def financial_payload() -> dict:
    return {
        "methanol_price_usd_per_ton": 1250,
        "grey_methanol_price_usd_per_ton": 350,
        "hydrogen_price_usd_per_kg": 3.0,
        "electricity_price_usd_per_kwh": 0.06,
        "carbon_credit_price_idr_per_ton": 58800,
        "exchange_rate_idr_usd": 17500,
        "discount_rate": 0.10,
        "tax_rate": 0.22,
        "capex_capture_usd": None,
        "capex_electrolyzer_usd": None,
        "capex_methanol_plant_usd": None,
        "capex_storage_port_usd": None,
        "opex_percent_capex": 0.04,
        "data_status": "benchmark",
        "confidence_level": "low",
    }


def test_create_list_update_delete_business_scenario(client: TestClient) -> None:
    plant = create_plant(client)

    create_response = client.post(f"/api/plants/{plant['id']}/scenarios", json=scenario_payload())
    assert create_response.status_code == 201
    scenario = create_response.json()
    assert scenario["plant_id"] == plant["id"]
    assert scenario["scheme"] == "align"
    assert scenario["capture_rate"] == 0.85

    list_response = client.get(f"/api/plants/{plant['id']}/scenarios")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    read_response = client.get(f"/api/scenarios/{scenario['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["scenario_name"] == "WIZ Align Test"

    update_response = client.put(
        f"/api/scenarios/{scenario['id']}",
        json={"scenario_name": "WIZ Access Test", "scheme": "access", "pln_ownership_percent": 0},
    )
    assert update_response.status_code == 200
    assert update_response.json()["scheme"] == "access"
    assert update_response.json()["pln_ownership_percent"] == 0

    delete_response = client.delete(f"/api/scenarios/{scenario['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/scenarios/{scenario['id']}").status_code == 404


def test_financial_assumption_create_get_update(client: TestClient) -> None:
    plant = create_plant(client)
    scenario_response = client.post(f"/api/plants/{plant['id']}/scenarios", json=scenario_payload())
    scenario_id = scenario_response.json()["id"]

    empty_response = client.get(f"/api/scenarios/{scenario_id}/financial-assumptions")
    assert empty_response.status_code == 200
    assert empty_response.json() is None

    create_response = client.post(f"/api/scenarios/{scenario_id}/financial-assumptions", json=financial_payload())
    assert create_response.status_code == 201
    record = create_response.json()
    assert record["methanol_price_usd_per_ton"] == 1250
    assert record["capex_capture_usd"] is None

    read_response = client.get(f"/api/scenarios/{scenario_id}/financial-assumptions")
    assert read_response.status_code == 200
    assert read_response.json()["id"] == record["id"]

    update_response = client.put(
        f"/api/scenarios/{scenario_id}/financial-assumptions",
        json={"methanol_price_usd_per_ton": 1300, "confidence_level": "medium"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["methanol_price_usd_per_ton"] == 1300
    assert update_response.json()["confidence_level"] == "medium"


def test_seed_tenayan_scenario_idempotent(db_session: Session) -> None:
    first = seed_tenayan(db_session)
    second = seed_tenayan(db_session)

    plants = list(db_session.scalars(select(Plant)))
    scenarios = list(db_session.scalars(select(BusinessScenario)))
    assumptions = list(db_session.scalars(select(FinancialAssumption)))

    assert first.id == second.id
    assert len(plants) == 1
    assert len(scenarios) == 1
    assert len(assumptions) == 1
    assert scenarios[0].scenario_name == "WIZ Align Base Case"
    assert scenarios[0].scheme == "align"
    assert assumptions[0].methanol_price_usd_per_ton == 1250
    assert assumptions[0].opex_percent_capex == 0.04
