from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HydrogenStrategy, Plant
from app.schemas.hydrogen_strategy import HydrogenStrategyCreate, HydrogenStrategyRead, HydrogenStrategyUpdate


router = APIRouter(tags=["hydrogen-strategy"])


def get_plant_or_404(plant_id: str, db: Session) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


def get_hydrogen_strategy_or_404(record_id: str, db: Session) -> HydrogenStrategy:
    record = db.get(HydrogenStrategy, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hydrogen strategy not found")
    return record


@router.get("/plants/{plant_id}/hydrogen-strategy", response_model=HydrogenStrategyRead | None)
def read_hydrogen_strategy(plant_id: str, db: Session = Depends(get_db)) -> HydrogenStrategy | None:
    get_plant_or_404(plant_id, db)
    return db.scalar(select(HydrogenStrategy).where(HydrogenStrategy.plant_id == plant_id))


@router.post(
    "/plants/{plant_id}/hydrogen-strategy",
    response_model=HydrogenStrategyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_hydrogen_strategy(
    plant_id: str,
    payload: HydrogenStrategyCreate,
    db: Session = Depends(get_db),
) -> HydrogenStrategy:
    get_plant_or_404(plant_id, db)
    record = HydrogenStrategy(plant_id=plant_id, **payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hydrogen strategy already exists") from exc
    db.refresh(record)
    return record


@router.put("/hydrogen-strategy/{record_id}", response_model=HydrogenStrategyRead)
def update_hydrogen_strategy(
    record_id: str,
    payload: HydrogenStrategyUpdate,
    db: Session = Depends(get_db),
) -> HydrogenStrategy:
    record = get_hydrogen_strategy_or_404(record_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record
