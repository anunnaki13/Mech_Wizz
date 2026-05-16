import os
from collections.abc import Generator

import httpx
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
from app.models import BusinessScenario, LlmInsight, Plant
from app.seed import seed_tenayan
from app.services.llm import build_prompt, generate_insight


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


class FakeOpenRouterTransport:
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict,
        timeout: float,
    ) -> httpx.Response:
        assert url.endswith("/chat/completions")
        assert headers["Authorization"] == "Bearer test-key"
        assert json["messages"][1]["content"]
        return httpx.Response(
            200,
            json={
                "id": "or-test-response",
                "model": json["model"],
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": "Ringkasan eksekutif berbasis data tersimpan.",
                        },
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            },
            request=httpx.Request("POST", url),
        )


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


def test_prompt_builder_separates_context_and_forbids_invented_numbers(
    client: TestClient,
    db_session: Session,
) -> None:
    _, scenario = _seed_phase3_outputs(client, db_session)

    prompt, plant_id, scenario_id, document_id = build_prompt(
        db_session,
        "executive_summary",
        scenario_id=scenario.id,
    )

    assert plant_id == scenario.plant_id
    assert scenario_id == scenario.id
    assert document_id is None
    assert "Do not invent numbers" in prompt
    assert "actual_data" in prompt
    assert "assumptions" in prompt
    assert "confidence" in prompt
    assert "data_gaps" in prompt


def test_generate_insight_persists_prompt_response_and_usage(
    client: TestClient,
    db_session: Session,
) -> None:
    _, scenario = _seed_phase3_outputs(client, db_session)

    insight = generate_insight(
        db_session,
        "investor_memo",
        scenario_id=scenario.id,
        api_key="test-key",
        transport=FakeOpenRouterTransport(),
    )

    assert insight.status == "completed"
    assert insight.scenario_id == scenario.id
    assert insight.insight_type == "investor_memo"
    assert insight.response_text == "Ringkasan eksekutif berbasis data tersimpan."
    assert insight.provider_response_id == "or-test-response"
    assert insight.usage == {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
    assert "Do not invent numbers" in insight.prompt

    persisted = list(db_session.scalars(select(LlmInsight)))
    assert len(persisted) == 1


def test_generation_endpoint_fails_cleanly_without_openrouter_key(
    client: TestClient,
    db_session: Session,
) -> None:
    _, scenario = _seed_phase3_outputs(client, db_session)

    response = client.post(f"/api/llm/summary/{scenario.id}")

    assert response.status_code == 503
    assert "OpenRouter API key is not configured" in response.json()["detail"]
    persisted = list(db_session.scalars(select(LlmInsight)))
    assert len(persisted) == 1
    assert persisted[0].status == "failed"
    assert persisted[0].response_text is None

    list_response = client.get(f"/api/llm/insights?scenario_id={scenario.id}")
    assert list_response.status_code == 200
    assert list_response.json()[0]["status"] == "failed"
