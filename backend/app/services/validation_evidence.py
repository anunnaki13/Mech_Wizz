import re
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import BusinessScenario, Document, Plant, ValidationEvidence
from app.schemas.validation_evidence import ValidationEvidenceCreate, ValidationEvidenceUpdate
from app.services.validation_pack import build_top3_validation_pack


class ValidationEvidenceInputError(ValueError):
    pass


CATEGORY_LABELS = {
    "Technical": "technical",
    "Economics": "economics",
    "Logistics": "logistics",
    "Power and H2": "power_h2",
    "Commercial and MRV": "commercial_mrv",
}

EVIDENCE_KEYS_BY_CATEGORY = {
    "technical": "site_stack_profile",
    "economics": "capex_opex_lcom",
    "logistics": "port_export_route",
    "power_h2": "electrolyzer_power_supply",
    "commercial_mrv": "offtake_mrv_carbon_accounting",
}

STATUS_SCORE = {
    "missing": 0.0,
    "requested": 0.35,
    "received": 0.7,
    "verified": 1.0,
    "rejected": 0.0,
}

PRIORITY_WEIGHT = {"high": 1.4, "medium": 1.0, "low": 0.7}


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return cleaned or "evidence"


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _get_plant_or_raise(db: Session, plant_id: str) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise ValidationEvidenceInputError("Plant not found")
    return plant


def _get_scenario_or_raise(db: Session, scenario_id: str) -> BusinessScenario:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise ValidationEvidenceInputError("Scenario not found")
    return scenario


def _validate_candidate_scope(db: Session, plant_id: str, scenario_id: str) -> None:
    _get_plant_or_raise(db, plant_id)
    scenario = _get_scenario_or_raise(db, scenario_id)
    if scenario.plant_id != plant_id:
        raise ValidationEvidenceInputError("Scenario belongs to a different plant")


def _validate_document_matches_candidate(db: Session, plant_id: str, scenario_id: str, document_id: str | None) -> None:
    if document_id is None:
        return
    document = db.get(Document, document_id)
    if document is None:
        raise ValidationEvidenceInputError("Supporting document not found")
    if document.plant_id and document.plant_id != plant_id:
        raise ValidationEvidenceInputError("Document belongs to a different plant")
    if document.scenario_id and document.scenario_id != scenario_id:
        raise ValidationEvidenceInputError("Document belongs to a different scenario")


def _evidence_identity(
    plant_id: str,
    scenario_id: str,
    category: str,
    evidence_key: str,
) -> tuple[str, str, str, str]:
    return (plant_id, scenario_id, category, evidence_key)


def _default_requirement(candidate: dict[str, Any], item: dict[str, str]) -> dict[str, Any]:
    category = CATEGORY_LABELS.get(item["category"], _slug(item["category"]))
    evidence_key = EVIDENCE_KEYS_BY_CATEGORY.get(category, _slug(item["item"]))
    return {
        "plant_id": candidate["plant_id"],
        "scenario_id": candidate["scenario_id"],
        "category": category,
        "evidence_key": evidence_key,
        "title": item["item"],
        "required_evidence": item["required_evidence"],
        "current_basis": item["current_basis"],
        "priority": item["priority"],
        "source_validation_status": item["status"],
    }


def _status_score(status: str) -> float:
    return STATUS_SCORE.get(status, 0.0)


def _readiness_score(items: list[dict[str, Any]]) -> float:
    if not items:
        return 0.0
    weighted_total = 0.0
    weight_sum = 0.0
    for item in items:
        weight = PRIORITY_WEIGHT.get(item["priority"], 1.0)
        weighted_total += _status_score(item["status"]) * weight
        weight_sum += weight
    if weight_sum == 0:
        return 0.0
    return round((weighted_total / weight_sum) * 100, 1)


def _apply_status_dates(record: ValidationEvidence) -> None:
    today = date.today()
    if record.status in {"received", "verified"} and record.received_date is None:
        record.received_date = today
    if record.status == "verified" and record.verified_date is None:
        record.verified_date = today


def _existing_record(
    db: Session,
    plant_id: str,
    scenario_id: str,
    category: str,
    evidence_key: str,
) -> ValidationEvidence | None:
    return db.scalar(
        select(ValidationEvidence)
        .where(
            ValidationEvidence.plant_id == plant_id,
            ValidationEvidence.scenario_id == scenario_id,
            ValidationEvidence.category == category,
            ValidationEvidence.evidence_key == evidence_key,
        )
        .options(selectinload(ValidationEvidence.supporting_document))
    )


def _record_updates(payload: ValidationEvidenceCreate | ValidationEvidenceUpdate) -> dict[str, Any]:
    updates = payload.model_dump(exclude_unset=True)
    if isinstance(updates.get("title"), str):
        title = updates["title"].strip()
        if not title:
            raise ValidationEvidenceInputError("Evidence title is required")
        updates["title"] = title
    for field in ("required_evidence", "current_basis", "owner_name", "source_organization", "reference_url", "notes"):
        if field in updates and isinstance(updates[field], str):
            updates[field] = _clean_optional_text(updates[field])
    return updates


