---
phase: 15
plan: 1
status: planned
created: 2026-05-18
---

# Phase 15 Plan: Guided Workflow & Simplified Navigation

## Tasks

1. Navigation shell
   - Convert `AppShell` to a client component.
   - Group routes into Decision, Analysis, and Data/Admin sections.
   - Add active route state and compact topbar workflow links.
   - Disable sidebar Link prefetching to avoid eager-loading heavy modules.

2. Dashboard guidance
   - Add reusable guided workflow component.
   - Put Pilot Decision and Evidence ahead of secondary modules.
   - Add Indonesian glossary for LCOM, MRV, Evidence, Pre-FEED, Pilot Decision, WIZ Align, confidence, and data status.
   - Replace stale Phase 11 side panel with current operator next step.

3. Save and destructive action UX
   - Add post-save next-step messages in Evidence, Scenarios, and Pre-FEED workspaces.
   - Add browser confirmation for scenario delete, package archive, document unlink, cost item delete, vendor proposal delete, price deck delete, offtake delete, MRV delete, risk delete, and decision gate delete.

4. Runtime polish
   - Disable Next.js dev indicator.
   - Update styles for grouped nav, active state, workflow cards, glossary, and operator strips.

5. Verification
   - Run frontend build.
   - Run backend tests if environment is available.
   - Smoke key frontend routes and APIs.
   - Run GSD state validation and secret scan.
   - Commit and push to GitHub main.

## Risks

- AppShell becomes a client component; keep it lightweight and avoid importing large modules.
- Confirmation dialogs must run only in client components.
- Dashboard additions must not make the first page visually heavier or less scannable.
