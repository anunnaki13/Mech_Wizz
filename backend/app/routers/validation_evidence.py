from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.validation_evidence import (
    ValidationEvidenceCreate,
    ValidationEvidenceRead,
    ValidationEvidenceUpdate,
    ValidationEvidenceWorkspace,
)
from app.services.validation_evidence import (
    ValidationEvidenceInputError,
    build_evidence_workspace,
    create_validation_evidence,
    update_validation_evidence,
)


router = APIRouter(prefix="/evidence", tags=["validation-evidence"])


def _bad_request(exc: ValidationEvidenceInputError) -> HTTPException:
    detail = str(exc)
    status_code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=status_code, detail=detail)


@router.get("/workspace", response_model=ValidationEvidenceWorkspace)
def get_evidence_workspace(
    scheme: str = Query(default="align", pattern="^(access|align|augment|all)$"),
    limit: int = Query(default=3, ge=1, le=5),
    db: Session = Depends(get_db),
) -> dict:
    return build_evidence_workspace(db, scheme=scheme, limit=limit)


@router.post("/records", response_model=ValidationEvidenceRead, status_code=status.HTTP_201_CREATED)
def create_evidence_record(payload: ValidationEvidenceCreate, db: Session = Depends(get_db)):
    try:
        return create_validation_evidence(db, payload)
    except ValidationEvidenceInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/records/{record_id}", response_model=ValidationEvidenceRead)
def update_evidence_record(record_id: str, payload: ValidationEvidenceUpdate, db: Session = Depends(get_db)):
    try:
        return update_validation_evidence(db, record_id, payload)
    except ValidationEvidenceInputError as exc:
        raise _bad_request(exc) from exc
