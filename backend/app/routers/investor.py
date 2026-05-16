from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.investor import InvestorCaseRead
from app.services.investor_case import InvestorCaseInputError, build_investor_case


router = APIRouter(tags=["investor"])


@router.get("/investor-case", response_model=InvestorCaseRead)
def read_investor_case(
    plant_id: str | None = None,
    scenario_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return build_investor_case(db, plant_id=plant_id, scenario_id=scenario_id)
    except InvestorCaseInputError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
