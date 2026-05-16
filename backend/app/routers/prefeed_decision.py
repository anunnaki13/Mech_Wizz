from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pre_feed_decision import (
    PreFeedDecisionBlockerRead,
    PreFeedDecisionDashboardRead,
    PreFeedDecisionGateCreate,
    PreFeedDecisionGateRead,
    PreFeedDecisionGateSummaryRead,
    PreFeedDecisionGateUpdate,
    PreFeedDecisionNextActionRead,
    PreFeedRiskCreate,
    PreFeedRiskRead,
    PreFeedRiskSummaryRead,
    PreFeedRiskUpdate,
)
from app.services.prefeed_decision import (
    PreFeedDecisionInputError,
    build_decision_blockers,
    build_decision_gate_summary,
    build_next_actions,
    build_prefeed_decision_dashboard,
    build_risk_summary,
    create_decision_gate,
    create_risk,
    delete_decision_gate,
    delete_risk,
    list_decision_gates,
    list_risks,
    update_decision_gate,
    update_risk,
)


router = APIRouter(prefix="/prefeed", tags=["prefeed-decision"])


def _bad_request(exc: PreFeedDecisionInputError) -> HTTPException:
    detail = str(exc)
    status_code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=status_code, detail=detail)


@router.get("/packages/{package_id}/risks", response_model=list[PreFeedRiskRead])
def read_risks(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_risks(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.post("/packages/{package_id}/risks", response_model=PreFeedRiskRead, status_code=status.HTTP_201_CREATED)
def create_prefeed_risk(package_id: str, payload: PreFeedRiskCreate, db: Session = Depends(get_db)):
    try:
        return create_risk(db, package_id, payload)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/risks/{risk_id}", response_model=PreFeedRiskRead)
def update_prefeed_risk(risk_id: str, payload: PreFeedRiskUpdate, db: Session = Depends(get_db)):
    try:
        return update_risk(db, risk_id, payload)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/risks/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_risk(risk_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_risk(db, risk_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/risk-summary", response_model=PreFeedRiskSummaryRead)
def read_risk_summary(package_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return build_risk_summary(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/decision-gates", response_model=list[PreFeedDecisionGateRead])
def read_decision_gates(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_decision_gates(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/decision-gates",
    response_model=PreFeedDecisionGateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_decision_gate(
    package_id: str,
    payload: PreFeedDecisionGateCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_decision_gate(db, package_id, payload)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/decision-gates/{gate_id}", response_model=PreFeedDecisionGateRead)
def update_prefeed_decision_gate(
    gate_id: str,
    payload: PreFeedDecisionGateUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_decision_gate(db, gate_id, payload)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/decision-gates/{gate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_decision_gate(gate_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_decision_gate(db, gate_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/decision-gate-summary", response_model=PreFeedDecisionGateSummaryRead)
def read_decision_gate_summary(package_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return build_decision_gate_summary(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/decision-blockers", response_model=list[PreFeedDecisionBlockerRead])
def read_decision_blockers(package_id: str, db: Session = Depends(get_db)) -> list[dict]:
    try:
        return build_decision_blockers(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/decision-next-actions", response_model=list[PreFeedDecisionNextActionRead])
def read_decision_next_actions(package_id: str, db: Session = Depends(get_db)) -> list[dict]:
    try:
        return build_next_actions(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/decision-dashboard", response_model=PreFeedDecisionDashboardRead)
def read_decision_dashboard(package_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return build_prefeed_decision_dashboard(db, package_id)
    except PreFeedDecisionInputError as exc:
        raise _bad_request(exc) from exc
