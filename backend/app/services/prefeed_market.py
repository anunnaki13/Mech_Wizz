from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    BusinessScenario,
    Document,
    FinancialAssumption,
    PreFeedMrvAssumption,
    PreFeedOfftakeProspect,
    PreFeedPackage,
    PreFeedPriceDeck,
    ScenarioResult,
)
from app.schemas.pre_feed_market import (
    CARBON_CREDIT_ELIGIBILITY_VALUES,
    MRV_VERIFICATION_STATUS_VALUES,
    OFFTAKE_PRODUCT_VALUES,
    OFFTAKE_STATUS_VALUES,
    PreFeedMrvAssumptionCreate,
    PreFeedMrvAssumptionUpdate,
    PreFeedOfftakeProspectCreate,
    PreFeedOfftakeProspectUpdate,
    PreFeedPriceDeckCreate,
    PreFeedPriceDeckUpdate,
)
from app.services.prefeed import get_package_or_raise


class PreFeedMarketInputError(ValueError):
    pass


OFFTAKE_STATUS_SCORE = {
    "inactive": 0.0,
    "lead": 0.2,
    "discussion": 0.35,
    "loi": 0.55,
    "term_sheet": 0.7,
    "contracted": 0.9,
    "signed": 1.0,
}

MRV_VERIFICATION_SCORE = {
    "not_started": 0.0,
    "method_selected": 0.35,
    "data_collected": 0.6,
    "third_party_review": 0.8,
    "verified": 1.0,
}

ELIGIBILITY_SCORE = {
    "unknown": 0.0,
    "screening": 0.35,
    "potentially_eligible": 0.65,
    "eligible": 1.0,
    "not_eligible": 0.0,
}

CONFIDENCE_SCORE = {"high": 1.0, "medium": 0.7, "low": 0.35, "unknown": 0.1}


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def _validate_choice(value: str, allowed: tuple[str, ...], label: str) -> None:
    if value not in allowed:
        raise PreFeedMarketInputError(f"Unsupported {label}: {value}")


def _get_document_or_raise(db: Session, document_id: str) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise PreFeedMarketInputError("Supporting document not found")
    return document


def _validate_document_matches_package(package: PreFeedPackage, document: Document) -> None:
    if document.plant_id and document.plant_id != package.plant_id:
        raise PreFeedMarketInputError("Document belongs to a different plant")
    if document.scenario_id and package.scenario_id and document.scenario_id != package.scenario_id:
        raise PreFeedMarketInputError("Document belongs to a different scenario")


def _validate_supporting_document(db: Session, package: PreFeedPackage, document_id: str | None) -> None:
    if document_id is None:
        return
    _validate_document_matches_package(package, _get_document_or_raise(db, document_id))


def _validate_scenario_matches_package(db: Session, package: PreFeedPackage, scenario_id: str | None) -> None:
    if scenario_id is None:
        return
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise PreFeedMarketInputError("Scenario not found")
    if scenario.plant_id != package.plant_id:
        raise PreFeedMarketInputError("Scenario belongs to a different plant")
    if package.scenario_id and scenario.id != package.scenario_id:
        raise PreFeedMarketInputError("Scenario does not match this package")


def _latest_result(db: Session, scenario_id: str | None) -> ScenarioResult | None:
    if not scenario_id:
        return None
    return db.scalar(
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
    )


def _confidence_score(confidence: str | None) -> float:
    return CONFIDENCE_SCORE.get(confidence or "unknown", 0.1)


def _gap(
    source_module: str,
    missing_data_name: str,
    impact_level: str,
    priority_level: str,
    owner: str,
    recommendation: str,
    confidence_level: str = "unknown",
) -> dict[str, str]:
    return {
        "source_module": source_module,
        "missing_data_name": missing_data_name,
        "impact_level": impact_level,
        "priority_level": priority_level,
        "owner": owner,
        "recommendation": recommendation,
        "status": "open",
        "confidence_level": confidence_level,
    }


def _get_price_deck_or_raise(db: Session, deck_id: str) -> PreFeedPriceDeck:
    deck = db.get(PreFeedPriceDeck, deck_id)
    if deck is None:
        raise PreFeedMarketInputError("Price deck not found")
    return deck


