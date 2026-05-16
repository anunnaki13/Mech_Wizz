from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.llm import LlmGenerateRequest, LlmInsightRead
from app.services.llm import LlmInputError, LlmProviderError, generate_insight, list_insights


router = APIRouter(prefix="/llm", tags=["llm"])


def _generate_or_error(db: Session, insight_type: str, payload: LlmGenerateRequest | None, **kwargs) -> object:
    try:
        return generate_insight(
            db,
            insight_type,
            model_name=payload.model_name if payload else None,
            **kwargs,
        )
    except LlmInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LlmProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/insights", response_model=list[LlmInsightRead])
def read_insights(
    scenario_id: str | None = None,
    plant_id: str | None = None,
    document_id: str | None = None,
    insight_type: str | None = None,
    db: Session = Depends(get_db),
) -> list:
    return list_insights(
        db,
        scenario_id=scenario_id,
        plant_id=plant_id,
        document_id=document_id,
        insight_type=insight_type,
    )


@router.post("/summary/{scenario_id}", response_model=LlmInsightRead)
def generate_executive_summary(
    scenario_id: str,
    payload: LlmGenerateRequest | None = None,
    db: Session = Depends(get_db),
):
    return _generate_or_error(db, "executive_summary", payload, scenario_id=scenario_id)


@router.post("/data-gap/{plant_id}", response_model=LlmInsightRead)
def generate_data_gap_explanation(
    plant_id: str,
    scenario_id: str | None = Query(default=None),
    payload: LlmGenerateRequest | None = None,
    db: Session = Depends(get_db),
):
    return _generate_or_error(
        db,
        "data_gap_explanation",
        payload,
        plant_id=plant_id,
        scenario_id=scenario_id,
    )


@router.post("/investor-memo/{scenario_id}", response_model=LlmInsightRead)
def generate_investor_memo(
    scenario_id: str,
    payload: LlmGenerateRequest | None = None,
    db: Session = Depends(get_db),
):
    return _generate_or_error(db, "investor_memo", payload, scenario_id=scenario_id)


@router.post("/explain-sensitivity/{scenario_id}", response_model=LlmInsightRead)
def generate_sensitivity_explanation(
    scenario_id: str,
    payload: LlmGenerateRequest | None = None,
    db: Session = Depends(get_db),
):
    return _generate_or_error(db, "sensitivity_explanation", payload, scenario_id=scenario_id)
