from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shortlist import ShortlistDecisionMatrix
from app.services.shortlist import build_shortlist_decision_matrix


router = APIRouter(prefix="/shortlist", tags=["shortlist"])


@router.get("/decision-matrix", response_model=ShortlistDecisionMatrix)
def get_shortlist_decision_matrix(
    scheme: str = Query(default="align", pattern="^(access|align|augment|all)$"),
    top_n: int = Query(default=5, ge=3, le=10),
    db: Session = Depends(get_db),
) -> dict:
    return build_shortlist_decision_matrix(db, scheme=scheme, top_n=top_n)