def list_price_decks(db: Session, package_id: str) -> list[PreFeedPriceDeck]:
    get_package_or_raise(db, package_id)
    return list(
        db.scalars(
            select(PreFeedPriceDeck)
            .where(PreFeedPriceDeck.package_id == package_id)
            .order_by(PreFeedPriceDeck.is_active.desc(), PreFeedPriceDeck.updated_at.desc(), PreFeedPriceDeck.id.desc())
        )
    )


def get_active_price_deck(db: Session, package_id: str) -> PreFeedPriceDeck | None:
    return db.scalar(
        select(PreFeedPriceDeck)
        .where(PreFeedPriceDeck.package_id == package_id, PreFeedPriceDeck.is_active.is_(True))
        .order_by(PreFeedPriceDeck.updated_at.desc(), PreFeedPriceDeck.id.desc())
    )


def _deactivate_price_decks(db: Session, package_id: str, except_id: str | None = None) -> None:
    for deck in db.scalars(
        select(PreFeedPriceDeck).where(PreFeedPriceDeck.package_id == package_id, PreFeedPriceDeck.is_active.is_(True))
    ):
        if deck.id != except_id:
            deck.is_active = False


def create_price_deck(db: Session, package_id: str, payload: PreFeedPriceDeckCreate) -> PreFeedPriceDeck:
    package = get_package_or_raise(db, package_id)
    _validate_scenario_matches_package(db, package, payload.scenario_id)
    if payload.is_active:
        _deactivate_price_decks(db, package.id)
    deck = PreFeedPriceDeck(
        package_id=package.id,
        scenario_id=payload.scenario_id or package.scenario_id,
        deck_name=payload.deck_name.strip(),
        is_active=payload.is_active,
        methanol_price_usd_per_ton=payload.methanol_price_usd_per_ton,
        carbon_credit_price_usd_per_ton=payload.carbon_credit_price_usd_per_ton,
        electricity_price_usd_per_kwh=payload.electricity_price_usd_per_kwh,
        hydrogen_price_usd_per_kg=payload.hydrogen_price_usd_per_kg,
        exchange_rate_idr_usd=payload.exchange_rate_idr_usd,
        escalation_percent=payload.escalation_percent,
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def update_price_deck(db: Session, deck_id: str, payload: PreFeedPriceDeckUpdate) -> PreFeedPriceDeck:
    deck = _get_price_deck_or_raise(db, deck_id)
    package = get_package_or_raise(db, deck.package_id)
    updates = payload.model_dump(exclude_unset=True)
    if "scenario_id" in updates:
        _validate_scenario_matches_package(db, package, updates["scenario_id"])
    if updates.get("is_active") is True:
        _deactivate_price_decks(db, deck.package_id, except_id=deck.id)
    for field, value in updates.items():
        if field == "deck_name" and isinstance(value, str):
            value = value.strip()
        if field == "notes" and isinstance(value, str):
            value = _clean_optional_text(value)
        setattr(deck, field, value)
    db.commit()
    db.refresh(deck)
    return deck


def activate_price_deck(db: Session, deck_id: str) -> PreFeedPriceDeck:
    deck = _get_price_deck_or_raise(db, deck_id)
    _deactivate_price_decks(db, deck.package_id, except_id=deck.id)
    deck.is_active = True
    db.commit()
    db.refresh(deck)
    return deck


def delete_price_deck(db: Session, deck_id: str) -> None:
    deck = _get_price_deck_or_raise(db, deck_id)
    db.delete(deck)
    db.commit()


def _get_offtake_or_raise(db: Session, prospect_id: str) -> PreFeedOfftakeProspect:
    prospect = db.scalar(
        select(PreFeedOfftakeProspect)
        .where(PreFeedOfftakeProspect.id == prospect_id)
        .options(selectinload(PreFeedOfftakeProspect.supporting_document))
    )
    if prospect is None:
        raise PreFeedMarketInputError("Offtake prospect not found")
    return prospect


def list_offtake_prospects(db: Session, package_id: str) -> list[PreFeedOfftakeProspect]:
    get_package_or_raise(db, package_id)
    return list(
        db.scalars(
            select(PreFeedOfftakeProspect)
            .where(PreFeedOfftakeProspect.package_id == package_id)
            .options(selectinload(PreFeedOfftakeProspect.supporting_document))
            .order_by(PreFeedOfftakeProspect.updated_at.desc(), PreFeedOfftakeProspect.id.desc())
        )
    )


def create_offtake_prospect(
    db: Session,
    package_id: str,
    payload: PreFeedOfftakeProspectCreate,
) -> PreFeedOfftakeProspect:
    package = get_package_or_raise(db, package_id)
    _validate_choice(payload.product, OFFTAKE_PRODUCT_VALUES, "offtake product")
    _validate_choice(payload.status, OFFTAKE_STATUS_VALUES, "offtake status")
    _validate_supporting_document(db, package, payload.supporting_document_id)
    prospect = PreFeedOfftakeProspect(
        package_id=package.id,
        supporting_document_id=payload.supporting_document_id,
        counterparty_name=payload.counterparty_name.strip(),
        product=payload.product,
        target_volume_tpy=payload.target_volume_tpy,
        term_years=payload.term_years,
        pricing_basis=_clean_optional_text(payload.pricing_basis),
        price_usd_per_ton=payload.price_usd_per_ton,
        status=payload.status,
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(prospect)
    db.commit()
    db.refresh(prospect)
    return _get_offtake_or_raise(db, prospect.id)


def update_offtake_prospect(
    db: Session,
    prospect_id: str,
    payload: PreFeedOfftakeProspectUpdate,
) -> PreFeedOfftakeProspect:
    prospect = _get_offtake_or_raise(db, prospect_id)
    package = get_package_or_raise(db, prospect.package_id)
    updates = payload.model_dump(exclude_unset=True)
    if "product" in updates and updates["product"]:
        _validate_choice(updates["product"], OFFTAKE_PRODUCT_VALUES, "offtake product")
    if "status" in updates and updates["status"]:
        _validate_choice(updates["status"], OFFTAKE_STATUS_VALUES, "offtake status")
    if "supporting_document_id" in updates:
        _validate_supporting_document(db, package, updates["supporting_document_id"])
    for field, value in updates.items():
        if field == "counterparty_name" and isinstance(value, str):
            value = value.strip()
        if field in {"pricing_basis", "notes"} and isinstance(value, str):
            value = _clean_optional_text(value)
        setattr(prospect, field, value)
    db.commit()
    db.refresh(prospect)
    return _get_offtake_or_raise(db, prospect.id)


def delete_offtake_prospect(db: Session, prospect_id: str) -> None:
    prospect = _get_offtake_or_raise(db, prospect_id)
    db.delete(prospect)
    db.commit()


def _price_for_prospect(prospect: PreFeedOfftakeProspect, deck: PreFeedPriceDeck | None) -> float | None:
    if prospect.price_usd_per_ton is not None:
        return prospect.price_usd_per_ton
    if deck is None:
        return None
    if prospect.product == "carbon_credit":
        return deck.carbon_credit_price_usd_per_ton
    if prospect.product == "hydrogen":
        return deck.hydrogen_price_usd_per_kg
    return deck.methanol_price_usd_per_ton


def _offtake_readiness(
    prospects: list[PreFeedOfftakeProspect],
    deck: PreFeedPriceDeck | None,
    result: ScenarioResult | None,
) -> tuple[float, dict[str, float], float | None]:
    active = [prospect for prospect in prospects if prospect.status != "inactive"]
    methanol_volume = sum(prospect.target_volume_tpy or 0 for prospect in active if prospect.product == "e_methanol")
    scenario_methanol = result.methanol_ton_per_year if result and result.methanol_ton_per_year else None
    volume_coverage = None if not scenario_methanol else min(methanol_volume / scenario_methanol, 1.0)
    status_score = max((OFFTAKE_STATUS_SCORE.get(prospect.status, 0) for prospect in active), default=0.0)
    term_score = max((min((prospect.term_years or 0) / 10, 1.0) for prospect in active), default=0.0)
    pricing_scores = []
    for prospect in active:
        price = _price_for_prospect(prospect, deck)
        if price is not None and prospect.pricing_basis:
            pricing_scores.append(1.0)
        elif price is not None or prospect.pricing_basis:
            pricing_scores.append(0.5)
        else:
            pricing_scores.append(0.0)
    pricing_score = sum(pricing_scores) / len(pricing_scores) if pricing_scores else 0.0
    evidence_scores = [
        (0.45 if prospect.supporting_document_id else 0.0) + (0.55 * _confidence_score(prospect.confidence_level))
        for prospect in active
    ]
    evidence_score = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.0
    components = {
        "counterparty_status": round(status_score, 4),
        "volume_coverage": round(volume_coverage or 0.0, 4),
        "term_certainty": round(term_score, 4),
        "pricing_clarity": round(pricing_score, 4),
        "document_confidence": round(evidence_score, 4),
    }
    readiness = (
        0.25 * components["counterparty_status"]
        + 0.25 * components["volume_coverage"]
        + 0.20 * components["term_certainty"]
        + 0.20 * components["pricing_clarity"]
        + 0.10 * components["document_confidence"]
    )
    return round(readiness, 4), components, volume_coverage


def build_offtake_summary(db: Session, package_id: str) -> dict:
    package = get_package_or_raise(db, package_id)
    prospects = list_offtake_prospects(db, package_id)
    deck = get_active_price_deck(db, package_id)
    result = _latest_result(db, package.scenario_id)
    warnings: list[str] = []

    active = [prospect for prospect in prospects if prospect.status != "inactive"]
    methanol_revenue = 0.0
    methanol_revenue_known = False
    methanol_volume = 0.0
    carbon_revenue: float | None = None
    carbon_volume = sum(prospect.target_volume_tpy or 0 for prospect in active if prospect.product == "carbon_credit")

    for prospect in active:
        if prospect.product != "e_methanol" or prospect.target_volume_tpy is None:
            continue
        methanol_volume += prospect.target_volume_tpy
        price = _price_for_prospect(prospect, deck)
        if price is not None:
            methanol_revenue += prospect.target_volume_tpy * price
            methanol_revenue_known = True

    if carbon_volume > 0 and deck and deck.carbon_credit_price_usd_per_ton is not None:
        carbon_revenue = carbon_volume * deck.carbon_credit_price_usd_per_ton
    elif result and result.captured_co2_ton_per_year is not None and deck and deck.carbon_credit_price_usd_per_ton is not None:
        carbon_revenue = result.captured_co2_ton_per_year * deck.carbon_credit_price_usd_per_ton

    if deck is None:
        warnings.append("No active price deck selected for this package.")
    if not active:
        warnings.append("No active offtake prospects recorded for this package.")
    if result is None:
        warnings.append("No stored scenario result is available for volume coverage or carbon revenue context.")
    if methanol_volume > 0 and not methanol_revenue_known:
        warnings.append("Methanol offtake volume exists but no prospect or active deck methanol price is available.")

    gross_revenue = None
    if methanol_revenue_known or carbon_revenue is not None:
        gross_revenue = (methanol_revenue if methanol_revenue_known else 0) + (carbon_revenue or 0)

    readiness, components, coverage = _offtake_readiness(prospects, deck, result)
    patch = {}
    if deck:
        if deck.methanol_price_usd_per_ton is not None:
            patch["methanol_price_usd_per_ton"] = deck.methanol_price_usd_per_ton
        if deck.hydrogen_price_usd_per_kg is not None:
            patch["hydrogen_price_usd_per_kg"] = deck.hydrogen_price_usd_per_kg
        if deck.electricity_price_usd_per_kwh is not None:
            patch["electricity_price_usd_per_kwh"] = deck.electricity_price_usd_per_kwh
        if deck.exchange_rate_idr_usd is not None:
            patch["exchange_rate_idr_usd"] = deck.exchange_rate_idr_usd
        if deck.carbon_credit_price_usd_per_ton is not None and deck.exchange_rate_idr_usd is not None:
            patch["carbon_credit_price_idr_per_ton"] = round(
                deck.carbon_credit_price_usd_per_ton * deck.exchange_rate_idr_usd,
                2,
            )
    if gross_revenue is not None:
        patch["gross_revenue_usd_per_year"] = round(gross_revenue, 2)

    db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == package.scenario_id))
    return {
        "package_id": package.id,
        "scenario_id": package.scenario_id,
        "active_price_deck_id": deck.id if deck else None,
        "prospect_count": len(prospects),
        "methanol_volume_committed_tpy": round(methanol_volume, 2),
        "methanol_volume_coverage": _round(coverage),
        "methanol_revenue_usd_per_year": round(methanol_revenue, 2) if methanol_revenue_known else None,
        "carbon_credit_revenue_usd_per_year": round(carbon_revenue, 2) if carbon_revenue is not None else None,
        "gross_revenue_usd_per_year": round(gross_revenue, 2) if gross_revenue is not None else None,
        "readiness_score": readiness,
        "readiness_components": components,
        "scenario_ready_assumptions": patch,
        "warnings": warnings,
    }


