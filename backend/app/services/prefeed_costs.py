from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    BusinessScenario,
    Document,
    FinancialAssumption,
    PreFeedCostBasisSelection,
    PreFeedCostItem,
    PreFeedPackage,
    PreFeedVendorProposal,
    ScenarioResult,
)
from app.schemas.pre_feed_cost import (
    COST_COMPONENT_VALUES,
    COST_TYPE_VALUES,
    OPEX_CATEGORY_VALUES,
    RECURRENCE_VALUES,
    SELECTION_TYPE_VALUES,
    PreFeedCostBasisSelectionCreate,
    PreFeedCostItemCreate,
    PreFeedCostItemUpdate,
    PreFeedVendorProposalCreate,
    PreFeedVendorProposalUpdate,
)
from app.services.prefeed import get_package_or_raise


class PreFeedCostInputError(ValueError):
    pass


SCOPE_FIELDS = (
    ("scope_capture_package", "capture_package"),
    ("scope_electrolyzer", "electrolyzer"),
    ("scope_methanol_plant", "methanol_plant"),
    ("scope_storage_port", "storage_port"),
    ("scope_grid_power", "grid_power"),
    ("scope_land", "land"),
    ("scope_mrv", "mrv"),
)

RECURRENCE_MULTIPLIERS = {
    "annual": 1,
    "monthly": 12,
    "quarterly": 4,
    "weekly": 52,
    "daily": 365,
    "one_time": 0,
}

SCENARIO_CAPEX_FIELD_BY_COMPONENT = {
    "capture_package": "capex_capture_usd",
    "electrolyzer": "capex_electrolyzer_usd",
    "methanol_plant": "capex_methanol_plant_usd",
    "storage_port": "capex_storage_port_usd",
}


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _normalize_currency(value: str) -> str:
    return value.strip().upper()


def _validate_cost_type(cost_type: str) -> None:
    if cost_type not in COST_TYPE_VALUES:
        raise PreFeedCostInputError(f"Unsupported cost type: {cost_type}")


def _validate_cost_component(cost_type: str, cost_component: str) -> None:
    allowed = COST_COMPONENT_VALUES if cost_type == "capex" else OPEX_CATEGORY_VALUES
    if cost_component not in allowed:
        raise PreFeedCostInputError(f"Unsupported {cost_type} component: {cost_component}")


def _validate_recurrence(recurrence: str | None) -> None:
    if recurrence is not None and recurrence not in RECURRENCE_VALUES:
        raise PreFeedCostInputError(f"Unsupported recurrence: {recurrence}")


def _validate_selection_type(selection_type: str) -> None:
    if selection_type not in SELECTION_TYPE_VALUES:
        raise PreFeedCostInputError(f"Unsupported selection type: {selection_type}")


def _get_cost_item_or_raise(db: Session, cost_item_id: str) -> PreFeedCostItem:
    item = db.get(PreFeedCostItem, cost_item_id)
    if item is None:
        raise PreFeedCostInputError("Cost item not found")
    return item


def get_vendor_proposal_or_raise(db: Session, proposal_id: str) -> PreFeedVendorProposal:
    proposal = db.scalar(
        select(PreFeedVendorProposal)
        .where(PreFeedVendorProposal.id == proposal_id)
        .options(selectinload(PreFeedVendorProposal.supporting_document))
    )
    if proposal is None:
        raise PreFeedCostInputError("Vendor proposal not found")
    return proposal


def _validate_vendor_belongs_to_package(vendor: PreFeedVendorProposal, package_id: str) -> None:
    if vendor.package_id != package_id:
        raise PreFeedCostInputError("Vendor proposal does not belong to this package")


def _validate_document_matches_package(package: PreFeedPackage, document: Document) -> None:
    if document.plant_id and document.plant_id != package.plant_id:
        raise PreFeedCostInputError("Document belongs to a different plant")
    if document.scenario_id and package.scenario_id and document.scenario_id != package.scenario_id:
        raise PreFeedCostInputError("Document belongs to a different scenario")


def _validate_supporting_document(db: Session, package: PreFeedPackage, document_id: str | None) -> Document | None:
    if document_id is None:
        return None
    document = db.get(Document, document_id)
    if document is None:
        raise PreFeedCostInputError("Supporting document not found")
    _validate_document_matches_package(package, document)
    return document


def list_cost_items(
    db: Session,
    package_id: str,
    vendor_proposal_id: str | None = None,
) -> list[PreFeedCostItem]:
    get_package_or_raise(db, package_id)
    statement = select(PreFeedCostItem).where(PreFeedCostItem.package_id == package_id)
    if vendor_proposal_id:
        proposal = get_vendor_proposal_or_raise(db, vendor_proposal_id)
        _validate_vendor_belongs_to_package(proposal, package_id)
        statement = statement.where(PreFeedCostItem.vendor_proposal_id == vendor_proposal_id)
    statement = statement.order_by(PreFeedCostItem.created_at.desc(), PreFeedCostItem.id.desc())
    return list(db.scalars(statement))


