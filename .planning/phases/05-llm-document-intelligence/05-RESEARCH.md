# Phase 5 Research: LLM & Document Intelligence

## Codebase Findings

- Backend already has deterministic read models for the context Phase 5 needs:
  - `build_investor_case`
  - data quality summary
  - scenario results
  - sensitivity results
  - persisted data gaps and settings
- Backend currently has no `documents` or `llm_insights` model.
- Frontend `/documents` is a placeholder.
- Frontend `/investor` is functional and can host a small insight panel.
- Existing frontend pattern is typed API helpers in `frontend/lib/api.ts` plus focused client components.

## OpenRouter Findings

- Official endpoint is `POST https://openrouter.ai/api/v1/chat/completions`.
- Requests use chat `messages`, `model`, `temperature`, and token limit parameters.
- Authentication uses `Authorization: Bearer <token>`.
- Responses return `choices`, selected `model`, and `usage`.
- Errors return JSON with `error.code` and `error.message`; common statuses include 401, 402, 403, 408, 429, 502, and 503.

## AI Framework Decision

Use direct HTTP integration.

Rationale:

- Phase 5 generation is four simple single-call narrative workflows plus document Q&A.
- Existing backend already provides the relevant context; no orchestration framework is needed.
- Avoids dependency weight and abstraction drift.

Rejected for MVP:

- LlamaIndex: useful for production RAG, but vector retrieval and advanced ingestion are out of scope.
- LangChain/LangGraph: useful for evolving chains/stateful workflows, but too heavy for current single-call generation.

## Backend Approach

Add:

- `Document` model and migration.
- `LlmInsight` model and migration.
- `llm.py` service:
  - prompt builders by insight type
  - OpenRouter client wrapper
  - persistence of prompt/response/status/error
  - missing-key failure path
- `documents.py` service:
  - safe upload path generation
  - text extraction for PDF, Excel/CSV, TXT/MD/JSON
  - basic document Q&A prompt context
- Routers:
  - `/api/llm/summary/{scenario_id}`
  - `/api/llm/data-gap/{plant_id}`
  - `/api/llm/investor-memo/{scenario_id}`
  - `/api/llm/explain-sensitivity/{scenario_id}`
  - `/api/llm/insights`
  - `/api/documents/upload`
  - `/api/documents`
  - `/api/documents/{id}`
  - `/api/documents/{id}/extract`
  - `/api/documents/{id}/ask`

## Frontend Approach

- Add `frontend/types/llm.ts` and `frontend/types/document.ts`.
- Add API helpers for insight generation/listing and document workflows.
- Add `InvestorInsightsPanel` into `/investor`.
- Replace `/documents` placeholder with document repository/upload/extract/Q&A workspace.

## Eval & Verification Approach

Code-based checks:

- Prompt contains guardrail phrases.
- Prompt includes actual data/assumptions/confidence/gaps sections.
- Insight records persist prompt and response.
- Missing API key returns a clear failure.
- Document upload rejects unsafe names and unsupported extraction is graceful.
- Document Q&A requires extracted text.

Manual smoke:

- API list endpoints.
- `/documents` loads.
- LLM generation endpoint fails cleanly without key or succeeds with configured key.

## Risks

- OpenRouter live calls cannot be reliably tested in CI without credentials. Mitigation: dependency-injected/mockable client and tests for both success and missing-key paths.
- Large PDFs can exceed prompt limits. Mitigation: truncate document context in MVP and record warning.
- Extraction quality varies by PDF. Mitigation: expose extracted text status and leave full OCR/document pipeline for later.
