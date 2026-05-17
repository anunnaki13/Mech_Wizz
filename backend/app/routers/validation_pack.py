from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.validation_pack import Top3ValidationPack
from app.services.validation_pack import build_top3_validation_pack, render_validation_pack_pdf


router = APIRouter(prefix="/validation-pack", tags=["validation-pack"])


@router.get("/top3", response_model=Top3ValidationPack)
def get_top3_validation_pack(
    scheme: str = Query(default="align", pattern="^(access|align|augment|all)$"),
    limit: int = Query(default=3, ge=1, le=5),
    db: Session = Depends(get_db),
) -> dict:
    return build_top3_validation_pack(db, scheme=scheme, limit=limit)


@router.get("/committee-memo.pdf")
def get_committee_memo_pdf(
    scheme: str = Query(default="align", pattern="^(access|align|augment|all)$"),
    limit: int = Query(default=3, ge=1, le=5),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    pack = build_top3_validation_pack(db, scheme=scheme, limit=limit)
    payload = render_validation_pack_pdf(pack)
    return StreamingResponse(
        BytesIO(payload),
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="MECH_WIZ_Top3_Validation_Committee_Memo.pdf"'},
    )
