from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pilot_decision import PilotDecisionDashboard
from app.services.pilot_decision import build_pilot_decision_dashboard


router = APIRouter(prefix="/pilot-decision", tags=["pilot-decision"])


@router.get("", response_model=PilotDecisionDashboard)
def get_pilot_decision_dashboard(
    scheme: str = Query(default="align", pattern="^(access|align|augment|all)$"),
    limit: int = Query(default=3, ge=1, le=5),
    db: Session = Depends(get_db),
) -> dict:
    return build_pilot_decision_dashboard(db, scheme=scheme, limit=limit)
