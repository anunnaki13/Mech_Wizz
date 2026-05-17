---
status: complete
created: 2026-05-17
completed: 2026-05-17
slug: pltu-screening-pdf-report
---

# PLTU Screening PDF Report

Generate a PDF report explaining the value and outputs of the 26-site curated PLTU dataset.

## Scope

- Pull current runtime metrics from the backend database.
- Correct the curated importer electrolyzer CAPEX unit basis before reporting economics.
- Generate a PDF report with summary KPIs, ranking, method, data confidence, economic caveats, and next phase.
- Add a reproducible report generator script.
- Run importer, tests, API smoke checks, commit, and push to GitHub main.

## Verification

- Full backend tests pass.
- Runtime DB has 26 plant/map records.
- Generated PDF exists and is non-empty.
