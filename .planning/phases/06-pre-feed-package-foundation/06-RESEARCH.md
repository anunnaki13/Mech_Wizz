---
phase: 06-pre-feed-package-foundation
status: complete
researched_at: 2026-05-16T14:38:00+07:00
---

# Phase 6 Research: Pre-FEED Package Foundation

## Objective

Plan the Pre-FEED package foundation so it fits the existing FastAPI/SQLAlchemy/Next.js codebase without rewriting v1.0 plant, scenario, document, data gap, or simulation history models.

## Existing Architecture To Reuse

- `Plant` remains the site/unit parent identity.
- `BusinessScenario` remains the scenario parent for simulation assumptions and results.
- `Document` already stores upload metadata, storage path, category, upload status, extraction status, extracted text, and extraction errors.
- `DataGap` and data quality services already define useful gap language: source module, missing data name, impact, priority, recommendation, status.
- Frontend workspace patterns already exist in `/documents`, `/settings`, `/scenarios`, and `/investor`.

## Recommended Data Model

Add two tables:

1. `pre_feed_packages`
   - `id`
   - `plant_id`
   - `scenario_id` nullable
   - `package_name`
   - `package_status`
   - `owner_name`
   - `source_organization`
   - `received_date`
   - `version_label`
   - `data_status`
   - `confidence_level`
   - `notes`
   - timestamps

2. `pre_feed_package_documents`
   - `id`
   - `package_id`
   - `document_id`
   - `document_role`
   - `notes`
   - timestamps

Use soft archival through `package_status = "archived"` rather than hard deletion. Keep relationship-level document role on the join table so one uploaded document can be reused in different package contexts.

## Recommended API Surface

Use a dedicated Pre-FEED router:

- `GET /api/prefeed/packages`
- `POST /api/prefeed/packages`
- `GET /api/prefeed/packages/{package_id}`
- `PUT /api/prefeed/packages/{package_id}`
- `POST /api/prefeed/packages/{package_id}/archive`
- `GET /api/prefeed/packages/{package_id}/documents`
- `POST /api/prefeed/packages/{package_id}/documents`
- `DELETE /api/prefeed/packages/{package_id}/documents/{link_id}`
- `GET /api/prefeed/packages/{package_id}/gaps`

Filters should support `plant_id`, `scenario_id`, and `include_archived`.

## Gap Strategy

Compute Phase 6 package gaps deterministically on read. Do not persist package gaps in Phase 6 unless implementation discovers that reusing `DataGap` is simpler and safe.

Recommended checks:

- Missing owner
- Missing source organization
- Missing received date
- Missing version label
- No vendor proposal linked
- No EPC estimate linked
- Low or unknown package confidence

Return a simple package gap schema that matches current data quality vocabulary so later phases can aggregate it.

## UI Strategy

Add `/prefeed` with `PreFeedWorkspace`:

- Control band: plant selector, scenario selector, package selector, `New Package`.
- Main panel: package metadata editor and save/archive actions.
- Linked documents panel: select existing document, assign role, link/unlink.
- Side panel: package warnings and selected package detail.

Keep CSS consistent with existing `document-workspace`, `settings-workspace`, `investor-controls`, `data-table`, `chip`, `notice`, and `.card` patterns.

## Verification Strategy

- Backend targeted tests for create/update/archive/list/read/link/unlink/gap behavior.
- Full backend test suite after router/model registration.
- Frontend production build after adding route/component/types/API helpers.
- Fresh Alembic SQLite upgrade through new migration.
- Marker search for `PreFeedPackage`, `pre_feed_packages`, `PreFeedWorkspace`, and `/api/prefeed`.

## Risks

- Avoid overreaching into Phase 7 cost line item modelling.
- Avoid mutating `FinancialAssumption` or `ScenarioResult` in Phase 6.
- Avoid duplicating document upload/extraction logic.
- Ensure archived packages remain audit-visible where requested.
