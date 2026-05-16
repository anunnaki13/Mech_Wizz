from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PreFeedDecisionGate, PreFeedPackage, PreFeedRisk, ScenarioResult
from app.models.pre_feed_decision import severity_band
from app.schemas.pre_feed_decision import (
    GATE_CATEGORY_VALUES,
    GATE_STATUS_VALUES,
    RISK_CATEGORY_VALUES,
    RISK_STATUS_VALUES,
    PreFeedDecisionGateCreate,
    PreFeedDecisionGateUpdate,
    PreFeedRiskCreate,
    PreFeedRiskUpdate,
)
from app.services.prefeed import generate_package_gaps, get_package_or_raise
from app.services.prefeed_costs import (
    build_cost_summary,
    build_vendor_comparison,
    generate_vendor_gaps,
    get_active_cost_basis,
    list_vendor_proposals,
)
from app.services.prefeed_market import (
    build_mrv_summary,
    build_offtake_summary,
    generate_mrv_gaps,
    generate_offtake_gaps,
)


class PreFeedDecisionInputError(ValueError):
    pass


SEVERITY_BANDS = ("low", "medium", "high", "critical")
GATE_COMPLETE_STATUSES = {"ready", "waived"}
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _validate_choice(value: str, allowed: tuple[str, ...], label: str) -> None:
    if value not in allowed:
        raise PreFeedDecisionInputError(f"Unsupported {label}: {value}")


def _validate_score(value: int, label: str) -> None:
    if value < 1 or value > 5:
        raise PreFeedDecisionInputError(f"{label} must be between 1 and 5")


def _get_risk_or_raise(db: Session, risk_id: str) -> PreFeedRisk:
    risk = db.get(PreFeedRisk, risk_id)
    if risk is None:
        raise PreFeedDecisionInputError("Risk not found")
    return risk


def _get_gate_or_raise(db: Session, gate_id: str) -> PreFeedDecisionGate:
    gate = db.get(PreFeedDecisionGate, gate_id)
    if gate is None:
        raise PreFeedDecisionInputError("Decision gate not found")
    return gate


def _sort_key_date(value: date | None) -> tuple[int, date | None]:
    return (1, None) if value is None else (0, value)


def _sort_risks(risks: list[PreFeedRisk]) -> list[PreFeedRisk]:
    return sorted(
        risks,
        key=lambda risk: (
            0 if risk.status == "escalated" else 1 if risk.status != "closed" else 2,
            -risk.severity_score,
            _sort_key_date(risk.due_date),
            risk.risk_statement,
        ),
    )


def _risk_priority(risk: PreFeedRisk) -> str:
    if risk.status == "escalated" or risk.severity_score >= 20:
        return "critical"
    if risk.severity_score >= 12:
        return "high"
    if risk.severity_score >= 6:
        return "medium"
    return "low"


def _blocker(
    source_module: str,
    title: str,
    priority_level: str,
    recommendation: str,
    *,
    source_id: str | None = None,
    owner: str | None = None,
    status: str = "open",
    confidence_level: str = "unknown",
) -> dict[str, str | None]:
    return {
        "source_module": source_module,
        "source_id": source_id,
        "title": title,
        "priority_level": priority_level,
        "owner": owner,
        "recommendation": recommendation,
        "status": status,
        "confidence_level": confidence_level,
    }


def list_risks(db: Session, package_id: str) -> list[PreFeedRisk]:
    get_package_or_raise(db, package_id)
    risks = list(
        db.scalars(
            select(PreFeedRisk)
            .where(PreFeedRisk.package_id == package_id)
            .order_by(PreFeedRisk.updated_at.desc(), PreFeedRisk.id.desc())
        )
    )
    return _sort_risks(risks)