def generate_offtake_gaps(db: Session, package_id: str) -> list[dict[str, str]]:
    prospects = list_offtake_prospects(db, package_id)
    deck = get_active_price_deck(db, package_id)
    gaps: list[dict[str, str]] = []
    if deck is None:
        gaps.append(_gap("prefeed_offtake", "Active price deck", "high", "high", "Commercial", "Select an active market price deck."))
    else:
        if deck.methanol_price_usd_per_ton is None:
            gaps.append(_gap("prefeed_offtake", "Methanol price", "high", "high", "Commercial", "Add methanol price to the active price deck.", deck.confidence_level))
        if deck.carbon_credit_price_usd_per_ton is None:
            gaps.append(_gap("prefeed_offtake", "Carbon credit price", "medium", "medium", "Commercial", "Add carbon credit price to support carbon revenue screening.", deck.confidence_level))
    active = [prospect for prospect in prospects if prospect.status != "inactive"]
    if not active:
        gaps.append(_gap("prefeed_offtake", "Offtake prospect", "high", "high", "Commercial", "Record at least one active offtake prospect or contract."))
    for prospect in active:
        confidence = prospect.confidence_level or "unknown"
        label = f"{prospect.counterparty_name} {prospect.product}".strip()
        if prospect.target_volume_tpy is None:
            gaps.append(_gap("prefeed_offtake", f"{label} target volume", "high", "high", "Commercial", "Record target offtake volume.", confidence))
        if not prospect.pricing_basis and prospect.price_usd_per_ton is None:
            gaps.append(_gap("prefeed_offtake", f"{label} pricing clarity", "medium", "medium", "Commercial", "Record pricing basis or fixed price.", confidence))
        if prospect.status in {"lead", "discussion"}:
            gaps.append(_gap("prefeed_offtake", f"{label} status", "medium", "medium", "Commercial", "Advance counterparty status beyond early discussion.", confidence))
        if prospect.supporting_document_id is None:
            gaps.append(_gap("prefeed_offtake", f"{label} supporting document", "medium", "medium", "Commercial", "Link LOI, term sheet, contract, or internal note evidence.", confidence))
        if confidence in {"low", "unknown"}:
            gaps.append(_gap("prefeed_offtake", f"{label} confidence", "medium", "medium", "Commercial", "Review evidence and update confidence level.", confidence))
    return gaps


