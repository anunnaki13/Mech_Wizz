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
from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models import Document, LlmInsight
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


@pytest.fixture(autouse=True)
def upload_dir(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Generator[None, None, None]:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


def test_upload_list_read_and_extract_text_document(client: TestClient, db_session: Session) -> None:
    plant = seed_tenayan(db_session)
    response = client.post(
        "/api/documents/upload",
        data={"plant_id": plant.id, "document_category": "emission_report"},
        files={"file": ("../tenayan-report.txt", b"Tenayan CO2 capture readiness note", "text/plain")},
    )
    assert response.status_code == 201
    document = response.json()
    assert document["plant_id"] == plant.id
    assert document["original_filename"] == "tenayan-report.txt"
    assert document["extraction_status"] == "pending"

    list_response = client.get("/api/documents")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    read_response = client.get(f"/api/documents/{document['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["filename"].endswith("tenayan-report.txt")

    extract_response = client.post(f"/api/documents/{document['id']}/extract")
    assert extract_response.status_code == 200
    extracted = extract_response.json()
    assert extracted["extraction_status"] == "extracted"
    assert "Tenayan CO2 capture readiness note" in extracted["extracted_text"]

    persisted = db_session.scalar(select(Document).where(Document.id == document["id"]))
    assert persisted is not None
    assert persisted.extracted_text is not None


def test_document_qa_requires_extracted_text(client: TestClient) -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("note.txt", b"Document content", "text/plain")},
    )
    assert response.status_code == 201
    document_id = response.json()["id"]

    ask_response = client.post(f"/api/documents/{document_id}/ask", json={"question": "What is this about?"})

    assert ask_response.status_code == 400
    assert "extracted" in ask_response.json()["detail"]


def test_document_qa_persists_failed_insight_without_openrouter_key(
    client: TestClient,
    db_session: Session,
) -> None:
    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("note.txt", b"Document content for grounded question", "text/plain")},
    )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]
    extract_response = client.post(f"/api/documents/{document_id}/extract")
    assert extract_response.status_code == 200

    ask_response = client.post(f"/api/documents/{document_id}/ask", json={"question": "What is this about?"})

    assert ask_response.status_code == 503
    assert "OpenRouter API key is not configured" in ask_response.json()["detail"]
    insights = list(db_session.scalars(select(LlmInsight)))
    assert len(insights) == 1
    assert insights[0].document_id == document_id
    assert insights[0].insight_type == "document_qa"
    assert insights[0].status == "failed"
