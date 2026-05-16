---
type: quick-task-summary
status: complete
created: 2026-05-16
updated: 2026-05-16
---

# Summary

Added a production UI path for creating units from `/units`.

## Changed

- Added `createPlant` API helper and `PlantPayload` type.
- Added `UnitWorkspace` client component with `New Unit` form, validation, save state, and redirect to the new unit profile.
- Updated the Units page to render the workspace.
- Updated unit empty-state copy and form styling.
- Updated README to mention adding/reviewing units from `/units`.

## Verification

- `npm run build` passed.
- Direct backend create/delete verification passed with `POST /api/plants/` followed by `DELETE /api/plants/{id}`.
