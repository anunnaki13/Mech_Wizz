from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import BusinessScenario, Document, Plant, PreFeedPackage, PreFeedPackageDocument
from app.schemas.pre_feed import DOCUMENT_ROLE_VALUES, PACKAGE_STATUS_VALUES, PreFeedPackageCreate, PreFeedPackageUpdate


class PreFeedInputError(ValueError):
    pass


REQUIRED_DOCUMENT_ROLES = ("vendor_proposal", "epc_estimate")


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _validate_package_status(package_status: str) -> None:
    if package_status not in PACKAGE_STATUS_VALUES:
        raise PreFeedInputError(f"Unsupported package status: {package_status}")


def _validate_document_role(document_role: str) -> None:
    if document_role not in DOCUMENT_ROLE_VALUES:
        raise PreFeedInputError(f"Unsupported document role: {document_role}")


def _get_plant_or_raise(db: Session, plant_id: str) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise PreFeedInputError("Plant not found")
    return plant


def _get_scenario_or_raise(db: Session, scenario_id: str, plant_id: str) -> BusinessScenario:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise PreFeedInputError("Scenario not found")
    if scenario.plant_id != plant_id:
        raise PreFeedInputError("Scenario does not belong to the selected plant")
    return scenario


def get_package_or_raise(db: Session, package_id: str) -> PreFeedPackage:
    package = db.scalar(
        select(PreFeedPackage)
        .where(PreFeedPackage.id == package_id)
        .options(selectinload(PreFeedPackage.document_links).selectinload(PreFeedPackageDocument.document))
    )
    if package is None:
        raise PreFeedInputError("Pre-FEED package not found")
    return package


def list_packages(
    db: Session,
    plant_id: str | None = None,
    scenario_id: str | None = None,
    include_archived: bool = False,
) -> list[PreFeedPackage]:
    statement = select(PreFeedPackage).options(
        selectinload(PreFeedPackage.document_links).selectinload(PreFeedPackageDocument.document)
    )
    if plant_id:
        statement = statement.where(PreFeedPackage.plant_id == plant_id)
    if scenario_id:
        statement = statement.where(PreFeedPackage.scenario_id == scenario_id)
    if not include_archived:
        statement = statement.where(PreFeedPackage.package_status != "archived")
    statement = statement.order_by(PreFeedPackage.updated_at.desc(), PreFeedPackage.created_at.desc())
    return list(db.scalars(statement))


