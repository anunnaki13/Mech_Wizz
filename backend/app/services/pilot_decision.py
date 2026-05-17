from typing import Any

from sqlalchemy.orm import Session

from app.services.validation_evidence import build_evidence_workspace


SHORTLIST_WEIGHT = 0.7
EVIDENCE_WEIGHT = 0.3
REJECTED_ITEM_PENALTY = 0.08
HIGH_PRIORITY_OPEN_PENALTY = 0.015


def _round(value: float) -> float:
    return round(value, 4)


def _blocker(candidate: dict[str, Any], item: dict[str, Any]) -> dict[str, str]:
    if item["status"] == "rejected":
        recommendation = "Resolve rejected evidence or remove this candidate from committee advancement."
    elif item["status"] == "missing":
        recommendation = "Request and upload the required evidence before committee review."
    elif item["status"] == "requested":
        recommendation = "Follow up with the evidence owner and confirm expected receipt date."
    else:
        recommendation = "Review received evidence and move it to verified when accepted."
    return {
        "plant_id": candidate["plant_id"],
        "scenario_id": candidate["scenario_id"],
        "site_name": candidate["site_name"],
        "category": item["category"],
        "evidence_key": item["evidence_key"],
        "title": item["title"],
        "status": item["status"],
        "priority": item["priority"],
        "recommendation": recommendation,
    }


def _candidate_gate_status(readiness: float, rejected_items: int, high_priority_open_items: int) -> str:
    if rejected_items > 0:
        return "blocked"
    if readiness >= 80 and high_priority_open_items == 0:
        return "committee_ready"
    return "needs_evidence"


def _candidate_recommendation(gate_status: str) -> str:
    if gate_status == "committee_ready":
        return "advance_to_committee"
    if gate_status == "blocked":
        return "do_not_advance"
    return "continue_validation"


def _candidate_score(candidate: dict[str, Any], rejected_items: int, high_priority_open_items: int) -> float:
    shortlist_component = float(candidate["final_score"] or 0) * SHORTLIST_WEIGHT
    evidence_component = (float(candidate["evidence_readiness_score"] or 0) / 100) * EVIDENCE_WEIGHT
    penalty = rejected_items * REJECTED_ITEM_PENALTY + high_priority_open_items * HIGH_PRIORITY_OPEN_PENALTY
    return _round(max(0.0, shortlist_component + evidence_component - penalty))


def _next_actions(candidate: dict[str, Any], gate_status: str, blockers: list[dict[str, str]]) -> list[str]:
    if gate_status == "committee_ready":
        return [
            f"Prepare committee decision note for {candidate['site_name']}.",
            "Freeze verified evidence snapshot before single-pilot approval discussion.",
            "Confirm final commercial, port, power/H2, and MRV assumptions are reflected in the committee pack.",
        ]
    if gate_status == "blocked":
        rejected = [item for item in blockers if item["status"] == "rejected"]
        return [
            f"Do not advance {candidate['site_name']} until rejected evidence is resolved.",
            f"Review {len(rejected)} rejected evidence item(s) and decide whether the candidate remains viable.",
            "Escalate no-go evidence to management before more validation effort is spent.",
        ]
    top_blockers = blockers[:3]
    actions = [f"Continue validation for {candidate['site_name']} before committee advancement."]
    actions.extend(f"Close {item['category']} evidence: {item['title']}." for item in top_blockers)
    return actions


def _portfolio_action_plan(candidates: list[dict[str, Any]]) -> list[str]:
    if not candidates:
        return ["Run shortlist scoring before opening pilot decision review."]
    leader = candidates[0]
    if leader["gate_status"] == "committee_ready":
        return [
            f"Advance {leader['site_name']} to committee review as the current evidence-ready lead candidate.",
            "Keep the other Top 3 candidates as fallbacks until committee approval is complete.",
            "Export or screenshot the decision dashboard together with the validation pack for the meeting record.",
        ]
    if leader["gate_status"] == "blocked":
        return [
            f"Resolve blocker evidence for {leader['site_name']} or select the next non-blocked candidate for validation focus.",
            "Review all rejected evidence before committing new vendor or site-validation effort.",
            "Use the evidence workspace to move rejected items to received/verified only after issue closure is documented.",
        ]
    return [
        f"Keep {leader['site_name']} as validation lead, but do not advance to final pilot selection yet.",
        "Close all high-priority technical, economics, logistics, and power/H2 evidence gaps first.",
        "Re-run this dashboard after evidence statuses are updated in the Evidence workspace.",
    ]


