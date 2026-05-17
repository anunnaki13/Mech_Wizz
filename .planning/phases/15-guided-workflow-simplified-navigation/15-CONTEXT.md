---
phase: 15
milestone: v2.6
status: planned
created: 2026-05-18
---

# Phase 15 Context: Guided Workflow & Simplified Navigation

## Trigger

Phase 14 found that the application is reachable but too hard to operate. The user also reported that modules feel unclear, saving/destructive actions are confusing, and the lower-left Next.js dev indicator looks like an unexplained menu.

## Goal

Make the app easier for a non-technical operator to use without changing the deterministic calculation model.

The operating path should be:

1. Dashboard - read the executive summary and current recommendation.
2. Pilot Decision - see the current business answer and blockers.
3. Evidence - update missing or rejected validation evidence.
4. Validation Pack - open committee-ready checklist and memo.

## Scope

- Group sidebar navigation by operator intent.
- Add active navigation state.
- Add a guided workflow panel on the dashboard.
- Replace stale dashboard "Phase 11" guidance with current next-step guidance.
- Add concise Indonesian glossary/help text for core terms.
- Add next-step messages after saves in evidence, scenarios, and Pre-FEED workspaces.
- Add confirmation dialogs before destructive archive/delete/unlink actions.
- Disable the Next.js dev indicator that appears as a lower-left "N" in development.
- Reduce navigation prefetching for heavy modules from the sidebar.

## Non-Goals

- No changes to PLTU data, coordinates, scoring formulas, or backend calculations.
- No new business module.
- No route removal; advanced modules remain available but grouped.

## Acceptance Criteria

- Primary navigation is grouped and highlights the current page.
- Dashboard explains what to do next and points to Pilot Decision first.
- Evidence save tells the user to review Pilot Decision after saving.
- Scenario and Pre-FEED saves tell the user what the next operational step is.
- Destructive actions require confirmation before API calls.
- The lower-left Next.js dev indicator is disabled.
- Frontend production build passes.
- Key routes and backend APIs still return HTTP 200.
