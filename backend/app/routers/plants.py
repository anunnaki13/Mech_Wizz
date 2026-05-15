from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plant
from app.schemas.plant import PlantCreate, PlantRead, PlantUpdate


router = APIRouter(prefix="/plants", tags=["plants"])


def get_plant_or_404(plant_id: str, db: Session) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


@router.get("/", response_model=list[PlantRead])
def list_plants(db: Session = Depends(get_db)) -> list[Plant]:
    return list(db.scalars(select(Plant).order_by(Plant.plant_name, Plant.unit_name)))


@router.post("/", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
def create_plant(payload: PlantCreate, db: Session = Depends(get_db)) -> Plant:
    plant = Plant(**payload.model_dump())
    db.add(plant)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plant already exists") from exc
    db.refresh(plant)
    return plant


@router.get("/{plant_id}", response_model=PlantRead)
def read_plant(plant_id: str, db: Session = Depends(get_db)) -> Plant:
    return get_plant_or_404(plant_id, db)


@router.put("/{plant_id}", response_model=PlantRead)
def update_plant(plant_id: str, payload: PlantUpdate, db: Session = Depends(get_db)) -> Plant:
    plant = get_plant_or_404(plant_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plant, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plant already exists") from exc
    db.refresh(plant)
    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(plant_id: str, db: Session = Depends(get_db)) -> None:
    plant = get_plant_or_404(plant_id, db)
    db.delete(plant)
    db.commit()
