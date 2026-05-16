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
from app.models import BusinessScenario, DataGap, Plant
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


def test_settings_api_seeds_defaults_and_updates_weights(client: TestClient) -> None:
    response = client.get("/api/settings")
    assert response.status_code == 200
    settings = response.json()

    keys = {record["key"] for record in settings}
    assert keys == {"default_financial_assumptions", "scoring_weights"}

    valid_payload = {
        "value": {
            "composite": {"opportunity": 0.50, "readiness": 0.30, "confidence": 0.20},
            "heatmap": {
                "opportunity": 0.40,
                "readiness": 0.30,
                "economic_return": 0.20,
                "confidence": 0.10,
            },
        },
        "data_status": "user_assumption",
        "confidence_level": "medium",
    }
    update_response = client.put("/api/settings/scoring_weights", json=valid_payload)
    assert update_response.status_code == 200
    assert update_response.json()["value"]["composite"]["opportunity"] == 0.50

    invalid_payload = {
        **valid_payload,
        "value": {
            "composite": {"opportunity": 0.50, "readiness": 0.30, "confidence": 0.20},
            "heatmap": {"opportunity": 0.40, "readiness": 0.30, "economic_return": 0.20},
        },
    }
    invalid_response = client.put("/api/settings/scoring_weights", json=invalid_payload)
    assert invalid_response.status_code == 400
    assert "sum to 1.0" in invalid_response.json()["detail"]


def test_openrouter_settings_mask_api_key_and_exclude_secret_from_generic_settings(client: TestClient) -> None:
    initial_response = client.get("/api/settings/openrouter/provider")
    assert initial_response.status_code == 200
    assert initial_response.json()["api_key_source"] in {"missing", "environment"}

    update_response = client.put(
        "/api/settings/openrouter/provider",
        json={
            "api_key": "dummy-openrouter-key",
            "model": "openai/gpt-5.2",
            "base_url": "https://openrouter.ai/api/v1",
            "site_url": "http://localhost:3000",
            "app_name": "MECH WIZ AI Digital Twin",
        },
    )
    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["has_api_key"] is True
    assert payload["api_key_source"] == "stored"
    assert payload["api_key_masked"] != "dummy-openrouter-key"
    assert payload["model"] == "openai/gpt-5.2"

    generic_response = client.get("/api/settings")
    assert generic_response.status_code == 200
    serialized = str(generic_response.json())
    assert "openrouter_provider" not in serialized
    assert "dummy-openrouter-key" not in serialized

    hidden_response = client.get("/api/settings/openrouter_provider")
    assert hidden_response.status_code == 404

    clear_response = client.put("/api/settings/openrouter/provider", json={"clear_api_key": True})
    assert clear_response.status_code == 200
    assert clear_response.json()["api_key_source"] in {"missing", "environment"}


def test_updated_scoring_weights_affect_scoring_recalculation(
    client: TestClient,
    db_session: Session,
) -> None:
    plant, scenario = _seed_phase3_outputs(client, db_session)
    seed_settings_response = client.get("/api/settings")
    assert seed_settings_response.status_code == 200

    update_response = client.put(
        "/api/settings/scoring_weights",
        json={
            "value": {
                "composite": {"opportunity": 1.0, "readiness": 0.0, "confidence": 0.0},
                "heatmap": {
                    "opportunity": 0.40,
                    "readiness": 0.30,
                    "economic_return": 0.20,
                    "confidence": 0.10,
                },
            },
            "data_status": "user_assumption",
            "confidence_level": "medium",
        },
    )
    assert update_response.status_code == 200

    scoring_response = client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id})
    assert scoring_response.status_code == 200
    score = scoring_response.json()["results"][0]

    assert score["plant_id"] == plant.id
    assert score["composite_score"] == score["opportunity_score"]
    assert score["component_scores"]["composite_weights"]["opportunity"] == 1.0


def test_data_quality_summary_persists_idempotent_gap_recommendations(
    client: TestClient,
    db_session: Session,
) -> None:
    plant, scenario = _seed_phase3_outputs(client, db_session)

    first_response = client.get(f"/api/data-quality/summary?plant_id={plant.id}&scenario_id={scenario.id}")
    assert first_response.status_code == 200
    summary = first_response.json()

    assert summary["plant_id"] == plant.id
    assert summary["scenario_id"] == scenario.id
    assert summary["input_status"]["plant"] == "actual"
    assert summary["input_status"]["financial_assumptions"] == "benchmark"
    assert summary["output_confidence"]["scenario_result"] == "low"
    assert summary["output_confidence"]["scoring"] in {"low", "medium"}
    gap_modules = {gap["source_module"] for gap in summary["gaps"]}
    assert {"hydrogen", "capex"}.issubset(gap_modules)
    assert all(gap["recommendation"] for gap in summary["gaps"])

    first_count = len(list(db_session.scalars(select(DataGap))))
    second_response = client.get(f"/api/data-quality/summary?plant_id={plant.id}&scenario_id={scenario.id}")
    assert second_response.status_code == 200
    second_count = len(list(db_session.scalars(select(DataGap))))
    assert second_count == first_count
