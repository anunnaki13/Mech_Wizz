from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pre_feed_cost import (
    PreFeedCostBasisSelectionCreate,
    PreFeedCostBasisSelectionRead,
    PreFeedCostItemCreate,
    PreFeedCostItemRead,
    PreFeedCostItemUpdate,
    PreFeedCostSummaryRead,
    PreFeedVendorComparisonRead,
    PreFeedVendorGapRead,
    PreFeedVendorProposalCreate,
    PreFeedVendorProposalRead,
    PreFeedVendorProposalUpdate,
)
from app.services.prefeed_costs import (
    PreFeedCostInputError,
    build_cost_summary,
    build_vendor_comparison,
    create_cost_item,
    create_vendor_proposal,
    delete_cost_item,
    delete_vendor_proposal,
    generate_vendor_gaps,
    get_active_cost_basis,
    list_cost_items,
    list_vendor_proposals,
    select_active_cost_basis,
    update_cost_item,
    update_vendor_proposal,
)


router = APIRouter(prefix="/prefeed", tags=["prefeed-costs"])


def _bad_request(exc: PreFeedCostInputError) -> HTTPException:
    detail = str(exc)
    status_code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=status_code, detail=detail)


@router.get("/packages/{package_id}/cost-items", response_model=list[PreFeedCostItemRead])
def read_cost_items(
    package_id: str,
    vendor_proposal_id: str | None = None,
    db: Session = Depends(get_db),
) -> list:
    try:
        return list_cost_items(db, package_id, vendor_proposal_id=vendor_proposal_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/cost-items",
    response_model=PreFeedCostItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_cost_item(package_id: str, payload: PreFeedCostItemCreate, db: Session = Depends(get_db)):
    try:
        return create_cost_item(db, package_id, payload)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/cost-items/{cost_item_id}", response_model=PreFeedCostItemRead)
def update_prefeed_cost_item(cost_item_id: str, payload: PreFeedCostItemUpdate, db: Session = Depends(get_db)):
    try:
        return update_cost_item(db, cost_item_id, payload)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/cost-items/{cost_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_cost_item(cost_item_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_cost_item(db, cost_item_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/cost-summary", response_model=PreFeedCostSummaryRead)
def read_cost_summary(
    package_id: str,
    vendor_proposal_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return build_cost_summary(db, package_id, vendor_proposal_id=vendor_proposal_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/vendor-proposals", response_model=list[PreFeedVendorProposalRead])
def read_vendor_proposals(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_vendor_proposals(db, package_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/vendor-proposals",
    response_model=PreFeedVendorProposalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_vendor_proposal(
    package_id: str,
    payload: PreFeedVendorProposalCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_vendor_proposal(db, package_id, payload)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/vendor-proposals/{proposal_id}", response_model=PreFeedVendorProposalRead)
def update_prefeed_vendor_proposal(
    proposal_id: str,
    payload: PreFeedVendorProposalUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_vendor_proposal(db, proposal_id, payload)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/vendor-proposals/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_vendor_proposal(proposal_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_vendor_proposal(db, proposal_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/vendor-comparison", response_model=list[PreFeedVendorComparisonRead])
def read_vendor_comparison(package_id: str, db: Session = Depends(get_db)) -> list[dict]:
    try:
        return build_vendor_comparison(db, package_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/vendor-proposals/{proposal_id}/gaps", response_model=list[PreFeedVendorGapRead])
def read_vendor_gaps(proposal_id: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:
    try:
        return generate_vendor_gaps(db, proposal_id)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/scenarios/{scenario_id}/active-cost-basis", response_model=PreFeedCostBasisSelectionRead | None)
def read_active_cost_basis(scenario_id: str, db: Session = Depends(get_db)):
    return get_active_cost_basis(db, scenario_id)


@router.post("/scenarios/{scenario_id}/active-cost-basis", response_model=PreFeedCostBasisSelectionRead)
def select_prefeed_active_cost_basis(
    scenario_id: str,
    payload: PreFeedCostBasisSelectionCreate,
    db: Session = Depends(get_db),
):
    try:
        return select_active_cost_basis(db, scenario_id, payload)
    except PreFeedCostInputError as exc:
        raise _bad_request(exc) from exc
