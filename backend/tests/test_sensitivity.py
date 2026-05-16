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
from app.models import BusinessScenario, FinancialAssumption, SensitivityResult
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


def _seed_scenario(db_session: Session) -> BusinessScenario:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None
    return scenario


def _make_financial_assumptions_complete(db_session: Session, scenario_id: str) -> None:
    assumption = db_session.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario_id))
    assert assumption is not None
    assumption.methanol_price_usd_per_ton = 2000
    assumption.hydrogen_price_usd_per_kg = 0.10
    assumption.electricity_price_usd_per_kwh = 0.005
    assumption.carbon_credit_price_idr_per_ton = 100000
    assumption.exchange_rate_idr_usd = 15000
    assumption.discount_rate = 0.10
    assumption.tax_rate = 0.22
    assumption.capex_capture_usd = 10_000_000
    assumption.capex_electrolyzer_usd = 10_000_000
    assumption.capex_methanol_plant_usd = 10_000_000
    assumption.capex_storage_port_usd = 5_000_000
    assumption.opex_percent_capex = 0.04
    assumption.data_status = "user_assumption"
    assumption.confidence_level = "medium"
    db_session.commit()


def test_run_sensitivity_persists_all_variables_with_complete_assumptions(
    client: TestClient,
    db_session: Session,
) -> None:
    scenario = _seed_scenario(db_session)
    _make_financial_assumptions_complete(db_session, scenario.id)
    simulate_response = client.post(f"/api/scenarios/{scenario.id}/simulate")
    assert simulate_response.status_code == 200

    run_response = client.post("/api/sensitivity/run", json={"scenario_id": scenario.id})
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["run_id"]
    assert payload["scenario_id"] == scenario.id
    assert len(payload["results"]) == 8

    h2_result = next(item for item in payload["results"] if item["variable_name"] == "h2_price")
    assert h2_result["base_input_value"] == 0.10
    assert h2_result["low_lcom_usd_per_ton"] is not None
    assert h2_result["high_lcom_usd_per_ton"] is not None
    assert h2_result["impact_score"] >= 0
    assert h2_result["missing_inputs"] == []

    persisted = list(db_session.scalars(select(SensitivityResult)))
    assert len(persisted) == 8

    list_response = client.get(f"/api/scenarios/{scenario.id}/sensitivity")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 8


def test_run_sensitivity_returns_warnings_for_missing_capex(
    client: TestClient,
    db_session: Session,
) -> None:
    scenario = _seed_scenario(db_session)
    simulate_response = client.post(f"/api/scenarios/{scenario.id}/simulate")
    assert simulate_response.status_code == 200

    run_response = client.post(
        "/api/sensitivity/run",
        json={"scenario_id": scenario.id, "variables": ["capex", "methanol_price"]},
    )
    assert run_response.status_code == 200
    payload = run_response.json()

    assert len(payload["results"]) == 2
    capex_result = next(item for item in payload["results"] if item["variable_name"] == "capex")
    assert capex_result["base_input_value"] is None
    assert capex_result["base_irr"] is None
    assert capex_result["base_lcom_usd_per_ton"] is None
    assert capex_result["confidence_level"] == "low"
    assert "financial_assumptions.capex_capture_usd" in capex_result["missing_inputs"]
    assert any("incomplete" in warning for warning in capex_result["warnings"])