def create_validation_evidence(db: Session, payload: ValidationEvidenceCreate) -> ValidationEvidence:
    _validate_candidate_scope(db, payload.plant_id, payload.scenario_id)
    _validate_document_matches_candidate(db, payload.plant_id, payload.scenario_id, payload.document_id)
    record = _existing_record(db, payload.plant_id, payload.scenario_id, payload.category, payload.evidence_key)
    updates = _record_updates(payload)
    if record is None:
        record = ValidationEvidence(**updates)
        db.add(record)
    else:
        for field, value in updates.items():
            setattr(record, field, value)
    _apply_status_dates(record)
    db.commit()
    db.refresh(record)
    return _existing_record(db, record.plant_id, record.scenario_id, record.category, record.evidence_key) or record


def update_validation_evidence(db: Session, record_id: str, payload: ValidationEvidenceUpdate) -> ValidationEvidence:
    record = db.scalar(
        select(ValidationEvidence)
        .where(ValidationEvidence.id == record_id)
        .options(selectinload(ValidationEvidence.supporting_document))
    )
    if record is None:
        raise ValidationEvidenceInputError("Evidence record not found")
    updates = _record_updates(payload)
    if "document_id" in updates:
        _validate_document_matches_candidate(db, record.plant_id, record.scenario_id, updates["document_id"])
    for field, value in updates.items():
        setattr(record, field, value)
    _apply_status_dates(record)
    db.commit()
    db.refresh(record)
    return _existing_record(db, record.plant_id, record.scenario_id, record.category, record.evidence_key) or record


def build_evidence_workspace(db: Session, scheme: str = "align", limit: int = 3) -> dict[str, Any]:
    pack = build_top3_validation_pack(db, scheme=scheme, limit=limit)
    candidates = pack["candidates"]
    plant_ids = [candidate["plant_id"] for candidate in candidates]
    scenario_ids = [candidate["scenario_id"] for candidate in candidates]
    records = (
        list(
            db.scalars(
                select(ValidationEvidence)
                .where(
                    ValidationEvidence.plant_id.in_(plant_ids),
                    ValidationEvidence.scenario_id.in_(scenario_ids),
                )
                .options(selectinload(ValidationEvidence.supporting_document))
                .order_by(ValidationEvidence.updated_at.desc(), ValidationEvidence.id.desc())
            )
        )
        if plant_ids and scenario_ids
        else []
    )
    record_index = {
        _evidence_identity(record.plant_id, record.scenario_id, record.category, record.evidence_key): record
        for record in records
    }

    status_counts = {status: 0 for status in STATUS_SCORE}
    workspace_candidates = []
    all_items: list[dict[str, Any]] = []

    for candidate in candidates:
        evidence_items = []
        for item in candidate["validation_items"]:
            requirement = _default_requirement(candidate, item)
            record = record_index.get(
                _evidence_identity(
                    requirement["plant_id"],
                    requirement["scenario_id"],
                    requirement["category"],
                    requirement["evidence_key"],
                )
            )
            status = record.status if record is not None else "missing"
            confidence_level = record.confidence_level if record is not None else "unknown"
            merged = {
                **requirement,
                "status": status,
                "confidence_level": confidence_level,
                "status_score": _status_score(status),
                "record": record,
            }
            evidence_items.append(merged)
            all_items.append(merged)
            status_counts[status] = status_counts.get(status, 0) + 1

        workspace_candidates.append(
            {
                "validation_rank": candidate["validation_rank"],
                "site_name": candidate["site_name"],
                "plant_id": candidate["plant_id"],
                "scenario_id": candidate["scenario_id"],
                "province": candidate["province"],
                "capacity_mw": candidate["capacity_mw"],
                "final_score": candidate["final_score"],
                "methanol_tpy": candidate["methanol_tpy"],
                "estimated_lcom_usd_ton": candidate["estimated_lcom_usd_ton"],
                "nearest_port_name": candidate["nearest_port_name"],
                "evidence_readiness_score": _readiness_score(evidence_items),
                "high_priority_open_items": sum(
                    1 for item in evidence_items if item["priority"] == "high" and item["status"] != "verified"
                ),
                "evidence_items": evidence_items,
            }
        )

    summary = {
        "candidate_count": len(workspace_candidates),
        "lead_candidate": workspace_candidates[0]["site_name"] if workspace_candidates else None,
        "total_items": len(all_items),
        "verified_items": status_counts.get("verified", 0),
        "high_priority_open_items": sum(
            1 for item in all_items if item["priority"] == "high" and item["status"] != "verified"
        ),
        "evidence_readiness_score": _readiness_score(all_items),
        "counts_by_status": status_counts,
    }
    return {
        "scheme": scheme,
        "limit": limit,
        "summary": summary,
        "candidates": workspace_candidates,
        "warnings": [
            "Evidence readiness tracks validation status only; it does not override deterministic shortlist ranking.",
            "Verified evidence should be PLN/site/vendor/port/offtake/MRV-confirmed before committee pilot selection.",
        ],
    }
