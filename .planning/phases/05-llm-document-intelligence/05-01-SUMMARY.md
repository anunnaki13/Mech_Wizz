---
phase: 05-llm-document-intelligence
plan: "01"
subsystem: llm-backend
tags: [fastapi, openrouter, prompts, persistence, guardrails]
requires:
  - phase: 04-investor-case-data-quality
    provides: Investor aggregate, data quality summary, sensitivity outputs, and persisted gaps
provides:
  - OpenRouter service wrapper
  - Guardrailed prompt builders
  - LLM insight persistence
  - LLM generation/listing APIs
affects: [phase-5-investor-insight-ui, phase-5-document-qa]
tech-stack:
  added: []
  patterns: [direct OpenRouter HTTP integration, prompt audit persistence, missing-key failure records]
key-files:
  created:
    - backend/alembic/versions/0007_phase5_llm_documents.py
    - backend/app/models/document.py
    - backend/app/models/llm_insight.py
    - backend/app/schemas/llm.py
    - backend/app/services/llm.py
    - backend/app/routers/llm.py
    - backend/tests/test_llm.py
  modified:
    - backend/app/config.py
    - backend/app/main.py
    - backend/app/models/__init__.py
    - .env.example
key-decisions:
  - "Phase 5 uses direct OpenRouter Chat Completions HTTP calls rather than a heavier AI framework."
  - "Prompt builders include fixed calculation-authority guardrails and persist exact prompt/response text."
  - "Generation endpoints persist failed insight records when OpenRouter is not configured."
  - "Document table was introduced with the same migration to support nullable `document_id` insight references."
patterns-established:
  - "LLM calls are injectable/mocked in tests via a transport protocol."
  - "LLM insights are listable without regeneration."
requirements-completed: [DATA-07, LLM-01, LLM-02, LLM-03, LLM-04, LLM-05, LLM-06, LLM-07, SENS-04]
duration: 5min
completed: 2026-05-16
---

# Phase 5 Plan 01: OpenRouter Backend Summary

**Implemented backend LLM insight generation foundation with OpenRouter guardrails and persistence.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-05-16T13:26:28+07:00
- **Completed:** 2026-05-16T13:31:34+07:00
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Added `LlmInsight` persistence with scenario/plant/document references, prompt, response, model, status, error, provider ID, and usage.
- Added base `Document` model/table so document Q&A insights can reference uploaded documents in later plans.
- Added OpenRouter configuration fields and `.env.example` placeholders.
- Added prompt builders for executive summary, data gap explanation, investor memo, sensitivity explanation, and document Q&A.
- Added OpenRouter client wrapper using backend-only API key, fixed prompt guardrails, and mockable transport.
- Added LLM endpoints:
  - `GET /api/llm/insights`
  - `POST /api/llm/summary/{scenario_id}`
  - `POST /api/llm/data-gap/{plant_id}`
  - `POST /api/llm/investor-memo/{scenario_id}`
  - `POST /api/llm/explain-sensitivity/{scenario_id}`
- Added tests for prompt guardrails, mocked generation success, and missing-key failure persistence.

## Verification

- `cd backend && pytest -q tests/test_llm.py` - passed, 3 tests.
- `cd backend && pytest -q` - passed, 34 tests.
- `DATABASE_URL=sqlite:////tmp/mechwiz_phase5_0501.db .venv/bin/alembic upgrade head` - passed through migration 0007.
- `rg -n "LlmInsight|OpenRouter|Do not invent numbers|document_qa" backend` - expected matches found.

## Notes

- Live OpenRouter generation requires `OPENROUTER_API_KEY`; without it the API returns a clear 503 and persists a failed insight record.
- The document upload/extraction endpoints are still Phase 5 plan 03.

---
*Phase: 05-llm-document-intelligence*
*Completed: 2026-05-16*
