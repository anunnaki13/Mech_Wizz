from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scoring import UnitProfileRead
from app.services.unit_profile import build_unit_profile


router = APIRouter(prefix="/units", tags=["unit profiles"])


@router.get("/{plant_id}/profile", response_model=UnitProfileRead)
def read_unit_profile(
    plant_id: str,
    scenario_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    profile = build_unit_profile(db, plant_id, scenario_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return profile
