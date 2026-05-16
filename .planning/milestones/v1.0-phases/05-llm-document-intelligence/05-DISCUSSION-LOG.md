# Phase 5 Discussion Log: LLM & Document Intelligence

## Inputs Used

- User instruction: continue the GSD project after Phase 4.
- Roadmap Phase 5: LLM & Document Intelligence.
- Project blueprint sections for OpenRouter, LLM prompt templates, `documents`, and `llm_insights`.
- Phase 4 outputs: investor aggregate, persisted data gaps, data quality summary, settings, and sensitivity outputs.
- Official OpenRouter documentation checked on 2026-05-16:
  - Chat Completions endpoint: `POST https://openrouter.ai/api/v1/chat/completions`
  - Authentication: Bearer token in `Authorization` header.
  - Error shape and relevant status codes.

## Resolved Questions

- Framework: direct HTTP OpenRouter integration is sufficient for MVP; no LangChain/LlamaIndex dependency in Phase 5.
- Retrieval: document Q&A uses extracted document text as context; no pgvector/Qdrant in v1.
- UI: use existing AppShell and dashboard CSS; `/documents` replaces placeholder and `/investor` gets a compact insight panel.
- Guardrails: prompts explicitly forbid invented numbers and separate actual data, assumptions, confidence, and gaps.

## Open Items

- Production model selection can be changed through environment settings; MVP defaults to a single configured model.
- Longer documents may need chunking/vector retrieval later.
