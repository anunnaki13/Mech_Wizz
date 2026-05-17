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
from app.models import BusinessScenario
from app.seed import seed_tenayan
from app.services import shortlist
from app.services.port_intelligence import normalize_wpi_port


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


@pytest.fixture(autouse=True)
def deterministic_ports(monkeypatch: pytest.MonkeyPatch) -> None:
    port = normalize_wpi_port(
        {
            "portNumber": 1,
            "portName": "Validation Port",
            "countryCode": "ID",
            "countryName": "Indonesia",
            "xcoord": 101.6,
            "ycoord": 0.55,
            "harborSize": "L",
            "harborType": "CN",
            "chDepth": "14",
            "anDepth": "12",
            "loWharves": "Y",
            "loContainer": "Y",
            "loLiquidBulk": "Y",
            "firstPortOfEntry": "Y",
            "tugsAssist": "Y",
            "cmRadio": "Y",
            "turningArea": "Y",
            "etaMessage": "Y",
        }
    )
    assert port is not None
    monkeypatch.setattr(shortlist, "load_wpi_ports", lambda _: (port,))


def test_shortlist_empty_state_returns_empty_matrix(client: TestClient) -> None:
    response = client.get("/api/shortlist/decision-matrix")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["candidate_count"] == 0
    assert payload["summary"]["top_candidate"] is None
    assert payload["candidates"] == []
    assert payload["weights"]["screening"] == 0.35


def test_shortlist_decision_matrix_returns_ranked_candidate(
    client: TestClient,
    db_session: Session,
) -> None:
    plant = seed_tenayan(db_session)
    scenario = db_session.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None
    assert client.post(f"/api/scenarios/{scenario.id}/simulate").status_code == 200
    assert client.post("/api/scoring/recalculate", json={"scenario_id": scenario.id}).status_code == 200

    response = client.get("/api/shortlist/decision-matrix?scheme=align&top_n=5")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["candidate_count"] == 1
    assert payload["summary"]["top_candidate"] == "PLTU Tenayan"
    candidate = payload["candidates"][0]
    assert candidate["shortlist_rank"] == 1
    assert candidate["recommendation"] == "shortlist_top3"
    assert candidate["plant_id"] == plant.id
    assert candidate["nearest_port_name"] == "Validation Port"
    assert candidate["nearest_port_distance_km"] is not None
    assert candidate["score_breakdown"]["final_score"] > 0
    assert 0 <= candidate["score_breakdown"]["logistics_score"] <= 1
    assert candidate["next_actions"]