def create_cost_item(db: Session, package_id: str, payload: PreFeedCostItemCreate) -> PreFeedCostItem:
    get_package_or_raise(db, package_id)
    _validate_cost_type(payload.cost_type)
    _validate_cost_component(payload.cost_type, payload.cost_component)
    _validate_recurrence(payload.recurrence)
    if payload.vendor_proposal_id:
        proposal = get_vendor_proposal_or_raise(db, payload.vendor_proposal_id)
        _validate_vendor_belongs_to_package(proposal, package_id)

    item = PreFeedCostItem(
        package_id=package_id,
        vendor_proposal_id=payload.vendor_proposal_id,
        cost_type=payload.cost_type,
        cost_component=payload.cost_component,
        amount=payload.amount,
        currency=_normalize_currency(payload.currency),
        unit_basis=_clean_optional_text(payload.unit_basis),
        recurrence=payload.recurrence,
        contingency_percent=payload.contingency_percent,
        escalation_percent=payload.escalation_percent,
        source_label=_clean_optional_text(payload.source_label),
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_cost_item(db: Session, cost_item_id: str, payload: PreFeedCostItemUpdate) -> PreFeedCostItem:
    item = _get_cost_item_or_raise(db, cost_item_id)
    updates = payload.model_dump(exclude_unset=True)
    next_cost_type = updates.get("cost_type", item.cost_type)
    next_component = updates.get("cost_component", item.cost_component)
    _validate_cost_type(next_cost_type)
    _validate_cost_component(next_cost_type, next_component)
    _validate_recurrence(updates.get("recurrence", item.recurrence))
    if "vendor_proposal_id" in updates and updates["vendor_proposal_id"]:
        proposal = get_vendor_proposal_or_raise(db, updates["vendor_proposal_id"])
        _validate_vendor_belongs_to_package(proposal, item.package_id)

    for field, value in updates.items():
        if field == "currency" and value:
            value = _normalize_currency(value)
        if field in {"unit_basis", "source_label", "notes"} and isinstance(value, str):
            value = _clean_optional_text(value)
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_cost_item(db: Session, cost_item_id: str) -> None:
    item = _get_cost_item_or_raise(db, cost_item_id)
    db.delete(item)
    db.commit()


def _adjusted_capex(item: PreFeedCostItem) -> float:
    contingency = 1 + ((item.contingency_percent or 0) / 100)
    escalation = 1 + ((item.escalation_percent or 0) / 100)
    return item.amount * contingency * escalation


def _annualized_opex(item: PreFeedCostItem) -> float:
    return item.amount * RECURRENCE_MULTIPLIERS.get(item.recurrence or "annual", 1)


def build_cost_summary(
    db: Session,
    package_id: str,
    vendor_proposal_id: str | None = None,
) -> dict:
    items = list_cost_items(db, package_id, vendor_proposal_id=vendor_proposal_id)
    capex_totals: dict[str, float] = {}
    opex_totals: dict[str, float] = {}
    scenario_patch: dict[str, float] = {}
    warnings: list[str] = []

    for item in items:
        currency = item.currency.upper()
        if item.cost_type == "capex":
            adjusted = _adjusted_capex(item)
            capex_totals[currency] = round(capex_totals.get(currency, 0) + adjusted, 2)
            field = SCENARIO_CAPEX_FIELD_BY_COMPONENT.get(item.cost_component)
            if field and currency == "USD":
                scenario_patch[field] = round(scenario_patch.get(field, 0) + adjusted, 2)
        else:
            annualized = _annualized_opex(item)
            opex_totals[currency] = round(opex_totals.get(currency, 0) + annualized, 2)

    if not items:
        warnings.append("No cost items recorded for this scope.")
    currencies = set(capex_totals) | set(opex_totals)
    if len(currencies) > 1:
        warnings.append("Multiple currencies present; Phase 7 does not convert currencies.")

    return {
        "package_id": package_id,
        "vendor_proposal_id": vendor_proposal_id,
        "item_count": len(items),
        "capex_total_by_currency": capex_totals,
        "annual_opex_total_by_currency": opex_totals,
        "scenario_ready_assumptions": scenario_patch,
        "warnings": warnings,
    }


def list_vendor_proposals(db: Session, package_id: str) -> list[PreFeedVendorProposal]:
    get_package_or_raise(db, package_id)
    statement = (
        select(PreFeedVendorProposal)
        .where(PreFeedVendorProposal.package_id == package_id)
        .options(selectinload(PreFeedVendorProposal.supporting_document))
        .order_by(PreFeedVendorProposal.updated_at.desc(), PreFeedVendorProposal.created_at.desc())
    )
    return list(db.scalars(statement))


def create_vendor_proposal(
    db: Session,
    package_id: str,
    payload: PreFeedVendorProposalCreate,
) -> PreFeedVendorProposal:
    package = get_package_or_raise(db, package_id)
    _validate_supporting_document(db, package, payload.supporting_document_id)
    proposal = PreFeedVendorProposal(
        package_id=package.id,
        supporting_document_id=payload.supporting_document_id,
        vendor_name=payload.vendor_name.strip(),
        proposal_name=payload.proposal_name.strip(),
        scope_capture_package=payload.scope_capture_package,
        scope_electrolyzer=payload.scope_electrolyzer,
        scope_methanol_plant=payload.scope_methanol_plant,
        scope_storage_port=payload.scope_storage_port,
        scope_grid_power=payload.scope_grid_power,
        scope_land=payload.scope_land,
        scope_mrv=payload.scope_mrv,
        commercial_basis=_clean_optional_text(payload.commercial_basis),
        delivery_assumptions=_clean_optional_text(payload.delivery_assumptions),
        exclusions=_clean_optional_text(payload.exclusions),
        validity_date=payload.validity_date,
        data_status=payload.data_status,
        confidence_level=payload.confidence_level,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return get_vendor_proposal_or_raise(db, proposal.id)


def update_vendor_proposal(
    db: Session,
    proposal_id: str,
    payload: PreFeedVendorProposalUpdate,
) -> PreFeedVendorProposal:
    proposal = get_vendor_proposal_or_raise(db, proposal_id)
    package = get_package_or_raise(db, proposal.package_id)
    updates = payload.model_dump(exclude_unset=True)
    if "supporting_document_id" in updates:
        _validate_supporting_document(db, package, updates["supporting_document_id"])

    for field, value in updates.items():
        if field in {
            "vendor_name",
            "proposal_name",
            "commercial_basis",
            "delivery_assumptions",
            "exclusions",
            "notes",
        } and isinstance(value, str):
            value = value.strip() if field in {"vendor_name", "proposal_name"} else _clean_optional_text(value)
        setattr(proposal, field, value)

    db.commit()
    db.refresh(proposal)
    return get_vendor_proposal_or_raise(db, proposal.id)


def delete_vendor_proposal(db: Session, proposal_id: str) -> None:
    proposal = get_vendor_proposal_or_raise(db, proposal_id)
    for item in db.scalars(select(PreFeedCostItem).where(PreFeedCostItem.vendor_proposal_id == proposal.id)):
        item.vendor_proposal_id = None
    for selection in db.scalars(
        select(PreFeedCostBasisSelection).where(PreFeedCostBasisSelection.vendor_proposal_id == proposal.id)
    ):
        selection.vendor_proposal_id = None
        selection.is_active = False
    db.delete(proposal)
    db.commit()


def _missing_scopes(proposal: PreFeedVendorProposal) -> list[str]:
    return [label for field, label in SCOPE_FIELDS if not getattr(proposal, field)]


def _scope_score(proposal: PreFeedVendorProposal) -> float:
    covered = len(SCOPE_FIELDS) - len(_missing_scopes(proposal))
    return round(covered / len(SCOPE_FIELDS), 2)


def _vendor_gap(
    proposal_id: str,
    missing_data_name: str,
    impact_level: str,
    priority_level: str,
    recommendation: str,
    confidence_level: str,
) -> dict[str, str]:
    return {
        "proposal_id": proposal_id,
        "source_module": "prefeed_vendor",
        "missing_data_name": missing_data_name,
        "impact_level": impact_level,
        "priority_level": priority_level,
        "recommendation": recommendation,
        "status": "open",
        "confidence_level": confidence_level,
    }


def generate_vendor_gaps(db: Session, proposal_id: str) -> list[dict[str, str]]:
    proposal = get_vendor_proposal_or_raise(db, proposal_id)
    confidence = proposal.confidence_level or "unknown"
    gaps = [
        _vendor_gap(
            proposal.id,
            f"{scope.replace('_', ' ').title()} scope",
            "high",
            "high",
            f"Confirm whether the vendor proposal includes {scope.replace('_', ' ')} scope.",
            confidence,
        )
        for scope in _missing_scopes(proposal)
    ]
    if not proposal.commercial_basis:
        gaps.append(
            _vendor_gap(
                proposal.id,
                "Commercial basis",
                "medium",
                "medium",
                "Record the commercial basis before comparing proposal economics.",
                confidence,
            )
        )
    if proposal.validity_date is None:
        gaps.append(
            _vendor_gap(
                proposal.id,
                "Validity date",
                "medium",
                "medium",
                "Record proposal validity date to support committee timing decisions.",
                confidence,
            )
        )
    if not list_cost_items(db, proposal.package_id, vendor_proposal_id=proposal.id):
        gaps.append(
            _vendor_gap(
                proposal.id,
                "Proposal cost items",
                "high",
                "high",
                "Attach detailed CAPEX/OPEX cost items to this proposal.",
                confidence,
            )
        )
    if confidence in {"low", "unknown"}:
        gaps.append(
            _vendor_gap(
                proposal.id,
                "Proposal confidence level",
                "medium",
                "medium",
                "Review supporting evidence and update confidence when proposal scope and costs are verified.",
                confidence,
            )
        )
    return gaps


def build_vendor_comparison(db: Session, package_id: str) -> list[dict]:
    rows: list[dict] = []
    for proposal in list_vendor_proposals(db, package_id):
        summary = build_cost_summary(db, package_id, vendor_proposal_id=proposal.id)
        gaps = generate_vendor_gaps(db, proposal.id)
        rows.append(
            {
                "proposal_id": proposal.id,
                "vendor_name": proposal.vendor_name,
                "proposal_name": proposal.proposal_name,
                "capex_total_by_currency": summary["capex_total_by_currency"],
                "annual_opex_total_by_currency": summary["annual_opex_total_by_currency"],
                "scope_completeness_score": _scope_score(proposal),
                "missing_scopes": _missing_scopes(proposal),
                "gap_count": len(gaps),
                "confidence_level": proposal.confidence_level,
                "validity_date": proposal.validity_date,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["gap_count"],
            -row["scope_completeness_score"],
            row["capex_total_by_currency"].get("USD", float("inf")),
            row["vendor_name"],
        ),
    )


def _get_scenario_or_raise(db: Session, scenario_id: str) -> BusinessScenario:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise PreFeedCostInputError("Scenario not found")
    return scenario


def get_active_cost_basis(db: Session, scenario_id: str) -> PreFeedCostBasisSelection | None:
    return db.scalar(
        select(PreFeedCostBasisSelection)
        .where(
            PreFeedCostBasisSelection.scenario_id == scenario_id,
            PreFeedCostBasisSelection.is_active.is_(True),
        )
        .order_by(PreFeedCostBasisSelection.created_at.desc(), PreFeedCostBasisSelection.id.desc())
    )


def select_active_cost_basis(
    db: Session,
    scenario_id: str,
    payload: PreFeedCostBasisSelectionCreate,
) -> PreFeedCostBasisSelection:
    scenario = _get_scenario_or_raise(db, scenario_id)
    package = get_package_or_raise(db, payload.package_id)
    if package.scenario_id and package.scenario_id != scenario.id:
        raise PreFeedCostInputError("Package belongs to a different scenario")
    _validate_selection_type(payload.selection_type)
    proposal = None
    if payload.selection_type == "vendor_proposal":
        if not payload.vendor_proposal_id:
            raise PreFeedCostInputError("vendor_proposal_id is required for vendor proposal selection")
        proposal = get_vendor_proposal_or_raise(db, payload.vendor_proposal_id)
        _validate_vendor_belongs_to_package(proposal, package.id)
    elif payload.vendor_proposal_id:
        raise PreFeedCostInputError("vendor_proposal_id is only valid for vendor proposal selections")

    summary = build_cost_summary(db, package.id, vendor_proposal_id=proposal.id if proposal else None)
    for existing in db.scalars(
        select(PreFeedCostBasisSelection).where(
            PreFeedCostBasisSelection.scenario_id == scenario.id,
            PreFeedCostBasisSelection.is_active.is_(True),
        )
    ):
        existing.is_active = False

    selection = PreFeedCostBasisSelection(
        scenario_id=scenario.id,
        package_id=package.id,
        vendor_proposal_id=proposal.id if proposal else None,
        selection_type=payload.selection_type,
        is_active=True,
        snapshot_totals={
            "package_id": package.id,
            "package_name": package.package_name,
            "version_label": package.version_label,
            "vendor_proposal_id": proposal.id if proposal else None,
            "vendor_name": proposal.vendor_name if proposal else None,
            "capex_total_by_currency": summary["capex_total_by_currency"],
            "annual_opex_total_by_currency": summary["annual_opex_total_by_currency"],
            "item_count": summary["item_count"],
            "warnings": summary["warnings"],
        },
        scenario_ready_assumptions=summary["scenario_ready_assumptions"],
        selected_by=_clean_optional_text(payload.selected_by),
        selection_notes=_clean_optional_text(payload.selection_notes),
    )
    db.add(selection)
    db.commit()
    db.refresh(selection)

    # Explicitly read these tables after commit to guard against accidental history mutation in future edits.
    db.scalar(select(FinancialAssumption).where(FinancialAssumption.scenario_id == scenario.id))
    db.scalar(select(ScenarioResult).where(ScenarioResult.scenario_id == scenario.id))
    return selection
