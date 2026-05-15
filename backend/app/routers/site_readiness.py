from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plant, SiteReadiness
from app.schemas.site_readiness import SiteReadinessCreate, SiteReadinessRead, SiteReadinessUpdate


router = APIRouter(tags=["site-readiness"])


def get_plant_or_404(plant_id: str, db: Session) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


def get_site_readiness_or_404(record_id: str, db: Session) -> SiteReadiness:
    record = db.get(SiteReadiness, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site readiness not found")
    return record


@router.get("/plants/{plant_id}/site-readiness", response_model=SiteReadinessRead | None)
def read_site_readiness(plant_id: str, db: Session = Depends(get_db)) -> SiteReadiness | None:
    get_plant_or_404(plant_id, db)
    return db.scalar(select(SiteReadiness).where(SiteReadiness.plant_id == plant_id))


@router.post(
    "/plants/{plant_id}/site-readiness",
    response_model=SiteReadinessRead,
    status_code=status.HTTP_201_CREATED,
)
def create_site_readiness(
    plant_id: str,
    payload: SiteReadinessCreate,
    db: Session = Depends(get_db),
) -> SiteReadiness:
    get_plant_or_404(plant_id, db)
    record = SiteReadiness(plant_id=plant_id, **payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Site readiness already exists") from exc
    db.refresh(record)
    return record


@router.put("/site-readiness/{record_id}", response_model=SiteReadinessRead)
def update_site_readiness(
    record_id: str,
    payload: SiteReadinessUpdate,
    db: Session = Depends(get_db),
) -> SiteReadiness:
    record = get_site_readiness_or_404(record_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record
