---
status: in_progress
created: 2026-05-17
skill: gsd-quick
---

# Sensitivity And OpenRouter Settings Fix

## Goal

Make the Sensitivity page functional and add OpenRouter API key management to Settings.

## Scope

- Replace the placeholder `/sensitivity` page with a working sensitivity workspace.
- Let users choose a ranked unit/scenario, run sensitivity, and inspect tornado/table outputs.
- Add backend endpoints to read/update OpenRouter provider settings without exposing the stored API key.
- Make LLM generation use the stored OpenRouter settings when present, falling back to environment variables.
- Add frontend Settings UI for OpenRouter key/model/base URL.

## Validation

- Backend tests pass.
- Frontend production build passes.
- Local API checks confirm sensitivity and OpenRouter settings endpoints.
- GSD state validation passes.