def _get_mrv_or_raise(db: Session, assumption_id: str) -> PreFeedMrvAssumption:
    assumption = db.scalar(
        select(PreFeedMrvAssumption)
        .where(PreFeedMrvAssumption.id == assumption_id)
        .options(selectinload(PreFeedMrvAssumption.supporting_document))
    )
    if assumption is None:
        raise PreFeedMarketInputError("MRV assumption not found")
    return assumption


def list_mrv_assumptions(db: Session, package_id: str) -> list[PreFeedMrvAssumption]:
    get_package_or_raise(db, package_id)
    return list(
        db.scalars(
            select(PreFeedMrvAssumption)
            .where(PreFeedMrvAssumption.package_id == package_id)
            .options(selectinload(PreFeedMrvAssumption.supporting_document))
            .order_by(PreFeedMrvAssumption.updated_at.desc(), PreFeedMrvAssumption.id.desc())
        )
    )


def _latest_mrv_assumption(db: Session, package_id: str) -> PreFeedMrvAssumption | None:
    return db.scalar(
        select(PreFeedMrvAssumption)
        .where(PreFeedMrvAssumption.package_id == package_id)
        .options(selectinload(PreFeedMrvAssumption.supporting_document))
        .order_by(PreFeedMrvAssumption.updated_at.desc(), PreFeedMrvAssumption.id.desc())
    )


