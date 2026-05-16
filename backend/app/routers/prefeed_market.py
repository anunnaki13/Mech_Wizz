from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pre_feed_market import (
    PreFeedGapRead,
    PreFeedMrvAssumptionCreate,
    PreFeedMrvAssumptionRead,
    PreFeedMrvAssumptionUpdate,
    PreFeedMrvSummaryRead,
    PreFeedOfftakeProspectCreate,
    PreFeedOfftakeProspectRead,
    PreFeedOfftakeProspectUpdate,
    PreFeedOfftakeSummaryRead,
    PreFeedPriceDeckCreate,
    PreFeedPriceDeckRead,
    PreFeedPriceDeckUpdate,
)
from app.services.prefeed_market import (
    PreFeedMarketInputError,
    activate_price_deck,
    build_mrv_summary,
    build_offtake_summary,
    create_mrv_assumption,
    create_offtake_prospect,
    create_price_deck,
    delete_mrv_assumption,
    delete_offtake_prospect,
    delete_price_deck,
    generate_mrv_gaps,
    generate_offtake_gaps,
    list_mrv_assumptions,
    list_offtake_prospects,
    list_price_decks,
    update_mrv_assumption,
    update_offtake_prospect,
    update_price_deck,
)


router = APIRouter(prefix="/prefeed", tags=["prefeed-market"])


def _bad_request(exc: PreFeedMarketInputError) -> HTTPException:
    detail = str(exc)
    status_code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=status_code, detail=detail)


@router.get("/packages/{package_id}/price-decks", response_model=list[PreFeedPriceDeckRead])
def read_price_decks(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_price_decks(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/price-decks",
    response_model=PreFeedPriceDeckRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_price_deck(package_id: str, payload: PreFeedPriceDeckCreate, db: Session = Depends(get_db)):
    try:
        return create_price_deck(db, package_id, payload)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/price-decks/{deck_id}", response_model=PreFeedPriceDeckRead)
def update_prefeed_price_deck(deck_id: str, payload: PreFeedPriceDeckUpdate, db: Session = Depends(get_db)):
    try:
        return update_price_deck(db, deck_id, payload)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.post("/price-decks/{deck_id}/activate", response_model=PreFeedPriceDeckRead)
def activate_prefeed_price_deck(deck_id: str, db: Session = Depends(get_db)):
    try:
        return activate_price_deck(db, deck_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/price-decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_price_deck(deck_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_price_deck(db, deck_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/offtake-prospects", response_model=list[PreFeedOfftakeProspectRead])
def read_offtake_prospects(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_offtake_prospects(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/offtake-prospects",
    response_model=PreFeedOfftakeProspectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_offtake_prospect(
    package_id: str,
    payload: PreFeedOfftakeProspectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_offtake_prospect(db, package_id, payload)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/offtake-prospects/{prospect_id}", response_model=PreFeedOfftakeProspectRead)
def update_prefeed_offtake_prospect(
    prospect_id: str,
    payload: PreFeedOfftakeProspectUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_offtake_prospect(db, prospect_id, payload)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/offtake-prospects/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_offtake_prospect(prospect_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_offtake_prospect(db, prospect_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/offtake-summary", response_model=PreFeedOfftakeSummaryRead)
def read_offtake_summary(package_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return build_offtake_summary(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/offtake-gaps", response_model=list[PreFeedGapRead])
def read_offtake_gaps(package_id: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:
    try:
        return generate_offtake_gaps(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/mrv-assumptions", response_model=list[PreFeedMrvAssumptionRead])
def read_mrv_assumptions(package_id: str, db: Session = Depends(get_db)) -> list:
    try:
        return list_mrv_assumptions(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.post(
    "/packages/{package_id}/mrv-assumptions",
    response_model=PreFeedMrvAssumptionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prefeed_mrv_assumption(
    package_id: str,
    payload: PreFeedMrvAssumptionCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_mrv_assumption(db, package_id, payload)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.put("/mrv-assumptions/{assumption_id}", response_model=PreFeedMrvAssumptionRead)
def update_prefeed_mrv_assumption(
    assumption_id: str,
    payload: PreFeedMrvAssumptionUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_mrv_assumption(db, assumption_id, payload)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.delete("/mrv-assumptions/{assumption_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prefeed_mrv_assumption(assumption_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_mrv_assumption(db, assumption_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/packages/{package_id}/mrv-summary", response_model=PreFeedMrvSummaryRead)
def read_mrv_summary(package_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return build_mrv_summary(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc


@router.get("/packages/{package_id}/mrv-gaps", response_model=list[PreFeedGapRead])
def read_mrv_gaps(package_id: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:
    try:
        return generate_mrv_gaps(db, package_id)
    except PreFeedMarketInputError as exc:
        raise _bad_request(exc) from exc
