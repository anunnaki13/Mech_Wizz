# Phase 5 UI Spec: LLM & Document Intelligence

## Pages

- `/investor`
- `/documents`

## Investor Insight Panel

Intent: let users generate narrative outputs from backend facts while keeping deterministic KPIs visually separate.

Controls:

- Insight type buttons:
  - Executive Summary
  - Investor Memo
  - Data Gap Explanation
  - Sensitivity Explanation
- Generate action.
- Latest insight list.

Display:

- Generated text in a narrative panel.
- Model name, status, and timestamp.
- Error notice when OpenRouter is not configured.
- Copy should clearly read as generated narrative, not source-of-record numbers.

## Documents Workspace

Intent: upload and manage documents, extract text, and ask simple grounded questions.

Layout:

- Page header: "Document Intelligence".
- Upload panel:
  - file input
  - category select/input
  - optional plant/scenario selectors if available
  - upload button
- Repository table:
  - filename
  - category
  - type
  - upload status
  - extraction status
  - created time
  - actions: select, extract
- Detail panel:
  - selected document metadata
  - extracted text preview
  - Q&A textarea/question input
  - ask button
  - answer panel

## Visual Contract

- Dense operational dashboard.
- No marketing hero.
- Cards use 8px radius.
- Buttons use lucide icons where helpful.
- Warnings use existing amber notice style.
- Generated insight text must wrap safely on mobile/desktop.

## Empty/Failure States

- No documents: show compact empty state inside repository area.
- No extracted text: disable Q&A and show extraction action.
- OpenRouter not configured: show backend error without crashing the page.