def _decision_message(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "No scored candidates are available for pilot decision review."
    leader = candidates[0]
    if leader["gate_status"] == "committee_ready":
        return f"{leader['site_name']} is evidence-ready for committee review under the current deterministic rules."
    if leader["gate_status"] == "blocked":
        return f"{leader['site_name']} remains the score leader but has blocker evidence that must be resolved first."
    return f"{leader['site_name']} is the current decision leader, but more evidence is required before committee advancement."


def build_pilot_decision_dashboard(db: Session, scheme: str = "align", limit: int = 3) -> dict[str, Any]:
    workspace = build_evidence_workspace(db, scheme=scheme, limit=limit)
    candidates = []
    all_blockers = []

    for candidate in workspace["candidates"]:
        blockers = [
            _blocker(candidate, item)
            for item in candidate["evidence_items"]
            if item["status"] == "rejected" or (item["priority"] == "high" and item["status"] != "verified")
        ]
        rejected_items = sum(1 for item in candidate["evidence_items"] if item["status"] == "rejected")
        verified_items = sum(1 for item in candidate["evidence_items"] if item["status"] == "verified")
        gate_status = _candidate_gate_status(
            float(candidate["evidence_readiness_score"]),
            rejected_items,
            int(candidate["high_priority_open_items"]),
        )
        packed = {
            "validation_rank": candidate["validation_rank"],
            "decision_rank": 0,
            "site_name": candidate["site_name"],
            "plant_id": candidate["plant_id"],
            "scenario_id": candidate["scenario_id"],
            "province": candidate["province"],
            "capacity_mw": candidate["capacity_mw"],
            "shortlist_score": candidate["final_score"],
            "evidence_readiness_score": candidate["evidence_readiness_score"],
            "evidence_adjusted_score": _candidate_score(candidate, rejected_items, int(candidate["high_priority_open_items"])),
            "gate_status": gate_status,
            "recommendation": _candidate_recommendation(gate_status),
            "verified_items": verified_items,
            "rejected_items": rejected_items,
            "high_priority_open_items": candidate["high_priority_open_items"],
            "methanol_tpy": candidate["methanol_tpy"],
            "estimated_lcom_usd_ton": candidate["estimated_lcom_usd_ton"],
            "nearest_port_name": candidate["nearest_port_name"],
            "blockers": blockers,
            "next_actions": [],
        }
        packed["next_actions"] = _next_actions(candidate, gate_status, blockers)
        candidates.append(packed)
        all_blockers.extend(blockers)

    candidates.sort(key=lambda item: item["evidence_adjusted_score"], reverse=True)
    for index, candidate in enumerate(candidates, start=1):
        candidate["decision_rank"] = index

    readiness_values = [float(candidate["evidence_readiness_score"]) for candidate in candidates]
    summary = {
        "candidate_count": len(candidates),
        "recommended_candidate": candidates[0]["site_name"] if candidates else None,
        "recommended_candidate_id": candidates[0]["plant_id"] if candidates else None,
        "committee_ready_count": sum(1 for candidate in candidates if candidate["gate_status"] == "committee_ready"),
        "blocked_count": sum(1 for candidate in candidates if candidate["gate_status"] == "blocked"),
        "high_priority_open_items": sum(int(candidate["high_priority_open_items"]) for candidate in candidates),
        "average_evidence_readiness_score": round(sum(readiness_values) / len(readiness_values), 1) if readiness_values else 0.0,
        "decision_message": _decision_message(candidates),
    }
    return {
        "scheme": scheme,
        "limit": limit,
        "summary": summary,
        "candidates": candidates,
        "blockers": all_blockers,
        "action_plan": _portfolio_action_plan(candidates),
        "methodology": [
            "Decision score = 70% deterministic shortlist score + 30% evidence readiness score.",
            "Each rejected evidence item subtracts 0.08 from the decision score.",
            "Each high-priority open item subtracts 0.015 from the decision score.",
            "Committee-ready requires evidence readiness >= 80%, zero rejected evidence, and zero high-priority open items.",
            "This dashboard does not overwrite stored shortlist ranks or make investment approvals automatically.",
        ],
        "warnings": [
            "Pilot decision outputs are decision-support guidance, not final investment approval.",
            "Real PLN/site/vendor/port/offtake/MRV evidence must be verified before a single-pilot decision.",
        ],
    }
