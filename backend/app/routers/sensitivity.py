from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sensitivity import SensitivityResultRead, SensitivityRunRequest, SensitivityRunResponse
from app.services.sensitivity import SensitivityInputError, list_sensitivity_results, run_sensitivity_analysis


router = APIRouter(tags=["sensitivity"])


@router.post("/sensitivity/run", response_model=SensitivityRunResponse)
def run_sensitivity(
    payload: SensitivityRunRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        run_id, records = run_sensitivity_analysis(
            db,
            scenario_id=payload.scenario_id,
            plant_id=payload.plant_id,
            variables=payload.variables,
            low_multiplier=payload.low_multiplier,
            high_multiplier=payload.high_multiplier,
        )
    except SensitivityInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "run_id": run_id,
        "plant_id": records[0].plant_id if records else payload.plant_id or "",
        "scenario_id": payload.scenario_id,
        "scenario_result_id": records[0].scenario_result_id if records else None,
        "results": records,
    }


@router.get("/scenarios/{scenario_id}/sensitivity", response_model=list[SensitivityResultRead])
def read_sensitivity_results(
    scenario_id: str,
    plant_id: str | None = None,
    db: Session = Depends(get_db),
) -> list:
    return list_sensitivity_results(db, scenario_id=scenario_id, plant_id=plant_id)
