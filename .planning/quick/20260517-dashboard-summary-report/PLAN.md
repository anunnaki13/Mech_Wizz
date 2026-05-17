---
status: complete
created: 2026-05-17
completed: 2026-05-17
slug: dashboard-summary-report
---

# Dashboard Summary Report

Replace the unclear empty dashboard with a polished executive summary based on the current 26-site PLTU screening dataset.

## Scope

- Load live plant and ranking data from the backend, including simulation aggregates exposed through the ranking response.
- Present executive KPIs for top candidate, total PLTU capacity, CO2 potential, captured CO2, e-methanol, H2 demand, electrolyzer scale, gross revenue, and average LCOM.
- Explain what the application calculates and what the output means.
- Show the Top 10 candidate ranking with confidence labels.
- Surface data-confidence caveats, current value delivered, and recommended next phase.
- Keep the dashboard linked to the existing map and investor case modules.
- Avoid many per-row scenario-result requests so the dashboard remains lightweight.

## Verification

- Frontend production build passes.
- `/dashboard` renders the new summary content from live backend data.
- GSD state validation passes.