def create_risk(db: Session, package_id: str, payload: PreFeedRiskCreate) -> PreFeedRisk:
    package = get_package_or_raise(db, package_id)
    _validate_choice(payload.category, RISK_CATEGORY_VALUES, "risk category")
    _validate_choice(payload.status, RISK_STATUS_VALUES, "risk status")
    _validate_score(payload.likelihood, "Likelihood")
    _validate_score(payload.impact, "Impact")
    risk = PreFeedRisk(
        package_id=package.id,
        category=payload.category,
        risk_statement=payload.risk_statement.strip(),
        likelihood=payload.likelihood,
        impact=payload.impact,
        mitigation=_clean_optional_text(payload.mitigation),
        owner_name=_clean_optional_text(payload.owner_name),
        due_date=payload.due_date,
        status=payload.status,
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


def update_risk(db: Session, risk_id: str, payload: PreFeedRiskUpdate) -> PreFeedRisk:
    risk = _get_risk_or_raise(db, risk_id)
    updates = payload.model_dump(exclude_unset=True)
    if "category" in updates and updates["category"]:
        _validate_choice(updates["category"], RISK_CATEGORY_VALUES, "risk category")
    if "status" in updates and updates["status"]:
        _validate_choice(updates["status"], RISK_STATUS_VALUES, "risk status")
    if "likelihood" in updates and updates["likelihood"] is not None:
        _validate_score(updates["likelihood"], "Likelihood")
    if "impact" in updates and updates["impact"] is not None:
        _validate_score(updates["impact"], "Impact")
    for field, value in updates.items():
        if field in {"risk_statement", "mitigation", "owner_name", "notes"} and isinstance(value, str):
            value = value.strip() if field == "risk_statement" else _clean_optional_text(value)
        setattr(risk, field, value)
    db.commit()
    db.refresh(risk)
    return risk


def delete_risk(db: Session, risk_id: str) -> None:
    risk = _get_risk_or_raise(db, risk_id)
    db.delete(risk)
    db.commit()


def list_decision_gates(db: Session, package_id: str) -> list[PreFeedDecisionGate]:
    get_package_or_raise(db, package_id)
    return list(
        db.scalars(
            select(PreFeedDecisionGate)
            .where(PreFeedDecisionGate.package_id == package_id)
            .order_by(PreFeedDecisionGate.is_critical.desc(), PreFeedDecisionGate.updated_at.desc(), PreFeedDecisionGate.id.desc())
        )
    )


def create_decision_gate(
    db: Session,
    package_id: str,
    payload: PreFeedDecisionGateCreate,
) -> PreFeedDecisionGate:
    package = get_package_or_raise(db, package_id)
    _validate_choice(payload.category, GATE_CATEGORY_VALUES, "decision gate category")
    _validate_choice(payload.status, GATE_STATUS_VALUES, "decision gate status")
    gate = PreFeedDecisionGate(
        package_id=package.id,
        category=payload.category,
        gate_title=payload.gate_title.strip(),
        evidence_reference=_clean_optional_text(payload.evidence_reference),
        owner_name=_clean_optional_text(payload.owner_name),
        due_date=payload.due_date,
        is_critical=payload.is_critical,
        status=payload.status,
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(gate)
    db.commit()
    db.refresh(gate)
    return gate


def update_decision_gate(
    db: Session,
    gate_id: str,
    payload: PreFeedDecisionGateUpdate,
) -> PreFeedDecisionGate:
    gate = _get_gate_or_raise(db, gate_id)
    updates = payload.model_dump(exclude_unset=True)
    if "category" in updates and updates["category"]:
        _validate_choice(updates["category"], GATE_CATEGORY_VALUES, "decision gate category")
    if "status" in updates and updates["status"]:
        _validate_choice(updates["status"], GATE_STATUS_VALUES, "decision gate status")
    for field, value in updates.items():
        if field in {"gate_title", "evidence_reference", "owner_name", "notes"} and isinstance(value, str):
            value = value.strip() if field == "gate_title" else _clean_optional_text(value)
        setattr(gate, field, value)
    db.commit()
    db.refresh(gate)
    return gate


def delete_decision_gate(db: Session, gate_id: str) -> None:
    gate = _get_gate_or_raise(db, gate_id)
    db.delete(gate)
    db.commit()


def build_risk_summary(db: Session, package_id: str) -> dict[str, Any]:
    risks = list_risks(db, package_id)
    distribution = {band: 0 for band in SEVERITY_BANDS}
    for risk in risks:
        distribution[severity_band(risk.severity_score)] += 1
    warnings = []
    if not risks:
        warnings.append("No risks recorded for this package.")
    open_risks = [risk for risk in risks if risk.status != "closed"]
    escalated = [risk for risk in risks if risk.status == "escalated"]
    return {
        "package_id": package_id,
        "risk_count": len(risks),
        "open_risk_count": len(open_risks),
        "escalated_risk_count": len(escalated),
        "severity_distribution": distribution,
        "top_risks": _sort_risks(open_risks)[:5],
        "warnings": warnings,
    }


def build_decision_gate_summary(db: Session, package_id: str) -> dict[str, Any]:
    gates = list_decision_gates(db, package_id)
    status_distribution = {status: 0 for status in GATE_STATUS_VALUES}
    category_counts: dict[str, dict[str, int]] = {}
    for gate in gates:
        status_distribution[gate.status] += 1
        bucket = category_counts.setdefault(gate.category, {"total": 0, "ready": 0, "blocked": 0})
        bucket["total"] += 1
        if gate.status in GATE_COMPLETE_STATUSES:
            bucket["ready"] += 1
        if gate.status == "blocked":
            bucket["blocked"] += 1

    ready_count = sum(1 for gate in gates if gate.status in GATE_COMPLETE_STATUSES)
    blocked_count = sum(1 for gate in gates if gate.status == "blocked")
    critical_blockers = [
        gate for gate in gates if gate.is_critical and gate.status not in GATE_COMPLETE_STATUSES
    ]
    warnings = []
    if not gates:
        warnings.append("No decision gate checklist items recorded for this package.")
    return {
        "package_id": package_id,
        "gate_count": len(gates),
        "ready_gate_count": ready_count,
        "blocked_gate_count": blocked_count,
        "critical_blocker_count": len(critical_blockers),
        "readiness_score": round(ready_count / len(gates), 4) if gates else 0.0,
        "status_distribution": status_distribution,
        "gates_by_category": category_counts,
        "warnings": warnings,
    }


def _risk_blockers(db: Session, package_id: str) -> list[dict[str, str | None]]:
    blockers = []
    for risk in list_risks(db, package_id):
        if risk.status == "closed":
            continue
        priority = _risk_priority(risk)
        if priority not in {"critical", "high"}:
            continue
        blockers.append(
            _blocker(
                "prefeed_risk",
                risk.risk_statement,
                priority,
                risk.mitigation or "Define and assign mitigation before committee review.",
                source_id=risk.id,
                owner=risk.owner_name,
                status=risk.status,
                confidence_level=risk.confidence_level,
            )
        )
    return blockers


def _gate_blockers(db: Session, package_id: str) -> list[dict[str, str | None]]:
    blockers = []
    for gate in list_decision_gates(db, package_id):
        if gate.status == "blocked" or (gate.is_critical and gate.status not in GATE_COMPLETE_STATUSES):
            blockers.append(
                _blocker(
                    "prefeed_decision_gate",
                    gate.gate_title,
                    "high" if gate.is_critical else "medium",
                    gate.evidence_reference or "Resolve this decision gate and attach evidence before committee review.",
                    source_id=gate.id,
                    owner=gate.owner_name,
                    status=gate.status,
                    confidence_level=gate.confidence_level,
                )
            )
    return blockers


def _gap_blockers(package_id: str, gaps: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    blockers = []
    for gap in gaps:
        priority = gap.get("priority_level", "medium")
        if priority not in {"high", "critical"}:
            continue
        blockers.append(
            _blocker(
                str(gap.get("source_module", "prefeed_gap")),
                str(gap.get("missing_data_name", "Missing data")),
                str(priority),
                str(gap.get("recommendation", "Close this data gap before committee review.")),
                source_id=gap.get("package_id") or package_id,
                owner=gap.get("owner"),
                status=str(gap.get("status", "open")),
                confidence_level=str(gap.get("confidence_level", "unknown")),
            )
        )
    return blockers


def _active_cost_basis_dict(selection: object | None) -> dict[str, Any] | None:
    if selection is None:
        return None
    return {
        "id": selection.id,
        "scenario_id": selection.scenario_id,
        "package_id": selection.package_id,
        "vendor_proposal_id": selection.vendor_proposal_id,
        "selection_type": selection.selection_type,
        "is_active": selection.is_active,
        "snapshot_totals": selection.snapshot_totals,
        "scenario_ready_assumptions": selection.scenario_ready_assumptions,
        "selected_by": selection.selected_by,
        "selection_notes": selection.selection_notes,
        "created_at": selection.created_at,
        "updated_at": selection.updated_at,
    }


def build_decision_blockers(db: Session, package_id: str) -> list[dict[str, str | None]]:
    package = get_package_or_raise(db, package_id)
    blockers: list[dict[str, str | None]] = []
    blockers.extend(_risk_blockers(db, package_id))
    blockers.extend(_gate_blockers(db, package_id))

    package_gaps = generate_package_gaps(db, package_id)
    blockers.extend(_gap_blockers(package_id, package_gaps))

    if not build_cost_summary(db, package_id)["item_count"]:
        blockers.append(
            _blocker(
                "prefeed_cost",
                "Cost basis",
                "high",
                "Record CAPEX/OPEX line items before committee review.",
                source_id=package_id,
                owner="Project Controls",
            )
        )
    if package.scenario_id and get_active_cost_basis(db, package.scenario_id) is None:
        blockers.append(
            _blocker(
                "prefeed_cost",
                "Active cost basis",
                "high",
                "Select an active cost basis for the package scenario.",
                source_id=package.scenario_id,
                owner="Project Controls",
            )
        )

    proposals = list_vendor_proposals(db, package_id)
    if not proposals:
        blockers.append(
            _blocker(
                "prefeed_vendor",
                "Vendor proposal",
                "high",
                "Record at least one vendor or EPC proposal before committee review.",
                source_id=package_id,
                owner="Procurement",
            )
        )
    for proposal in proposals:
        blockers.extend(_gap_blockers(package_id, generate_vendor_gaps(db, proposal.id)))

    blockers.extend(_gap_blockers(package_id, generate_offtake_gaps(db, package_id)))
    blockers.extend(_gap_blockers(package_id, generate_mrv_gaps(db, package_id)))
    return sorted(blockers, key=lambda item: (PRIORITY_ORDER.get(str(item["priority_level"]), 9), item["title"] or ""))


def build_next_actions(db: Session, package_id: str) -> list[dict[str, str | None]]:
    actions = [
        {
            "source_module": blocker["source_module"],
            "source_id": blocker["source_id"],
            "title": blocker["title"],
            "priority_level": blocker["priority_level"],
            "owner": blocker["owner"],
            "recommendation": blocker["recommendation"],
            "status": "open",
        }
        for blocker in build_decision_blockers(db, package_id)[:8]
    ]
    if not list_risks(db, package_id):
        actions.append(
            {
                "source_module": "prefeed_risk",
                "source_id": package_id,
                "title": "Risk register",
                "priority_level": "high",
                "owner": "Project Lead",
                "recommendation": "Create the first risk register entries for technical, commercial, MRV, and financing readiness.",
                "status": "open",
            }
        )
    if not list_decision_gates(db, package_id):
        actions.append(
            {
                "source_module": "prefeed_decision_gate",
                "source_id": package_id,
                "title": "Decision gates",
                "priority_level": "high",
                "owner": "Project Lead",
                "recommendation": "Create decision gates for technical, commercial, legal, land, grid, offtake, MRV, and financing readiness.",
                "status": "open",
            }
        )
    return sorted(actions, key=lambda item: (PRIORITY_ORDER.get(str(item["priority_level"]), 9), item["title"] or ""))[:10]


def _latest_scenario_result_exists(db: Session, package: PreFeedPackage) -> bool:
    if not package.scenario_id:
        return False
    return (
        db.scalar(
            select(ScenarioResult.id)
            .where(ScenarioResult.scenario_id == package.scenario_id)
            .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
        )
        is not None
    )


def build_prefeed_decision_dashboard(db: Session, package_id: str) -> dict[str, Any]:
    package = get_package_or_raise(db, package_id)
    package_gaps = generate_package_gaps(db, package_id)
    cost_summary = build_cost_summary(db, package_id)
    active_cost_basis = get_active_cost_basis(db, package.scenario_id) if package.scenario_id else None
    vendor_comparison = build_vendor_comparison(db, package_id)
    offtake_summary = build_offtake_summary(db, package_id)
    offtake_gaps = generate_offtake_gaps(db, package_id)
    mrv_summary = build_mrv_summary(db, package_id)
    mrv_gaps = generate_mrv_gaps(db, package_id)
    risk_summary = build_risk_summary(db, package_id)
    gate_summary = build_decision_gate_summary(db, package_id)
    blockers = build_decision_blockers(db, package_id)
    next_actions = build_next_actions(db, package_id)

    warnings: list[str] = []
    warnings.extend(cost_summary.get("warnings", []))
    warnings.extend(offtake_summary.get("warnings", []))
    warnings.extend(mrv_summary.get("warnings", []))
    warnings.extend(risk_summary.get("warnings", []))
    warnings.extend(gate_summary.get("warnings", []))
    if package.scenario_id and not _latest_scenario_result_exists(db, package):
        warnings.append("No stored scenario result is available for the selected package scenario.")
    if package.scenario_id and active_cost_basis is None:
        warnings.append("No active cost basis selected for the selected package scenario.")

    return {
        "package_id": package.id,
        "plant_id": package.plant_id,
        "scenario_id": package.scenario_id,
        "package_name": package.package_name,
        "package_status": package.package_status,
        "package_confidence_level": package.confidence_level,
        "package_data_status": package.data_status,
        "package_gaps": package_gaps,
        "cost_summary": cost_summary,
        "active_cost_basis": _active_cost_basis_dict(active_cost_basis),
        "vendor_comparison": vendor_comparison,
        "offtake_summary": offtake_summary,
        "offtake_gaps": offtake_gaps,
        "mrv_summary": mrv_summary,
        "mrv_gaps": mrv_gaps,
        "risk_summary": risk_summary,
        "decision_gate_summary": gate_summary,
        "blockers": blockers,
        "next_actions": next_actions,
        "warnings": warnings,
    }
