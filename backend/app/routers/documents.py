from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.document import DocumentAskRequest, DocumentRead
from app.schemas.llm import LlmInsightRead
from app.services.documents import (
    DocumentInputError,
    extract_document_text,
    get_document_or_raise,
    list_documents,
    save_uploaded_document,
)
from app.services.llm import LlmInputError, LlmProviderError, generate_insight


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    plant_id: str | None = Form(default=None),
    scenario_id: str | None = Form(default=None),
    document_category: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    try:
        content = await file.read()
        return save_uploaded_document(
            db,
            content=content,
            original_filename=file.filename or "document",
            file_type=file.content_type or "application/octet-stream",
            plant_id=plant_id,
            scenario_id=scenario_id,
            document_category=document_category,
        )
    except DocumentInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentRead])
def read_documents(
    plant_id: str | None = None,
    scenario_id: str | None = None,
    db: Session = Depends(get_db),
) -> list:
    return list_documents(db, plant_id=plant_id, scenario_id=scenario_id)


@router.get("/{document_id}", response_model=DocumentRead)
def read_document(document_id: str, db: Session = Depends(get_db)):
    try:
        return get_document_or_raise(db, document_id)
    except DocumentInputError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{document_id}/extract", response_model=DocumentRead)
def extract_document(document_id: str, db: Session = Depends(get_db)):
    try:
        return extract_document_text(db, document_id)
    except DocumentInputError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{document_id}/ask", response_model=LlmInsightRead)
def ask_document(document_id: str, payload: DocumentAskRequest, db: Session = Depends(get_db)):
    try:
        return generate_insight(
            db,
            "document_qa",
            document_id=document_id,
            question=payload.question,
            model_name=payload.model_name,
        )
    except LlmInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LlmProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
