# Phase 5 AI Spec: LLM & Document Intelligence

## AI System Type

Single-model narrative generation and lightweight document Q&A.

## Framework Selection

Selected: direct OpenRouter Chat Completions HTTP integration.

Why:

- The phase needs controlled one-shot generations, not autonomous agents.
- Backend already has deterministic context and retrieval is simple extracted text for MVP.
- Direct integration keeps prompt, response, model, and error persistence auditable.

Not selected:

- LlamaIndex: deferred until vector retrieval or advanced RAG is required.
- LangChain/LangGraph: unnecessary orchestration overhead for Phase 5.

## Provider Contract

OpenRouter official docs identify:

- Endpoint: `POST https://openrouter.ai/api/v1/chat/completions`
- Auth: `Authorization: Bearer <OPENROUTER_API_KEY>`
- Request: chat `messages`, optional `model`, `temperature`, token limit, and metadata.
- Response: `choices`, `model`, and `usage`.
- Errors: JSON `error.code` and `error.message`, including auth, credits, moderation/guardrail, rate limit, and provider availability failures.

## Core Prompt Rules

Every prompt must include:

- Use only supplied context.
- Do not invent numbers.
- Do not recalculate IRR, NPV, LCOM, payback, scoring, sensitivity, CO2, H2, or methanol outputs.
- Separate actual data, assumptions, confidence, and data gaps.
- Write concise professional Indonesian unless the user explicitly asks otherwise.

## Insight Workflows

| Insight Type | Input Context | Output |
|--------------|---------------|--------|
| `executive_summary` | investor case, scenario result, data quality | concise management/investor summary |
| `data_gap_explanation` | plant, scenario, data gaps, recommendations | prioritized explanation of gaps and next actions |
| `investor_memo` | investor case aggregate | structured memo with thesis, economics, risk, confidence, next actions |
| `sensitivity_explanation` | latest sensitivity run and scenario context | 3-5 business insights from sensitivity results |
| `document_qa` | extracted document text plus question | answer grounded only in document context |

## Critical Failure Modes

- Hallucinated numbers or calculations.
- Missing separation between actual data, assumptions, confidence, and gaps.
- Treating generated text as deterministic source of record.
- Answering document questions without extracted text.
- Leaking API keys to frontend or persisted prompts.
- Silent generation failure without an auditable error record.

## Guardrails

- Backend prompt builder injects fixed calculation-authority rules.
- Frontend never sends raw API keys.
- Missing API key returns unavailable error.
- Document Q&A requires extracted text.
- Prompt context is truncated with a visible note when needed.
- Persist prompt and response/error for every attempted generation.

## Evaluation Strategy

Code-based evals in tests:

- Prompt builder contains required guardrail strings.
- Generated insight persists prompt, response, model, status, and scenario/document references.
- Missing API key fails cleanly.
- Document Q&A without extracted text is rejected.
- Document extraction updates `extraction_status`.

Manual review before production:

- Check generated Indonesian tone for professional PLN NP/investor audience.
- Review 10-20 examples covering complete case, missing CAPEX, missing H2, sensitivity-dominant case, and document Q&A.

## Reference Dataset Seed

Initial eval examples:

- Tenayan base case with incomplete CAPEX.
- Data gap explanation for missing H2 strategy and CAPEX.
- Sensitivity explanation with missing CAPEX warnings.
- Investor memo using current Phase 4 aggregate.
- Uploaded text document asking a grounded question.
