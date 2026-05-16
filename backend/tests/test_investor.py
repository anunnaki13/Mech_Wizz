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
from app.models import BusinessScenario, Plant
from app.seed import seed_tenayan
from app.services.investor_case import build_investor_case


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


def _seed_phase3_outputs(client: TestClient, db_session: Session) -> tuple[Plant, BusinessScenario]:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None

    simulate_response = client.post(f"/api/scenarios/{scenario.id}/simulate")
    assert simulate_response.status_code == 200
    scoring_response = client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id})
    assert scoring_response.status_code == 200
    sensitivity_response = client.post("/api/sensitivity/run", json={"scenario_id": scenario.id, "plant_id": plant.id})
    assert sensitivity_response.status_code == 200
    return plant, scenario


def test_build_investor_case_aggregates_phase3_outputs(client: TestClient, db_session: Session) -> None:
    plant, scenario = _seed_phase3_outputs(client, db_session)

    investor_case = build_investor_case(db_session, plant_id=plant.id, scenario_id=scenario.id)

    assert investor_case["plant"]["id"] == plant.id
    assert investor_case["scenario"]["id"] == scenario.id
    assert investor_case["kpis"]["e_methanol_capacity_tpy"] is not None
    assert investor_case["kpis"]["co2_abatement_tpy"] is not None
    assert investor_case["kpis"]["project_irr"] is None
    assert investor_case["kpis"]["estimated_npv_usd"] is None
    assert investor_case["capex_structure"]["is_complete"] is False
    assert investor_case["revenue_mix"][0]["label"] == "E-methanol sales"
    assert investor_case["revenue_mix"][0]["value_usd_per_year"] is not None
    assert len(investor_case["scenario_comparison"]) == 3
    assert investor_case["scenario_comparison"][1]["scheme"] == "align"
    assert investor_case["thesis_flow"][0]["stage"] == "Assets & Advantages"
    assert any("Investment" not in item["stage"] for item in investor_case["thesis_flow"])
    assert any(gap["module"] == "capex" for gap in investor_case["data_gaps"])
    assert investor_case["sensitivity"]["dominant_driver"] is not None
    assert investor_case["confidence_level"] == "low"
    assert any("CAPEX structure is incomplete" in warning for warning in investor_case["warnings"])


def test_investor_case_api_returns_dashboard_payload(client: TestClient, db_session: Session) -> None:
    plant, scenario = _seed_phase3_outputs(client, db_session)

    response = client.get(f"/api/investor-case?plant_id={plant.id}&scenario_id={scenario.id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["plant"]["plant_name"] == "PLTU Tenayan"
    assert payload["scenario"]["scenario_name"] == "WIZ Align Base Case"
    assert payload["kpis"]["lcom_usd_per_ton"] is None
    assert payload["capex_structure"]["model"] == "WIZ Align"
    assert len(payload["risks"]) >= 1
    assert len(payload["roadmap"]) == 5
    assert len(payload["why_this_wins"]) >= 4
    assert payload["data_quality"]["output_confidence"]["investor_case"] == "low"


def test_investor_case_api_can_default_to_seeded_plant_and_scenario(
    client: TestClient,
    db_session: Session,
) -> None:
    _seed_phase3_outputs(client, db_session)

    response = client.get("/api/investor-case")

    assert response.status_code == 200
    assert response.json()["plant"]["plant_name"] == "PLTU Tenayan"
