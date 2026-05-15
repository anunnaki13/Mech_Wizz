from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EmissionTest, Plant
from app.schemas.emission_test import EmissionTestCreate, EmissionTestRead, EmissionTestUpdate


router = APIRouter(tags=["emission-tests"])


def get_plant_or_404(plant_id: str, db: Session) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


def get_emission_test_or_404(emission_test_id: str, db: Session) -> EmissionTest:
    emission_test = db.get(EmissionTest, emission_test_id)
    if emission_test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emission test not found")
    return emission_test


@router.get("/plants/{plant_id}/emission-tests", response_model=list[EmissionTestRead])
def list_emission_tests(plant_id: str, db: Session = Depends(get_db)) -> list[EmissionTest]:
    get_plant_or_404(plant_id, db)
    return list(
        db.scalars(
            select(EmissionTest)
            .where(EmissionTest.plant_id == plant_id)
            .order_by(EmissionTest.stack_id, EmissionTest.created_at)
        )
    )


@router.post(
    "/plants/{plant_id}/emission-tests",
    response_model=EmissionTestRead,
    status_code=status.HTTP_201_CREATED,
)
def create_emission_test(
    plant_id: str,
    payload: EmissionTestCreate,
    db: Session = Depends(get_db),
) -> EmissionTest:
    get_plant_or_404(plant_id, db)
    emission_test = EmissionTest(plant_id=plant_id, **payload.model_dump())
    db.add(emission_test)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Emission test already exists") from exc
    db.refresh(emission_test)
    return emission_test


@router.put("/emission-tests/{emission_test_id}", response_model=EmissionTestRead)
def update_emission_test(
    emission_test_id: str,
    payload: EmissionTestUpdate,
    db: Session = Depends(get_db),
) -> EmissionTest:
    emission_test = get_emission_test_or_404(emission_test_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emission_test, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Emission test already exists") from exc
    db.refresh(emission_test)
    return emission_test


@router.delete("/emission-tests/{emission_test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emission_test(emission_test_id: str, db: Session = Depends(get_db)) -> None:
    emission_test = get_emission_test_or_404(emission_test_id, db)
    db.delete(emission_test)
    db.commit()
