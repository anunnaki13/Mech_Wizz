# Phase 9 UI-SPEC: Risk & Pre-FEED Decision Dashboard

## Surface

Extend `/prefeed`. Do not add a new top-level route.

## Layout Contract

- Place a compact decision dashboard section after the selected package summary and before deeper cost/offtake/MRV editors.
- Use a dense operational layout: KPI cards, two-column panels on desktop, single-column on mobile, tables/lists for repeated risk/gate rows.
- Keep cards at or below the existing project radius. Avoid decorative hero or marketing layout.
- Use existing status chips, warning notices, and table styles where possible.

## Required Panels

- **Decision Overview:** package status, package confidence, risk readiness, gate readiness, blocker count, next-action count.
- **Economics Snapshot:** CAPEX/OPEX totals, active cost basis, vendor count, offtake revenue, MRV readiness. Values come from backend aggregate.
- **Blockers:** backend-generated blocker list with source, priority, owner, and recommendation.
- **Next Actions:** backend-generated next actions with owner, priority, recommendation, and status.
- **Risk Register:** create/edit/delete risks; table shows category, statement, likelihood, impact, backend severity, status, owner, due date.
- **Decision Gates:** create/edit/delete gates; table shows category, title, critical flag, backend status, owner, due date, evidence.
- **Committee Brief:** button to generate brief and response/status panel using existing LLM insight response shape.

## Interaction Rules

- Disable Phase 9 create/edit actions until a package is selected.
- Use backend errors verbatim through existing `apiFetch` behavior.
- Refresh dashboard after any risk, gate, or brief action.
- Frontend must not calculate severity score, readiness score, blockers, next actions, cost totals, revenue, carbon intensity, or MRV/offtake readiness.

## Copy

Keep labels operational:

- "Decision Dashboard"
- "Blockers"
- "Next Actions"
- "Risk Register"
- "Decision Gates"
- "Generate Committee Brief"

No visible explanatory tutorial text.
