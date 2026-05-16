from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BusinessScenario, FinancialAssumption, Plant
from app.schemas.business_scenario import BusinessScenarioCreate, BusinessScenarioRead, BusinessScenarioUpdate
from app.schemas.financial_assumption import (
    FinancialAssumptionCreate,
    FinancialAssumptionRead,
    FinancialAssumptionUpdate,
)


router = APIRouter(tags=["scenarios"])


def get_plant_or_404(plant_id: str, db: Session) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


def get_scenario_or_404(scenario_id: str, db: Session) -> BusinessScenario:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return scenario


def get_financial_assumption(scenario_id: str, db: Session) -> FinancialAssumption | None:
    return db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario_id))


@router.get("/plants/{plant_id}/scenarios", response_model=list[BusinessScenarioRead])
def list_plant_scenarios(plant_id: str, db: Session = Depends(get_db)) -> list[BusinessScenario]:
    get_plant_or_404(plant_id, db)
    return list(
        db.scalars(
            select(BusinessScenario)
            .where(BusinessScenario.plant_id == plant_id)
            .order_by(BusinessScenario.created_at, BusinessScenario.scenario_name)
        )
    )


@router.post(
    "/plants/{plant_id}/scenarios",
    response_model=BusinessScenarioRead,
    status_code=status.HTTP_201_CREATED,
)
def create_plant_scenario(
    plant_id: str,
    payload: BusinessScenarioCreate,
    db: Session = Depends(get_db),
) -> BusinessScenario:
    get_plant_or_404(plant_id, db)
    scenario = BusinessScenario(plant_id=plant_id, **payload.model_dump())
    db.add(scenario)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Scenario already exists") from exc
    db.refresh(scenario)
    return scenario


@router.get("/scenarios/{scenario_id}", response_model=BusinessScenarioRead)
def read_scenario(scenario_id: str, db: Session = Depends(get_db)) -> BusinessScenario:
    return get_scenario_or_404(scenario_id, db)


@router.put("/scenarios/{scenario_id}", response_model=BusinessScenarioRead)
def update_scenario(
    scenario_id: str,
    payload: BusinessScenarioUpdate,
    db: Session = Depends(get_db),
) -> BusinessScenario:
    scenario = get_scenario_or_404(scenario_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(scenario, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Scenario already exists") from exc
    db.refresh(scenario)
    return scenario


@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)) -> None:
    scenario = get_scenario_or_404(scenario_id, db)
    db.delete(scenario)
    db.commit()


@router.get("/scenarios/{scenario_id}/financial-assumptions", response_model=FinancialAssumptionRead | None)
def read_scenario_financial_assumption(
    scenario_id: str,
    db: Session = Depends(get_db),
) -> FinancialAssumption | None:
    get_scenario_or_404(scenario_id, db)
    return get_financial_assumption(scenario_id, db)


@router.post(
    "/scenarios/{scenario_id}/financial-assumptions",
    response_model=FinancialAssumptionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scenario_financial_assumption(
    scenario_id: str,
    payload: FinancialAssumptionCreate,
    db: Session = Depends(get_db),
) -> FinancialAssumption:
    get_scenario_or_404(scenario_id, db)
    record = FinancialAssumption(scenario_id=scenario_id, **payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Financial assumption already exists") from exc
    db.refresh(record)
    return record


@router.put("/scenarios/{scenario_id}/financial-assumptions", response_model=FinancialAssumptionRead)
def upsert_scenario_financial_assumption(
    scenario_id: str,
    payload: FinancialAssumptionUpdate,
    db: Session = Depends(get_db),
) -> FinancialAssumption:
    get_scenario_or_404(scenario_id, db)
    record = get_financial_assumption(scenario_id, db)
    if record is None:
        record = FinancialAssumption(scenario_id=scenario_id)
        db.add(record)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record
