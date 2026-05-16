# Phase 5 Context: LLM & Document Intelligence

## Phase Goal

Add OpenRouter-backed narrative insight and lightweight document intelligence while preserving deterministic backend calculations as the source of truth.

## Boundary

In scope:

- OpenRouter chat-completion service with explicit guardrails.
- Prompt templates for executive summary, data gap explanation, investor memo, and sensitivity explanation.
- Persisted `LlmInsight` records containing scenario reference, insight type, prompt, response, model name, status, and errors.
- UI workflow to generate/read LLM insights from investor/document workflows.
- Document upload, repository, text extraction for PDF/Excel/text-like files, and basic document Q&A using extracted text.

Out of scope:

- LLM-generated technical or financial calculations.
- Vector database, embeddings, semantic retrieval, or production RAG infrastructure.
- Streaming response UI.
- Multi-agent orchestration.
- Full document parsing worker and asynchronous queue. MVP extraction may run synchronously.
- Internet/web-search augmented LLM answers.

<decisions>
## Implementation Decisions

### AI Provider & Framework

- **D-01:** Use OpenRouter as the provider for Phase 5 LLM calls.
- **D-02:** Use direct HTTP calls to OpenRouter Chat Completions instead of LangChain/LlamaIndex/LangGraph for MVP because workflows are simple single-call generations.
- **D-03:** Store `OPENROUTER_API_KEY` and model configuration in backend environment settings only; never expose keys to the frontend.
- **D-04:** Use non-streaming chat completions for MVP to keep persistence and tests simple.
- **D-05:** If no API key is configured, the API returns a deterministic clear error and does not create fake LLM responses.

### Calculation Authority & Guardrails

- **D-06:** LLM output is narrative only; deterministic backend outputs remain the numeric source of record.
- **D-07:** Prompts must include explicit instructions not to invent numbers or override calculations.
- **D-08:** Prompts must separate actual data, assumptions, confidence labels, and data gaps.
- **D-09:** Prompt context is built from existing backend aggregate/read models: investor case, data quality summary, sensitivity results, scenario result, and document extracted text.
- **D-10:** Store the exact prompt and response for auditability.

### Insight Types

- **D-11:** Supported Phase 5 insight types are `executive_summary`, `data_gap_explanation`, `investor_memo`, `sensitivity_explanation`, and `document_qa`.
- **D-12:** LLM insight APIs persist model name, prompt, response, scenario ID where applicable, document ID where applicable, status, and error message.
- **D-13:** Existing insights should be listable by scenario/document/type without regenerating.

### Document Intelligence

- **D-14:** `documents` stores plant/scenario references, filename, file type, storage path, category, upload status, extraction status, extracted text, and timestamps.
- **D-15:** Upload API stores files under configured `UPLOAD_DIR`; file paths must be sanitized to avoid directory traversal.
- **D-16:** MVP extraction supports PDF, XLSX/XLS/CSV, TXT, MD, and JSON with graceful warnings for unsupported formats.
- **D-17:** Basic document Q&A uses extracted text as bounded context and must tell the model to answer only from document/context data.
- **D-18:** Document Q&A records are persisted as `document_qa` insights.

### UI

- **D-19:** `/investor` can include an insight panel for executive summary, investor memo, data gap explanation, and sensitivity explanation.
- **D-20:** `/documents` becomes the document repository and Q&A workspace.
- **D-21:** UI must make generated narrative visibly separate from deterministic KPIs and data records.

### Completion

- **D-22:** Phase 5 completion requires backend tests, frontend build, Docker Compose config, Alembic temp upgrade, LLM/document marker searches, smoke checks for `/documents` and LLM endpoints, plus final GSD verification/review artifacts.
</decisions>

## Acceptance Notes

- It is acceptable for OpenRouter generation tests to mock the HTTP client; tests must not require a live API key.
- Without `OPENROUTER_API_KEY`, generation endpoints should return a 503-style unavailable response and explain configuration is missing.
- Document Q&A can be lightweight context injection from extracted text; vector retrieval is a later enhancement.
