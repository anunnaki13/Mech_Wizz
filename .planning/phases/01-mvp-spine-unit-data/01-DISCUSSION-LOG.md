# Phase 1: MVP Spine & Unit Data - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 1-MVP Spine & Unit Data
**Areas discussed:** App spine and repository shape, data model and persistence, seed data and defaults, first UI surface, API and validation

---

## App Spine And Repository Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Blueprint monorepo | Use `backend/`, `frontend/`, root Docker Compose, root docs, and `.env.example` as described by the blueprint | ✓ |
| Backend-first skeleton | Build FastAPI and database first, defer frontend shell | |
| Frontend-first prototype | Build static dashboard first, defer real backend wiring | |

**User's choice:** Auto-selected recommended blueprint monorepo under approved YOLO/default workflow.
**Notes:** This phase must prove all three services run together and communicate.

---

## Data Model And Persistence

| Option | Description | Selected |
|--------|-------------|----------|
| Core input tables first | Implement plants, emission tests, site readiness, and hydrogen strategy now | ✓ |
| Full blueprint schema now | Implement all tables, including future scenario/result/LLM/document tables immediately | |
| Minimal plant table only | Keep schema very small and add fields later | |

**User's choice:** Auto-selected core input tables first.
**Notes:** This keeps Phase 1 aligned with its boundary while leaving structure ready for later phases.

---

## Seed Data And Defaults

| Option | Description | Selected |
|--------|-------------|----------|
| Tenayan seed from blueprint | Seed PLTU Tenayan and its two chimney emission entries exactly from the blueprint | ✓ |
| Synthetic multi-site seed | Invent several additional sites for richer UI | |
| No seed data | Require manual entry before the app is useful | |

**User's choice:** Auto-selected Tenayan seed from blueprint.
**Notes:** Missing values should stay missing or explicitly marked as unknown; no invented data in Phase 1.

---

## First UI Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Functional enterprise shell | Build dark premium dashboard shell with real Tenayan data and basic unit/profile forms | ✓ |
| Polished static mockup | Prioritize visual finish with mostly static data | |
| Plain admin CRUD | Prioritize forms only and defer dashboard styling | |

**User's choice:** Auto-selected functional enterprise shell.
**Notes:** Phase 1 should not fake charts or economics that belong to later phases.

---

## API And Validation

| Option | Description | Selected |
|--------|-------------|----------|
| REST/JSON with schemas | Use blueprint-aligned REST endpoints and structured validation | ✓ |
| Ad hoc endpoints | Add only whatever frontend needs per screen | |
| GraphQL/RPC | Use a different API style than the blueprint | |

**User's choice:** Auto-selected REST/JSON with schemas.
**Notes:** Deterministic calculations are out of scope for Phase 1.

## the agent's Discretion

- Choose specific ORM/migration and frontend data-fetching tools that fit the stack.
- Keep Phase 1 UI lean but visibly aligned with the blueprint's premium dark dashboard direction.
- Choose safe local seed behavior that avoids uncontrolled duplicate records.

## Deferred Ideas

- Calculation engine, scoring/ranking, investor dashboard, confidence/data-gap engine, LLM insight, and document intelligence are deferred to later roadmap phases.
