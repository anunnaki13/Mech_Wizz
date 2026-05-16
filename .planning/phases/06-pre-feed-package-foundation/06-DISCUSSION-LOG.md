# Phase 6: Pre-FEED Package Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-16T14:36:00+07:00
**Phase:** 6-Pre-FEED Package Foundation
**Areas discussed:** milestone target, package identity, document linking, audit/history, gaps/confidence, UI behavior

---

## Milestone Target

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-FEED Digital Twin | Promote the deferred v2 scope: detailed CAPEX/OPEX, vendor comparison, offtake readiness, MRV, and risk register. | ✓ |
| Operational Digital Twin | Move directly to DCS/SCADA, historian data, real-time optimization, and predictive maintenance. | |
| Production Hardening | Focus on VPS/Nginx/backup/observability and deployment hardening. | |

**User's choice:** User approved continuing after being offered Pre-FEED Digital Twin as the next vNext scope.
**Notes:** Phase 6 is the first scoped phase inside v2.0 Pre-FEED and stays limited to package foundation.

---

## Package Identity

| Option | Description | Selected |
|--------|-------------|----------|
| Plant + optional scenario parent | Package belongs to a plant and can reference a scenario when relevant. | ✓ |
| Scenario-only parent | Package always belongs to one scenario. | |
| New plant site/unit hierarchy first | Rework v1.0 plant identity before adding packages. | |

**User's choice:** Inferred from v2.0 roadmap and v1.0 decision to keep `Plant` as the MVP unit/site identity.
**Notes:** This preserves v1.0 continuity and avoids a schema rewrite in Phase 6.

---

## Document Linking

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse Phase 5 documents | Link existing uploaded documents to Pre-FEED packages with relationship metadata. | ✓ |
| Build a separate package upload flow | Duplicate document upload/extraction under Pre-FEED. | |
| Delay documents until later | Ignore package-document relationships in Phase 6. | |

**User's choice:** Inferred from Phase 6 requirements and existing Phase 5 document intelligence layer.
**Notes:** Package links should add role/category metadata without taking ownership of document extraction fields.

---

## Audit And History

| Option | Description | Selected |
|--------|-------------|----------|
| Append/package records only | Store package state separately and do not overwrite historical scenario results. | ✓ |
| Mutate active assumptions directly | Package edits immediately rewrite financial assumptions and prior outputs. | |
| Soft archive only | Package archival is a state/status rather than destructive deletion. | ✓ |

**User's choice:** Inferred from v1.0 deterministic audit trail decisions and Phase 6 requirement `PFD-04`.
**Notes:** Later phases may derive assumptions from packages, but Phase 6 should keep history intact.

---

## Gaps And Confidence

| Option | Description | Selected |
|--------|-------------|----------|
| Deterministic package gaps | Compute rule-based metadata/document readiness gaps. | ✓ |
| LLM-generated gaps | Ask LLM to infer missing package data. | |
| No gaps until dashboard | Defer all warnings until Phase 9. | |

**User's choice:** Inferred from the project constraint that LLMs cannot become source-of-truth and from Phase 4 data gap patterns.
**Notes:** Phase 6 gaps focus on metadata and document readiness, not cost/vendor/offtake/MRV content.

---

## UI Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| New `/prefeed` workspace | Add a focused Pre-FEED workspace route for package selection and metadata. | ✓ |
| Extend `/documents` | Put package behavior inside document intelligence. | |
| Extend `/investor` | Put package foundation inside investor dashboard. | |

**User's choice:** Inferred from v2.0 roadmap and the need for a dedicated Pre-FEED workflow.
**Notes:** UI should be operational and dense, consistent with existing dashboard/workspace routes.

---

## the agent's Discretion

- Exact enum names and field names.
- Whether package gaps are stored or computed on read.
- Exact component split for `/prefeed`, provided the route is usable and consistent with existing workspaces.

## Deferred Ideas

- Cost line items, vendor comparison, and active cost basis: Phase 7.
- Offtake and MRV readiness: Phase 8.
- Risk register, decision gates, and committee dashboard/brief: Phase 9.
- OCR/vector retrieval/structured table extraction: future document intelligence milestone.
