# Phase 5 Patterns: LLM & Document Intelligence

## Backend Patterns

- Keep ORM models in `backend/app/models/`.
- Add schemas under `backend/app/schemas/`.
- Add routers under `backend/app/routers/` and include in `backend/app/main.py`.
- Keep provider/network logic in `backend/app/services/`.
- Make OpenRouter calls injectable/mocked in tests.
- Persist prompt and response exactly as sent/received.
- Return null-safe records and explicit errors; never fabricate model output.

## Frontend Patterns

- Add frontend types under `frontend/types/`.
- Extend `frontend/lib/api.ts` with typed helpers.
- Use AppShell, compact panels, existing card/table/notice styles.
- Generated insights must be displayed as narrative output, not source-of-record calculations.
- Upload/extract/Q&A controls should stay in `/documents`; investor insight actions stay in `/investor`.

## Expected New Files

Backend:

- `backend/alembic/versions/0007_phase5_llm_documents.py`
- `backend/app/models/document.py`
- `backend/app/models/llm_insight.py`
- `backend/app/schemas/document.py`
- `backend/app/schemas/llm.py`
- `backend/app/services/llm.py`
- `backend/app/services/documents.py`
- `backend/app/routers/llm.py`
- `backend/app/routers/documents.py`
- `backend/tests/test_llm.py`
- `backend/tests/test_documents.py`

Frontend:

- `frontend/types/llm.ts`
- `frontend/types/document.ts`
- `frontend/components/investor/InvestorInsightsPanel.tsx`
- `frontend/components/documents/DocumentWorkspace.tsx`

## API Contract Conventions

- Use `scenario_id`, `plant_id`, and `document_id` consistently.
- Insight responses include `status`, `error_message`, and `response_text`.
- Document extraction should be idempotent: running extract again updates the same document record.
- Q&A should store the question in the prompt and generated answer in `LlmInsight`.
