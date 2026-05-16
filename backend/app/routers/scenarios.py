from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BusinessScenario, FinancialAssumption, Plant, ScenarioResult
from app.schemas.business_scenario import BusinessScenarioCreate, BusinessScenarioRead, BusinessScenarioUpdate
from app.schemas.financial_assumption import (
    FinancialAssumptionCreate,
    FinancialAssumptionRead,
    FinancialAssumptionUpdate,
)
from app.schemas.scenario_result import ScenarioResultRead
from app.services.scenario_simulation import SimulationInputError, run_scenario_simulation


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


def get_scenario_result_or_404(result_id: str, db: Session) -> ScenarioResult:
    result = db.get(ScenarioResult, result_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario result not found")
    return result


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


@router.post("/scenarios/{scenario_id}/simulate", response_model=ScenarioResultRead)
def simulate_scenario(scenario_id: str, db: Session = Depends(get_db)) -> ScenarioResult:
    get_scenario_or_404(scenario_id, db)
    try:
        return run_scenario_simulation(db, scenario_id)
    except SimulationInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/scenarios/{scenario_id}/results", response_model=list[ScenarioResultRead])
def list_scenario_results(scenario_id: str, db: Session = Depends(get_db)) -> list[ScenarioResult]:
    get_scenario_or_404(scenario_id, db)
    return list(
        db.scalars(
            select(ScenarioResult)
            .where(ScenarioResult.scenario_id == scenario_id)
            .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
        )
    )


@router.get("/scenario-results/{result_id}", response_model=ScenarioResultRead)
def read_scenario_result(result_id: str, db: Session = Depends(get_db)) -> ScenarioResult:
    return get_scenario_result_or_404(result_id, db)
