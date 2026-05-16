from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pre_feed import (
    PreFeedPackageCreate,
    PreFeedPackageDocumentCreate,
    PreFeedPackageDocumentRead,
    PreFeedPackageGapRead,
    PreFeedPackageRead,
    PreFeedPackageUpdate,
)
from app.services.prefeed import (
    PreFeedInputError,
    archive_package,
    create_package,
    generate_package_gaps,
    get_package_or_raise,
    link_package_document,
    list_package_documents,
    list_packages,
    unlink_package_document,
    update_package,
)


router = APIRouter(prefix="/prefeed", tags=["prefeed"])


def _bad_request(exc: PreFeedInputError) -> HTTPException:
    detail = str(exc)
    status_code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=status_code, detail=detail)


@router.get("/packages", response_model=list[PreFeedPackageRead])
def read_prefeed_packages(
    plant_id: str | None = None,
    scenario_id: str | None = None,
    include_archived: bool = False,
    db: Session = Depends(get_db),
) -> list:
    return list_packages(db, plant_id=plant_id, scenario_id=scenario_id, include_archived=include_archived)


@router.post("/packages", response_model=PreFeedPackageRead, status_code=status.HTTP_201_CREATED)
def create_prefeed_package(payload: PreFeedPackageCreate, db: Session = Depends(get_db)):
    try:
        return create_package(db, payload)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}", response_model=PreFeedPackageRead)
def read_prefeed_package(package_id: str, db: Session = Depends(get_db)):
    try:
        return get_package_or_raise(db, package_id)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/packages/{package_id}", response_model=PreFeedPackageRead)
def update_prefeed_package(package_id: str, payload: PreFeedPackageUpdate, db: Session = Depends(get_db)):
    try:
        return update_package(db, package_id, payload)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc


@router.post("/packages/{package_id}/archive", response_model=PreFeedPackageRead)
def archive_prefeed_package(package_id: str, db: Session = Depends(get_db)):
    try:
        return archive_package(db, package_id)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/documents", response_model=list[PreFeedPackageDocumentRead])
def read_prefeed_package_documents(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_package_documents(db, package_id)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/documents",
    response_model=PreFeedPackageDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_package_document_link(
    package_id: str,
    payload: PreFeedPackageDocumentCreate,
    db: Session = Depends(get_db),
):
    try:
        return link_package_document(
            db,
            package_id,
            document_id=payload.document_id,
            document_role=payload.document_role,
            notes=payload.notes,
        )
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/packages/{package_id}/documents/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_package_document_link(package_id: str, link_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        unlink_package_document(db, package_id, link_id)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/gaps", response_model=list[PreFeedPackageGapRead])
def read_prefeed_package_gaps(package_id: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:
    try:
        return generate_package_gaps(db, package_id)
    except PreFeedInputError as exc:
        raise _bad_request(exc) from exc