def create_mrv_assumption(db: Session, package_id: str, payload: PreFeedMrvAssumptionCreate) -> PreFeedMrvAssumption:
    package = get_package_or_raise(db, package_id)
    _validate_choice(payload.verification_status, MRV_VERIFICATION_STATUS_VALUES, "MRV verification status")
    _validate_choice(payload.carbon_credit_eligibility, CARBON_CREDIT_ELIGIBILITY_VALUES, "carbon credit eligibility")
    _validate_supporting_document(db, package, payload.supporting_document_id)
    assumption = PreFeedMrvAssumption(
        package_id=package.id,
        supporting_document_id=payload.supporting_document_id,
        baseline_emissions_tco2e_per_year=payload.baseline_emissions_tco2e_per_year,
        captured_co2_accounting_tpy=payload.captured_co2_accounting_tpy,
        product_carbon_intensity_tco2e_per_ton=payload.product_carbon_intensity_tco2e_per_ton,
        electricity_source=_clean_optional_text(payload.electricity_source),
        electricity_emission_factor_tco2e_per_mwh=payload.electricity_emission_factor_tco2e_per_mwh,
        methanol_pathway=_clean_optional_text(payload.methanol_pathway),
        carbon_credit_methodology=_clean_optional_text(payload.carbon_credit_methodology),
        verification_status=payload.verification_status,
        verifier_name=_clean_optional_text(payload.verifier_name),
        carbon_credit_eligibility=payload.carbon_credit_eligibility,
        eligibility_basis=_clean_optional_text(payload.eligibility_basis),
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(assumption)
    db.commit()
    db.refresh(assumption)
    return _get_mrv_or_raise(db, assumption.id)


def update_mrv_assumption(db: Session, assumption_id: str, payload: PreFeedMrvAssumptionUpdate) -> PreFeedMrvAssumption:
    assumption = _get_mrv_or_raise(db, assumption_id)
    package = get_package_or_raise(db, assumption.package_id)
    updates = payload.model_dump(exclude_unset=True)
    if "verification_status" in updates and updates["verification_status"]:
        _validate_choice(updates["verification_status"], MRV_VERIFICATION_STATUS_VALUES, "MRV verification status")
    if "carbon_credit_eligibility" in updates and updates["carbon_credit_eligibility"]:
        _validate_choice(updates["carbon_credit_eligibility"], CARBON_CREDIT_ELIGIBILITY_VALUES, "carbon credit eligibility")
    if "supporting_document_id" in updates:
        _validate_supporting_document(db, package, updates["supporting_document_id"])
    for field, value in updates.items():
        if field in {
            "electricity_source",
            "methanol_pathway",
            "carbon_credit_methodology",
            "verifier_name",
            "eligibility_basis",
            "notes",
        } and isinstance(value, str):
            value = _clean_optional_text(value)
        setattr(assumption, field, value)
    db.commit()
    db.refresh(assumption)
    return _get_mrv_or_raise(db, assumption.id)


def delete_mrv_assumption(db: Session, assumption_id: str) -> None:
    assumption = _get_mrv_or_raise(db, assumption_id)
    db.delete(assumption)
    db.commit()


def _mrv_readiness(assumption: PreFeedMrvAssumption | None) -> tuple[float, dict[str, float]]:
    if assumption is None:
        components = {
            "baseline_data": 0.0,
            "captured_accounting": 0.0,
            "methodology": 0.0,
            "verification": 0.0,
            "electricity_source": 0.0,
            "credit_eligibility": 0.0,
            "confidence": 0.0,
        }
        return 0.0, components
    components = {
        "baseline_data": 1.0 if assumption.baseline_emissions_tco2e_per_year is not None else 0.0,
        "captured_accounting": 1.0 if assumption.captured_co2_accounting_tpy is not None else 0.0,
        "methodology": 1.0 if assumption.carbon_credit_methodology else 0.0,
        "verification": MRV_VERIFICATION_SCORE.get(assumption.verification_status, 0.0),
        "electricity_source": 1.0
        if assumption.electricity_source and assumption.electricity_emission_factor_tco2e_per_mwh is not None
        else 0.0,
        "credit_eligibility": ELIGIBILITY_SCORE.get(assumption.carbon_credit_eligibility, 0.0),
        "confidence": _confidence_score(assumption.confidence_level),
    }
    readiness = (
        0.15 * components["baseline_data"]
        + 0.15 * components["captured_accounting"]
        + 0.15 * components["methodology"]
        + 0.20 * components["verification"]
        + 0.15 * components["electricity_source"]
        + 0.10 * components["credit_eligibility"]
        + 0.10 * components["confidence"]
    )
    return round(readiness, 4), {key: round(value, 4) for key, value in components.items()}


def build_mrv_summary(db: Session, package_id: str) -> dict:
    package = get_package_or_raise(db, package_id)
    assumption = _latest_mrv_assumption(db, package_id)
    result = _latest_result(db, package.scenario_id)
    warnings: list[str] = []
    if assumption is None:
        warnings.append("No MRV assumption recorded for this package.")
    if result is None:
        warnings.append("No stored scenario result is available for scenario-derived MRV values.")

    baseline = assumption.baseline_emissions_tco2e_per_year if assumption else None
    captured = assumption.captured_co2_accounting_tpy if assumption else None
    if baseline is None and result:
        baseline = result.total_co2_ton_per_year
    if captured is None and result:
        captured = result.captured_co2_ton_per_year

    methanol = result.methanol_ton_per_year if result else None
    carbon_intensity = assumption.product_carbon_intensity_tco2e_per_ton if assumption else None
    if carbon_intensity is None and baseline is not None and captured is not None and methanol:
        carbon_intensity = max(baseline - captured, 0) / methanol
        warnings.append("Carbon intensity derived from scenario CO2 balance because no MRV product intensity was recorded.")
    abatement = None
    if baseline is not None and carbon_intensity is not None and methanol:
        abatement = max(baseline - (carbon_intensity * methanol), 0)
    elif captured is not None:
        abatement = captured

    readiness, components = _mrv_readiness(assumption)
    return {
        "package_id": package.id,
        "assumption_id": assumption.id if assumption else None,
        "scenario_id": package.scenario_id,
        "carbon_intensity_tco2e_per_ton_methanol": _round(carbon_intensity),
        "abatement_tco2e_per_year": _round(abatement),
        "baseline_emissions_tco2e_per_year": _round(baseline),
        "captured_co2_accounting_tpy": _round(captured),
        "carbon_credit_eligibility": assumption.carbon_credit_eligibility if assumption else None,
        "readiness_score": readiness,
        "readiness_components": components,
        "warnings": warnings,
    }


def generate_mrv_gaps(db: Session, package_id: str) -> list[dict[str, str]]:
    assumption = _latest_mrv_assumption(db, package_id)
    if assumption is None:
        return [
            _gap(
                "prefeed_mrv",
                "MRV assumptions",
                "high",
                "high",
                "MRV",
                "Record baseline, captured accounting, methodology, verification, and eligibility assumptions.",
            )
        ]
    confidence = assumption.confidence_level or "unknown"
    gaps = []
    if assumption.baseline_emissions_tco2e_per_year is None:
        gaps.append(_gap("prefeed_mrv", "Baseline emissions", "high", "high", "MRV", "Record baseline emissions for the selected unit/package.", confidence))
    if assumption.captured_co2_accounting_tpy is None:
        gaps.append(_gap("prefeed_mrv", "Captured CO2 accounting", "high", "high", "MRV", "Record captured CO2 accounting basis for MRV.", confidence))
    if not assumption.carbon_credit_methodology:
        gaps.append(_gap("prefeed_mrv", "Carbon credit methodology", "high", "high", "MRV", "Select the applicable carbon credit methodology or screening basis.", confidence))
    if assumption.verification_status in {"not_started", "method_selected"}:
        gaps.append(_gap("prefeed_mrv", "Verification status", "medium", "medium", "MRV", "Advance MRV verification status with third-party evidence.", confidence))
    if not assumption.electricity_source:
        gaps.append(_gap("prefeed_mrv", "Electricity source", "medium", "medium", "MRV", "Record electricity source for product carbon intensity.", confidence))
    if assumption.electricity_emission_factor_tco2e_per_mwh is None:
        gaps.append(_gap("prefeed_mrv", "Electricity emission factor", "medium", "medium", "MRV", "Record electricity emission factor or source-specific factor.", confidence))
    if assumption.carbon_credit_eligibility in {"unknown", "screening"} or not assumption.eligibility_basis:
        gaps.append(_gap("prefeed_mrv", "Carbon credit eligibility basis", "high", "high", "MRV", "Record eligibility conclusion and supporting basis.", confidence))
    if assumption.supporting_document_id is None:
        gaps.append(_gap("prefeed_mrv", "MRV supporting document", "medium", "medium", "MRV", "Link an MRV document, methodology note, or verification evidence.", confidence))
    if confidence in {"low", "unknown"}:
        gaps.append(_gap("prefeed_mrv", "MRV confidence", "medium", "medium", "MRV", "Review evidence and update MRV confidence level.", confidence))
    return gaps
