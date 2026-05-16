from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scoring import ScoringRecalculateRequest, ScoringRecalculateResponse, UnitRankingRow
from app.services.scoring import (
    ScoringInputError,
    latest_scoring_records,
    ranking_row_from_record,
    recalculate_unit_scoring,
)


router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/recalculate", response_model=ScoringRecalculateResponse)
def recalculate_scoring(
    payload: ScoringRecalculateRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> dict:
    try:
        scoring_run_id, records = recalculate_unit_scoring(
            db,
            scenario_id=payload.scenario_id if payload else None,
            scheme=payload.scheme if payload else None,
        )
    except ScoringInputError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {
        "scoring_run_id": scoring_run_id,
        "created_count": len(records),
        "results": records,
    }


@router.get("/unit-ranking", response_model=list[UnitRankingRow])
def list_unit_ranking(
    scenario_id: str | None = None,
    scheme: str | None = None,
    region: str | None = None,
    fuel_type: str | None = None,
    confidence: str | None = Query(default=None, pattern="^(all|high|medium|low|unknown)$"),
    opportunity_level: str | None = Query(default=None, pattern="^(all|low|medium|high|priority)$"),
    db: Session = Depends(get_db),
) -> list[dict]:
    records = latest_scoring_records(
        db,
        scenario_id=scenario_id,
        scheme=scheme,
        region=region,
        fuel_type=fuel_type,
        confidence=confidence,
        opportunity_filter=opportunity_level,
    )
    return [ranking_row_from_record(record) for record in records]
