---
status: resolved
trigger: "Save does not work, app feels heavy opening modules, and there is an N menu/logo at the bottom-left."
created: 2026-05-16
updated: 2026-05-16
---

# Debug Session: save-cors-dev-indicator

## Symptoms

- Expected behavior: save actions persist records from the browser UI.
- Actual behavior: user reports save does not work.
- Error messages: user reports errors but no browser console text yet.
- Timeline: observed after current GitHub deployment/push.
- Reproduction: open app modules from the browser and attempt to save.

## Current Focus

- hypothesis: Browser requests are blocked because the frontend uses a localhost API base URL and the backend CORS policy only allows localhost, while the user opens the app through a server/IP origin.
- test: Reproduce CORS preflight from a non-localhost origin and inspect frontend runtime mode.
- expecting: Non-localhost origin is rejected, and frontend is running via Next.js dev server.
- next_action: Monitor browser-side save from the public URL; server-side verification now passes.

## Evidence

- 2026-05-16: `OPTIONS /api/prefeed/packages` with `Origin: http://103.150.197.225:3000` returned `400 Disallowed CORS origin`.
- 2026-05-16: `frontend/lib/api.ts` hardcoded default API base to `http://localhost:8000/api`.
- 2026-05-16: `backend/app/main.py` only allowed CORS origin `http://localhost:3000`.
- 2026-05-16: Process list showed `next dev --hostname 0.0.0.0 --port 3000`; frontend log showed slow first route compiles and Next dev cross-origin warning.
- 2026-05-16: First CORS patch briefly shadowed the `settings` router with a local `settings` variable in `main.py`; fixed by renaming it to `app_settings`.
- 2026-05-16: Backend test suite passed with `47 passed`.
- 2026-05-16: `npm run build` passed after moving MapLibre JS to a client-only dynamic import; `/dashboard/map` first-load bundle dropped from roughly 388 kB to 115 kB.
- 2026-05-16: Production frontend server returned HTTP 200 for `/prefeed`, `/dashboard`, `/dashboard/map`, `/scenarios`, and `/units`.
- 2026-05-16: CORS POST from `Origin: http://103.150.197.225:3000` returned `201 Created` and `access-control-allow-origin: *`; verification package was archived.

## Eliminated

- hypothesis: Backend package list endpoint is down.
  reason: `GET /api/prefeed/packages` returned successfully.

## Resolution

- root_cause: Frontend API calls were built for `localhost` and backend CORS only allowed `localhost:3000`, so browser saves from the public server/IP origin were blocked. The app was also running through `next dev`, causing the visible Next dev indicator and route-by-route compilation latency. Production serving exposed a MapLibre chunk issue because the map dependency was pulled into server startup.
- fix: Added runtime API base URL fallback for non-localhost browser hosts, made CORS configurable with non-credential wildcard default for demo use, moved MapLibre JS to a client-only dynamic import, rebuilt frontend, and restarted backend/frontend as non-dev servers.
- verification: CORS preflight passed, CORS POST save passed, temporary save records were archived, `pytest -q` passed with 47 tests, `npm run build` passed, and production routes returned HTTP 200.
- files_changed: `.env.example`, `README.md`, `backend/app/config.py`, `backend/app/main.py`, `frontend/lib/api.ts`, `frontend/components/dashboard/OpportunityMap.tsx`
