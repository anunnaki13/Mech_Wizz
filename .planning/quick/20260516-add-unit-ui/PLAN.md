---
type: quick-task-plan
status: complete
created: 2026-05-16
updated: 2026-05-16
---

# Add Unit Creation UI

## Goal

Expose the existing backend `POST /api/plants/` capability in the web app so users can create new unit records from `/units`.

## Plan

- Add typed frontend API support for creating plants.
- Replace the read-only Units page body with a client workspace containing a `New Unit` form.
- Keep the existing unit list and open flow intact.
- Verify frontend build and backend create/delete API behavior.

## Result

Implemented in `frontend/components/units/UnitWorkspace.tsx`, with supporting updates to `frontend/lib/api.ts`, `frontend/types/plant.ts`, `frontend/app/units/page.tsx`, `frontend/components/units/UnitList.tsx`, and `frontend/app/globals.css`.
