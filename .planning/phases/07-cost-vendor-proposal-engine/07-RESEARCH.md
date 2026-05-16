---
phase: 07-cost-vendor-proposal-engine
status: complete
researched_at: 2026-05-16T15:08:00+07:00
---

# Phase 7 Research: Cost & Vendor Proposal Engine

## Objective

Add detailed Pre-FEED cost and vendor proposal functionality while preserving Phase 6 package/document audit behavior and v1.0 simulation history.

## Existing Architecture To Reuse

- `PreFeedPackage` is the parent for package-scoped cost and proposal records.
- `Document` remains the owner for uploaded files and extracted text.
- `BusinessScenario` is the scenario parent for active cost-basis selection.
- `FinancialAssumption` exposes existing CAPEX fields that can be referenced by a scenario-ready patch, but Phase 7 should not update it automatically.
- Existing deterministic service patterns live in `prefeed.py`, `data_quality.py`, and scenario/scoring services.

## Recommended Data Model

Add three tables in a Phase 7 migration:

1. `pre_feed_cost_items`
   - `id`
   - `package_id`
   - `vendor_proposal_id` nullable
   - `cost_type`
   - `cost_component`
   - `amount`
   - `currency`
   - `unit_basis`
   - `recurrence`
   - `contingency_percent`
   - `escalation_percent`
   - `source_label`
   - `data_status`
   - `confidence_level`
   - `notes`
   - timestamps

2. `pre_feed_vendor_proposals`
   - `id`
   - `package_id`
   - `supporting_document_id` nullable
   - `vendor_name`
   - `proposal_name`
   - required scope coverage booleans
   - `commercial_basis`
   - `delivery_assumptions`
   - `exclusions`
   - `validity_date`
   - `data_status`
   - `confidence_level`
   - `notes`
   - timestamps

3. `pre_feed_cost_basis_selections`
   - `id`
   - `scenario_id`
   - `package_id`
   - `vendor_proposal_id` nullable
   - `selection_type`
   - `is_active`
   - snapshot totals JSON
   - scenario-ready patch JSON
   - `selected_by`
   - `selection_notes`
   - timestamps

## Recommended API Surface

- `GET /api/prefeed/packages/{package_id}/cost-items`
- `POST /api/prefeed/packages/{package_id}/cost-items`
- `PUT /api/prefeed/cost-items/{cost_item_id}`
- `DELETE /api/prefeed/cost-items/{cost_item_id}`
- `GET /api/prefeed/packages/{package_id}/cost-summary`
- `GET /api/prefeed/packages/{package_id}/vendor-proposals`
- `POST /api/prefeed/packages/{package_id}/vendor-proposals`
- `PUT /api/prefeed/vendor-proposals/{proposal_id}`
- `DELETE /api/prefeed/vendor-proposals/{proposal_id}`
- `GET /api/prefeed/packages/{package_id}/vendor-comparison`
- `GET /api/prefeed/vendor-proposals/{proposal_id}/gaps`
- `POST /api/prefeed/scenarios/{scenario_id}/active-cost-basis`
- `GET /api/prefeed/scenarios/{scenario_id}/active-cost-basis`

## Aggregation Strategy

- Apply CAPEX contingency and escalation to item amount when computing adjusted CAPEX.
- Annualize OPEX by recurrence (`annual` = 1, `monthly` = 12, `quarterly` = 4, `weekly` = 52, `daily` = 365, `one_time` = 0 for annual OPEX).
- Return totals by currency.
- Return USD scenario-ready patch only for mapped CAPEX components:
  - `capture_package` -> `capex_capture_usd`
  - `electrolyzer` -> `capex_electrolyzer_usd`
  - `methanol_plant` -> `capex_methanol_plant_usd`
  - `storage_port` -> `capex_storage_port_usd`

## UI Strategy

Add a `CostVendorWorkspace` child component under `/prefeed` and pass the selected package/scenario context from `PreFeedWorkspace`. This keeps Phase 6 package metadata controls separate from Phase 7 cost/vendor controls.

## Verification Strategy

- Targeted backend tests for cost CRUD, aggregation, proposal CRUD, comparison/gaps, active selection, and history preservation.
- Full backend test suite.
- Frontend build.
- Fresh Alembic SQLite upgrade.
- Marker search for `PreFeedCostItem`, `VendorProposal`, `CostVendorWorkspace`, and active cost basis endpoints.

## Risks

- Avoid automatically mutating `FinancialAssumption`.
- Avoid mixing currency conversion into Phase 7.
- Avoid duplicating document upload/linking.
- Keep `/prefeed` component complexity controlled by splitting cost/vendor UI.
