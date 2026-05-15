<!-- GSD:project-start source:PROJECT.md -->
## Project

**MECH WIZ AI Digital Twin**

MECH WIZ AI Digital Twin is a web-based pre-feasibility simulation and decision-support engine for identifying PLN NP power generation units that are suitable candidates for e-methanol / carbon-to-fuel projects. It combines unit mapping, deterministic technical and financial calculations, scoring, ranking, sensitivity analysis, data confidence tracking, data gap analysis, investor-facing dashboards, and LLM-generated narrative insight.

This is not a real-time operational digital twin connected to DCS/SCADA. The MVP is an assumption-driven simulator that works with incomplete early-stage data by using explicit assumptions, confidence levels, and visible data gaps.

**Core Value:** Help PLN NP select the best pilot unit for MECH WIZ and explain the early feasibility case visually, quantitatively, and in an investor-friendly way without inventing unsupported numbers.

### Constraints

- **Calculation Authority**: Deterministic backend code must calculate all technical and financial outputs - LLM must not invent or calculate source-of-record numbers.
- **Data Status**: Important inputs must carry `data_status` values: `actual`, `estimated`, `benchmark`, `user_assumption`, `unknown`, or `partner_supplied`.
- **Confidence**: Important outputs must carry `confidence_level` values: `high`, `medium`, `low`, or `unknown`.
- **Incomplete Data**: Missing inputs must trigger default assumptions, low-confidence output labels, data gaps, and recommended collection actions.
- **Backend Stack**: FastAPI/Python is preferred because calculation services are central to the product.
- **Frontend Stack**: Next.js/React/TypeScript is preferred for dashboard delivery and VPS deployment.
- **Deployment**: The target runtime is VPS with Docker Compose and Nginx.
- **LLM Provider**: LLM integration should use OpenRouter.
- **Seed Data**: The initial MVP should include PLTU Tenayan sample data from the blueprint.
- **Language**: Investor and management narratives should support concise professional Indonesian.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
