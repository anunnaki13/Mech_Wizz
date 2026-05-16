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
from app.models import BusinessScenario, Document, Plant, PreFeedPackage, ScenarioResult
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


def _seed_package_inputs(db: Session) -> tuple[str, str]:
    plant = seed_tenayan(db)
    scenario = db.scalar(select(BusinessScenario).where(BusinessScenario.plant_id == plant.id))
    assert scenario is not None
    return plant.id, scenario.id


def _create_document(db: Session, plant_id: str, scenario_id: str | None = None) -> Document:
    document = Document(
        plant_id=plant_id,
        scenario_id=scenario_id,
        filename="proposal.txt",
        original_filename="proposal.txt",
        file_type="text/plain",
        storage_path="/tmp/proposal.txt",
        document_category="prefeed",
        upload_status="uploaded",
        extraction_status="pending",
        file_size_bytes=128,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def test_prefeed_package_crud_archive_and_filters(client: TestClient, db_session: Session) -> None:
    plant_id, scenario_id = _seed_package_inputs(db_session)
    create_response = client.post(
        "/api/prefeed/packages",
        json={
            "plant_id": plant_id,
            "scenario_id": scenario_id,
            "package_name": "Tenayan Pre-FEED Starter",
            "package_status": "draft",
            "owner_name": "PLN NP",
            "source_organization": "Internal Pre-FEED Team",
            "received_date": "2026-05-16",
            "version_label": "rev-a",
            "data_status": "partner_supplied",
            "confidence_level": "medium",
            "notes": "Initial package shell",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["plant_id"] == plant_id
    assert created["scenario_id"] == scenario_id
    assert created["package_status"] == "draft"

    update_response = client.put(
        f"/api/prefeed/packages/{created['id']}",
        json={"package_status": "in_review", "confidence_level": "high"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["package_status"] == "in_review"
    assert update_response.json()["confidence_level"] == "high"

    list_response = client.get(f"/api/prefeed/packages?plant_id={plant_id}&scenario_id={scenario_id}")
    assert list_response.status_code == 200
    assert [package["id"] for package in list_response.json()] == [created["id"]]

    archive_response = client.post(f"/api/prefeed/packages/{created['id']}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["package_status"] == "archived"

    default_list_response = client.get(f"/api/prefeed/packages?plant_id={plant_id}")
    assert default_list_response.status_code == 200
    assert default_list_response.json() == []

    archived_list_response = client.get(f"/api/prefeed/packages?plant_id={plant_id}&include_archived=true")
    assert archived_list_response.status_code == 200
    assert [package["id"] for package in archived_list_response.json()] == [created["id"]]


def test_prefeed_package_validates_scenario_parent(client: TestClient, db_session: Session) -> None:
    plant_id, scenario_id = _seed_package_inputs(db_session)
    other_plant = Plant(plant_name="Other Plant", unit_name="Unit 9")
    db_session.add(other_plant)
    db_session.commit()
    db_session.refresh(other_plant)

    response = client.post(
        "/api/prefeed/packages",
        json={
            "plant_id": other_plant.id,
            "scenario_id": scenario_id,
            "package_name": "Invalid Parent",
        },
    )

    assert other_plant.id != plant_id
    assert response.status_code == 400
    assert "Scenario does not belong" in response.json()["detail"]


def test_prefeed_document_link_unlink_and_duplicate_guard(client: TestClient, db_session: Session) -> None:
    plant_id, scenario_id = _seed_package_inputs(db_session)
    document = _create_document(db_session, plant_id, scenario_id)
    create_response = client.post(
        "/api/prefeed/packages",
        json={"plant_id": plant_id, "scenario_id": scenario_id, "package_name": "Document Package"},
    )
    assert create_response.status_code == 201
    package_id = create_response.json()["id"]

    link_response = client.post(
        f"/api/prefeed/packages/{package_id}/documents",
        json={"document_id": document.id, "document_role": "vendor_proposal", "notes": "Main proposal"},
    )
    assert link_response.status_code == 201
    link = link_response.json()
    assert link["document_id"] == document.id
    assert link["document_role"] == "vendor_proposal"
    assert link["document"]["original_filename"] == "proposal.txt"

    duplicate_response = client.post(
        f"/api/prefeed/packages/{package_id}/documents",
        json={"document_id": document.id, "document_role": "vendor_proposal"},
    )
    assert duplicate_response.status_code == 400
    assert "already linked" in duplicate_response.json()["detail"]

    list_response = client.get(f"/api/prefeed/packages/{package_id}/documents")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/api/prefeed/packages/{package_id}/documents/{link['id']}")
    assert delete_response.status_code == 204

    empty_response = client.get(f"/api/prefeed/packages/{package_id}/documents")
    assert empty_response.status_code == 200
    assert empty_response.json() == []


def test_prefeed_gaps_are_deterministic_and_do_not_mutate_scenario_history(
    client: TestClient,
    db_session: Session,
) -> None:
    plant_id, scenario_id = _seed_package_inputs(db_session)
    create_response = client.post(
        "/api/prefeed/packages",
        json={
            "plant_id": plant_id,
            "scenario_id": scenario_id,
            "package_name": "Gap Package",
            "confidence_level": "low",
        },
    )
    assert create_response.status_code == 201
    package_id = create_response.json()["id"]
    before_results = len(list(db_session.scalars(select(ScenarioResult))))

    gaps_response = client.get(f"/api/prefeed/packages/{package_id}/gaps")

    assert gaps_response.status_code == 200
    gaps = gaps_response.json()
    names = {gap["missing_data_name"] for gap in gaps}
    assert {
        "Package owner",
        "Source organization",
        "Received date",
        "Version label",
        "Vendor Proposal document",
        "Epc Estimate document",
        "Package confidence level",
    }.issubset(names)
    assert all(gap["source_module"].startswith("prefeed_") for gap in gaps)
    assert len(list(db_session.scalars(select(ScenarioResult)))) == before_results

    persisted_package = db_session.get(PreFeedPackage, package_id)
    assert persisted_package is not None
    assert persisted_package.package_status == "draft"
