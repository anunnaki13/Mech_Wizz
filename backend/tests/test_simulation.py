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
from app.models import ScenarioResult


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


def create_plant_with_emission_test(client: TestClient) -> dict:
    plant_response = client.post(
        "/api/plants/",
        json={
            "plant_name": "PLTU Simulation Test",
            "unit_name": "Unit A",
            "province": "Riau",
            "city": "Pekanbaru",
            "capacity_mw": 220,
            "fuel_type": "coal",
            "status": "active",
            "capacity_factor": 0.90,
            "operating_days_per_year": 330,
            "owner": "PLN NP",
            "data_status": "actual",
            "confidence_level": "medium",
        },
    )
    assert plant_response.status_code == 201
    plant = plant_response.json()

    emission_response = client.post(
        f"/api/plants/{plant['id']}/emission-tests",
        json={
            "stack_id": "Stack A",
            "stack_diameter_m": 3.0,
            "gas_velocity_m_s": 15.0,
            "flue_gas_temperature_c": 100,
            "co2_percent_dry": 10.0,
            "moisture_percent": 5.0,
            "data_status": "actual",
            "confidence_level": "medium",
        },
    )
    assert emission_response.status_code == 201
    return plant


def create_scenario(client: TestClient, plant_id: str) -> dict:
    response = client.post(
        f"/api/plants/{plant_id}/scenarios",
        json={
            "scenario_name": "Complete WIZ Align",
            "scheme": "align",
            "pln_ownership_percent": 25,
            "partner_capex_responsibility_percent": 100,
            "pln_capex_responsibility_percent": 0,
            "revenue_model": "equity_share_plus_asset_revenue",
            "capture_rate": 0.85,
            "process_efficiency": 0.60,
            "data_status": "user_assumption",
            "confidence_level": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()


def complete_financial_payload() -> dict:
    return {
        "methanol_price_usd_per_ton": 2000,
        "grey_methanol_price_usd_per_ton": 350,
        "hydrogen_price_usd_per_kg": 0.10,
        "electricity_price_usd_per_kwh": 0.005,
        "carbon_credit_price_idr_per_ton": 100000,
        "exchange_rate_idr_usd": 15000,
        "discount_rate": 0.10,
        "tax_rate": 0.22,
        "capex_capture_usd": 100_000_000,
        "capex_electrolyzer_usd": 200_000_000,
        "capex_methanol_plant_usd": 150_000_000,
        "capex_storage_port_usd": 50_000_000,
        "opex_percent_capex": 0.04,
        "data_status": "user_assumption",
        "confidence_level": "medium",
    }


def test_run_simulation_persists_result(client: TestClient, db_session: Session) -> None:
    plant = create_plant_with_emission_test(client)
    scenario = create_scenario(client, plant["id"])
    assumption_response = client.put(
        f"/api/scenarios/{scenario['id']}/financial-assumptions",
        json=complete_financial_payload(),
    )
    assert assumption_response.status_code == 200

    simulate_response = client.post(f"/api/scenarios/{scenario['id']}/simulate")
    assert simulate_response.status_code == 200
    result = simulate_response.json()

    assert result["scenario_id"] == scenario["id"]
    assert result["total_co2_ton_per_year"] > 0
    assert result["captured_co2_ton_per_year"] > 0
    assert result["methanol_ton_per_year"] > 0
    assert result["h2_required_ton_per_year"] > 0
    assert result["electrolyzer_required_mw"] > 0
    assert result["gross_revenue_usd_per_year"] > 0
    assert result["lcom_usd_per_ton"] is not None
    assert result["npv_usd"] is not None
    assert result["irr"] is not None
    assert result["payback_years"] is not None
    assert result["missing_inputs"] == []
    assert result["calculation_version"] == "phase2-v1"

    persisted = list(db_session.scalars(select(ScenarioResult)))
    assert len(persisted) == 1

    list_response = client.get(f"/api/scenarios/{scenario['id']}/results")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    read_response = client.get(f"/api/scenario-results/{result['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["id"] == result["id"]


def test_run_simulation_marks_missing_financial_inputs(client: TestClient) -> None:
    plant = create_plant_with_emission_test(client)
    scenario = create_scenario(client, plant["id"])

    simulate_response = client.post(f"/api/scenarios/{scenario['id']}/simulate")
    assert simulate_response.status_code == 200
    result = simulate_response.json()

    assert result["total_co2_ton_per_year"] is not None
    assert result["captured_co2_ton_per_year"] is not None
    assert result["methanol_ton_per_year"] is not None
    assert result["gross_revenue_usd_per_year"] is None
    assert result["lcom_usd_per_ton"] is None
    assert result["npv_usd"] is None
    assert result["irr"] is None
    assert result["payback_years"] is None
    assert result["confidence_level"] == "low"
    assert "financial_assumptions" in result["missing_inputs"]
