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
from app.models import BusinessScenario, Plant, ScenarioResult, UnitScoringResult
from app.seed import seed_tenayan
from app.services.scoring import confidence_score_for_status, normalize_score


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


def _seed_and_simulate(client: TestClient, db_session: Session) -> tuple[Plant, BusinessScenario, dict]:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None

    response = client.post(f"/api/scenarios/{scenario.id}/simulate")
    assert response.status_code == 200
    return plant, scenario, response.json()


def test_score_normalization_and_confidence_mapping() -> None:
    assert normalize_score(None, 0, 100) == 0.0
    assert normalize_score(-10, 0, 100) == 0.0
    assert normalize_score(50, 0, 100) == 0.5
    assert normalize_score(150, 0, 100) == 1.0
    assert confidence_score_for_status("actual") == 1.0
    assert confidence_score_for_status("estimated") == 0.70
    assert confidence_score_for_status("benchmark") == 0.55
    assert confidence_score_for_status("user_assumption") == 0.50
    assert confidence_score_for_status("partner_supplied") == 0.60
    assert confidence_score_for_status("unknown") == 0.0


def test_seed_tenayan_uses_verified_map_coordinates(db_session: Session) -> None:
    plant = seed_tenayan(db_session)

    assert plant.latitude == 0.56437
    assert plant.longitude == 101.52345


def test_recalculate_scoring_persists_scores_and_rank(client: TestClient, db_session: Session) -> None:
    plant, scenario, simulation = _seed_and_simulate(client, db_session)

    response = client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id})
    assert response.status_code == 200
    payload = response.json()

    assert payload["created_count"] == 1
    assert payload["scoring_run_id"]
    score = payload["results"][0]
    assert score["plant_id"] == plant.id
    assert score["scenario_id"] == scenario.id
    assert score["scenario_result_id"] == simulation["id"]
    assert score["rank_position"] == 1
    assert score["scoring_version"] == "phase3-scoring-v1"
    assert score["recommended_scheme"] == "WIZ Align"
    assert score["key_bottleneck"] == "Hydrogen supply strategy"
    assert 0 <= score["opportunity_score"] <= 1
    assert 0 <= score["readiness_score"] <= 1
    assert 0 <= score["confidence_score"] <= 1
    assert 0 <= score["composite_score"] <= 1
    assert 0 <= score["component_scores"]["heatmap_weight"] <= 1

    expected_composite = round(
        (0.45 * score["opportunity_score"])
        + (0.35 * score["readiness_score"])
        + (0.20 * score["confidence_score"]),
        4,
    )
    assert score["composite_score"] == expected_composite

    persisted = list(db_session.scalars(select(UnitScoringResult)))
    assert len(persisted) == 1
    assert persisted[0].rank_position == 1


def test_ranking_geojson_and_profile_api(client: TestClient, db_session: Session) -> None:
    plant, scenario, _ = _seed_and_simulate(client, db_session)
    recalc_response = client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id})
    assert recalc_response.status_code == 200

    ranking_response = client.get(f"/api/scoring/unit-ranking?scenario_id={scenario.id}&scheme=align")
    assert ranking_response.status_code == 200
    ranking = ranking_response.json()
    assert len(ranking) == 1
    assert ranking[0]["rank"] == 1
    assert ranking[0]["plant_id"] == plant.id
    assert ranking[0]["site_id"] == plant.id
    assert ranking[0]["site_name"] == "PLTU Tenayan"
    assert ranking[0]["co2_tpy"] is not None
    assert ranking[0]["captured_co2_tpy"] is not None
    assert ranking[0]["methanol_tpy"] is not None
    assert ranking[0]["estimated_irr"] is None
    assert ranking[0]["data_confidence_label"] in {"Low", "Medium", "High", "Unknown"}

    geojson_response = client.get(f"/api/map/unit-opportunity?scenario_id={scenario.id}")
    assert geojson_response.status_code == 200
    geojson = geojson_response.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1
    feature = geojson["features"][0]
    assert feature["geometry"]["coordinates"] == [101.52345, 0.56437]
    assert feature["properties"]["site_id"] == plant.id
    assert feature["properties"]["heatmap_weight"] == ranking[0]["heatmap_weight"]
    assert feature["properties"]["key_bottleneck"] == "Hydrogen supply strategy"

    profile_response = client.get(f"/api/units/{plant.id}/profile?scenario_id={scenario.id}")
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["plant"]["id"] == plant.id
    assert profile["scenario"]["id"] == scenario.id
    assert profile["latest_result"]["id"] is not None
    assert profile["latest_scoring"]["rank_position"] == 1
    assert profile["score_breakdown"]["opportunity_level"] in {"low", "medium", "high", "priority"}
    assert any(gap["module"] == "hydrogen" for gap in profile["data_gaps"])


def test_scoring_recalculate_skips_scenarios_without_results(client: TestClient, db_session: Session) -> None:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None

    response = client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id})
    assert response.status_code == 200
    assert response.json()["created_count"] == 0
    assert list(db_session.scalars(select(ScenarioResult))) == []
