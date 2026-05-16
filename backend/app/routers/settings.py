from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.application_setting import ApplicationSettingRead, ApplicationSettingUpdate
from app.schemas.data_quality import DataQualitySummaryRead
from app.services.data_quality import build_data_quality_summary
from app.services.settings import SettingInputError, get_setting, list_settings, seed_default_settings, update_setting


router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=list[ApplicationSettingRead])
def read_settings(category: str | None = None, db: Session = Depends(get_db)) -> list:
    records = list_settings(db, category)
    if not records:
        seed_default_settings(db)
        records = list_settings(db, category)
    return records


@router.get("/settings/{key}", response_model=ApplicationSettingRead)
def read_setting(key: str, db: Session = Depends(get_db)):
    record = get_setting(db, key)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return record


@router.put("/settings/{key}", response_model=ApplicationSettingRead)
def save_setting(key: str, payload: ApplicationSettingUpdate, db: Session = Depends(get_db)):
    try:
        return update_setting(
            db,
            key=key,
            value=payload.value,
            data_status=payload.data_status,
            confidence_level=payload.confidence_level,
        )
    except SettingInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/data-quality/summary", response_model=DataQualitySummaryRead)
def read_data_quality_summary(
    plant_id: str,
    scenario_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    return build_data_quality_summary(db, plant_id=plant_id, scenario_id=scenario_id)