def create_package(db: Session, payload: PreFeedPackageCreate) -> PreFeedPackage:
    _get_plant_or_raise(db, payload.plant_id)
    if payload.scenario_id:
        _get_scenario_or_raise(db, payload.scenario_id, payload.plant_id)
    _validate_package_status(payload.package_status)

    package = PreFeedPackage(
        plant_id=payload.plant_id,
        scenario_id=payload.scenario_id,
        package_name=payload.package_name.strip(),
        package_status=payload.package_status,
        owner_name=_clean_optional_text(payload.owner_name),
        source_organization=_clean_optional_text(payload.source_organization),
        received_date=payload.received_date,
        version_label=_clean_optional_text(payload.version_label),
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(package)
    db.commit()
    db.refresh(package)
    return get_package_or_raise(db, package.id)


def update_package(db: Session, package_id: str, payload: PreFeedPackageUpdate) -> PreFeedPackage:
    package = get_package_or_raise(db, package_id)
    updates = payload.model_dump(exclude_unset=True)
    plant_id = updates.get("plant_id", package.plant_id)
    scenario_id = updates.get("scenario_id", package.scenario_id)

    if "plant_id" in updates:
        _get_plant_or_raise(db, plant_id)
    if scenario_id:
        _get_scenario_or_raise(db, scenario_id, plant_id)
    if "package_status" in updates and updates["package_status"] is not None:
        _validate_package_status(updates["package_status"])

    for field, value in updates.items():
        if field in {"package_name", "owner_name", "source_organization", "version_label", "notes"} and isinstance(
            value,
            str,
        ):
            value = value.strip()
        setattr(package, field, value or None if field != "package_name" and value == "" else value)

    db.commit()
    db.refresh(package)
    return get_package_or_raise(db, package.id)


def archive_package(db: Session, package_id: str) -> PreFeedPackage:
    package = get_package_or_raise(db, package_id)
    package.package_status = "archived"
    db.commit()
    db.refresh(package)
    return get_package_or_raise(db, package.id)


def _validate_document_matches_package(package: PreFeedPackage, document: Document) -> None:
    if document.plant_id and document.plant_id != package.plant_id:
        raise PreFeedInputError("Document belongs to a different plant")
    if document.scenario_id and package.scenario_id and document.scenario_id != package.scenario_id:
        raise PreFeedInputError("Document belongs to a different scenario")


def list_package_documents(db: Session, package_id: str) -> list[PreFeedPackageDocument]:
    get_package_or_raise(db, package_id)
    statement = (
        select(PreFeedPackageDocument)
        .where(PreFeedPackageDocument.package_id == package_id)
        .options(selectinload(PreFeedPackageDocument.document))
        .order_by(PreFeedPackageDocument.created_at.desc(), PreFeedPackageDocument.id.desc())
    )
    return list(db.scalars(statement))


def link_package_document(
    db: Session,
    package_id: str,
    document_id: str,
    document_role: str,
    notes: str | None = None,
) -> PreFeedPackageDocument:
    package = get_package_or_raise(db, package_id)
    document = db.get(Document, document_id)
    if document is None:
        raise PreFeedInputError("Document not found")
    _validate_document_role(document_role)
    _validate_document_matches_package(package, document)

    existing = db.scalar(
        select(PreFeedPackageDocument).where(
            PreFeedPackageDocument.package_id == package.id,
            PreFeedPackageDocument.document_id == document.id,
            PreFeedPackageDocument.document_role == document_role,
        )
    )
    if existing is not None:
        raise PreFeedInputError("Document is already linked to this package with that role")

    link = PreFeedPackageDocument(
        package_id=package.id,
        document_id=document.id,
        document_role=document_role,
        notes=_clean_optional_text(notes),
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return db.scalar(
        select(PreFeedPackageDocument)
        .where(PreFeedPackageDocument.id == link.id)
        .options(selectinload(PreFeedPackageDocument.document))
    )


def unlink_package_document(db: Session, package_id: str, link_id: str) -> None:
    get_package_or_raise(db, package_id)
    link = db.scalar(
        select(PreFeedPackageDocument).where(
            PreFeedPackageDocument.id == link_id,
            PreFeedPackageDocument.package_id == package_id,
        )
    )
    if link is None:
        raise PreFeedInputError("Package document link not found")
    db.delete(link)
    db.commit()


def _gap(
    package_id: str,
    source_module: str,
    missing_data_name: str,
    impact_level: str,
    priority_level: str,
    recommendation: str,
    confidence_level: str,
) -> dict[str, str]:
    return {
        "package_id": package_id,
        "source_module": source_module,
        "missing_data_name": missing_data_name,
        "impact_level": impact_level,
        "priority_level": priority_level,
        "recommendation": recommendation,
        "status": "open",
        "confidence_level": confidence_level,
    }


def _missing_text_fields(package: PreFeedPackage) -> Iterable[tuple[str, str, str]]:
    checks = (
        ("Package owner", package.owner_name, "Assign a package owner for accountable Pre-FEED follow-up."),
        (
            "Source organization",
            package.source_organization,
            "Record the vendor, EPC, PLN unit, or partner organization that supplied this package.",
        ),
        ("Version label", package.version_label, "Record the package version or revision label before review."),
    )
    for name, value, recommendation in checks:
        if not value:
            yield name, "medium", recommendation


def generate_package_gaps(db: Session, package_id: str) -> list[dict[str, str]]:
    package = get_package_or_raise(db, package_id)
    confidence = package.confidence_level or "unknown"
    gaps = [
        _gap(
            package.id,
            "prefeed_package",
            name,
            impact,
            "high" if impact == "high" else "medium",
            recommendation,
            confidence,
        )
        for name, impact, recommendation in _missing_text_fields(package)
    ]

    if package.received_date is None:
        gaps.append(
            _gap(
                package.id,
                "prefeed_package",
                "Received date",
                "medium",
                "medium",
                "Record when the Pre-FEED package or source document was received.",
                confidence,
            )
        )

    linked_roles = {link.document_role for link in list_package_documents(db, package.id)}
    for role in REQUIRED_DOCUMENT_ROLES:
        if role not in linked_roles:
            label = role.replace("_", " ").title()
            gaps.append(
                _gap(
                    package.id,
                    "prefeed_documents",
                    f"{label} document",
                    "high",
                    "high",
                    f"Link an uploaded document classified as {role} before downstream Pre-FEED review.",
                    confidence,
                )
            )

    if confidence in {"low", "unknown"}:
        gaps.append(
            _gap(
                package.id,
                "prefeed_package",
                "Package confidence level",
                "medium",
                "medium",
                "Review source evidence and raise confidence only when package metadata and supporting documents are verified.",
                confidence,
            )
        )

    return gaps
