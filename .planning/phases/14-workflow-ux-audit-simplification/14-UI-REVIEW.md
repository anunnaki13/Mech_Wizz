---
phase: 14
status: reviewed
created: 2026-05-17
---

# UI Review: Workflow Simplicity Audit

## Executive Finding

The application is now feature-rich but too complex for a non-technical operator. Most modules work at route/API level, but the user is forced to understand many separate pages and technical concepts before knowing what to do next.

## 6-Pillar Scores

| Pillar | Score | Finding |
|--------|------:|---------|
| Clarity | 2/4 | Pages explain their own module, but the full app flow is not clear. |
| Visual hierarchy | 3/4 | Cards, KPIs, and reports are generally readable; Pre-FEED and form-heavy pages are dense. |
| Task flow | 1/4 | No guided end-to-end workflow from data input to pilot decision. |
| Feedback | 2/4 | Save/refresh status messages exist, but downstream effects are not obvious. |
| Safety | 2/4 | Destructive/archive/delete actions exist without a consistent confirmation step. |
| Cognitive load | 1/4 | 13 sidebar items, mixed technical labels, and many forms create high operator burden. |

Overall score: **11/24**.

## Route Smoke Results

| Route | Status | Notes |
|-------|--------|-------|
| `/dashboard` | PASS | Good summary entry point, but does not guide the next action strongly enough. |
| `/dashboard/map` | PASS | Interactive map page is useful but feels separate from decision workflow. |
| `/shortlist` | PASS | Strong decision matrix, but should be integrated into a guided flow. |
| `/validation-pack` | PASS | Good management artifact, mostly read-only. |
| `/evidence` | PASS | Functional, but evidence workflow needs clearer document/upload linkage. |
| `/pilot-decision` | PASS | Good endpoint for management, should become the main destination after dashboard. |
| `/units` | PASS | Data-entry oriented; too low-level for most users. |
| `/scenarios` | PASS | Powerful but heavy; user must understand schemes and assumptions. |
| `/investor` | PASS | Useful but depends on selected scenario context that is not obvious. |
| `/prefeed` | PASS | Too dense; combines packages, documents, cost/vendor, offtake/MRV, risk, gates in one page. |
| `/sensitivity` | PASS | Works, but should be presented as optional analysis. |
| `/documents` | PASS | Useful, but not integrated enough with evidence tasks. |
| `/settings` | PASS | Necessary admin page; should be kept away from daily workflow. |

## Button/Form Inventory

Runtime rendered count:

| Route | Buttons | Links | Fields |
|-------|--------:|------:|-------:|
| `/dashboard` | 0 | 18 | 0 |
| `/dashboard/map` | 3 | 13 | 12 |
| `/shortlist` | 0 | 16 | 0 |
| `/validation-pack` | 0 | 17 | 0 |
| `/evidence` | 17 | 15 | 13 |
| `/pilot-decision` | 0 | 15 | 0 |
| `/units` | 1 | 39 | 0 |
| `/scenarios` | 6 | 13 | 36 |
| `/investor` | 7 | 13 | 2 |
| `/prefeed` | 5 | 13 | 15 |
| `/sensitivity` | 2 | 13 | 9 |
| `/documents` | 4 | 13 | 5 |
| `/settings` | 4 | 13 | 7 |

This confirms the most complex operator pages are `/scenarios`, `/evidence`, `/prefeed`, `/dashboard/map`, and `/sensitivity`.

## Critical UX Problems

1. **No single “Start Here” workflow.**
   Users see modules, not a process. The app needs to say: review dashboard -> inspect map -> choose shortlist -> collect evidence -> review pilot decision.

2. **Sidebar is too flat.**
   13 navigation items are equal weight. Daily workflow, advanced tools, data entry, documents, and settings need grouping.

3. **Pre-FEED is overloaded.**
   One page contains package metadata, document links, cost/vendor, offtake/MRV, risk, gates, and dashboard. This is too much for non-expert operation.

4. **Save actions do not explain downstream impact.**
   After saving scenarios, evidence, settings, package data, or assumptions, the user is not told whether scoring, shortlist, validation, or pilot decision should be refreshed next.

5. **Destructive actions lack consistent confirmation.**
   Delete/archive buttons exist for scenarios, Pre-FEED packages, cost items, vendor proposals, price decks, offtake, MRV, risks, and gates. The code scan did not find a consistent `confirm()`/modal pattern.

6. **Evidence and Documents are separated.**
   Evidence needs actual source proof, but `/evidence` mainly uses status/reference URL while document upload/linking lives elsewhere.

7. **Technical vocabulary is unavoidable.**
   Terms like LCOM, MRV, data_status, confidence_level, WIZ Align, Pre-FEED, and carbon accounting appear without a simplified operator layer.

8. **Module order can be misread.**
   A user can open Investor, Sensitivity, Pre-FEED, or Settings before understanding that the main product output is Pilot Decision.

## Recommended Simplified Workflow

### Primary Operator Flow

1. **Dashboard** - see current Top candidate and overall status.
2. **Pilot Decision** - see whether a candidate can advance or what blocks it.
3. **Evidence Tasks** - close only the required evidence blockers.
4. **Map / Shortlist** - inspect why candidates rank as they do.
5. **Validation Pack / PDF** - export discussion material.

### Secondary/Admin Flow

1. Units.
2. Scenarios.
3. Documents.
4. Pre-FEED.
5. Sensitivity.
6. Settings.

## Recommended Next Implementation Phase

**Phase 15: Guided Workflow & Simplified Navigation**

Deliver:

- New home/dashboard workflow panel: “What should I do next?”
- Grouped sidebar:
  - Decision: Dashboard, Pilot Decision, Evidence, Validation Pack.
  - Analysis: Map, Shortlist, Sensitivity, Investor.
  - Data/Admin: Units, Scenarios, Documents, Pre-FEED, Settings.
- Add active nav state.
- Add stepper cards across key pages.
- Add “next recommended action” after save operations.
- Add confirmation dialogs for destructive actions.
- Add a simple Indonesian glossary/tooltips for core terms.
