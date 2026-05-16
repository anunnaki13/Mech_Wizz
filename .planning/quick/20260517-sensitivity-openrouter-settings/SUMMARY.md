---
status: complete
completed: 2026-05-17
skill: gsd-quick
---

# Sensitivity And OpenRouter Settings Summary

## Completed

- Replaced the `/sensitivity` placeholder page with a working sensitivity workspace.
- Added ranked-unit selection, variable checkboxes, run sensitivity action, KPI cards, tornado chart, warnings, and result table.
- Added backend OpenRouter settings endpoints:
  - `GET /api/settings/openrouter/provider`
  - `PUT /api/settings/openrouter/provider`
- Stored OpenRouter API keys are masked in read responses and excluded from generic `/api/settings`.
- LLM generation now reads stored OpenRouter settings before falling back to environment variables.
- Added Settings UI for OpenRouter API key, model, base URL, site URL, and app name.

## Validation

- `cd backend && .venv/bin/pytest -q` -> 51 passed.
- `cd frontend && npm run build` -> passed.
- `GET /api/settings/openrouter/provider` -> returns masked status payload.
- `POST /api/sensitivity/run` on the current top ranked WIZ Align case -> 8 results, dominant driver `capex`.
- `/sensitivity` and `/settings` -> 200.
- `gsd-sdk query state.validate` -> valid.
