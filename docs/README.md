# Documentation

Documentation for the AI Conversational Assessment Agent. Start with the
[project README](../readme.MD) for an overview and quickstart.

## Reference (current system)

Authoritative docs for the system as built:

| Doc | What |
|-----|------|
| [09 — Build & Run](09-build-and-run.MD) | Setup: Docker Compose and local dev |
| [13 — API Reference](13-api-reference.MD) | All endpoints (public + admin), request/response shapes |
| [14 — Configuration & Operations](14-configuration-and-operations.MD) | Env vars, admin auth, authoring templates, testing |
| [11 — Pipeline Config](11-pipeline-config.MD) | The configurable pipeline: `PipelineConfig`, `FieldSpec`, hybrid storage, templates |
| [12 — Admin Dashboard](12-admin-dashboard.MD) | Admin design: templates, assessments browser, metrics, auth |

## Design docs (original intent)

The design documents the implementation was built from. Where behavior differs,
the reference docs above and the "Implementation status" notes in 10–12 are
authoritative.

| Doc | What |
|-----|------|
| [01 — Business Problem](01-business-problem.MD) | Why the product exists |
| [02 — User Personas](02-user-personas.MD) | Who it serves |
| [03 — Assessment Schema](03-assessment-schema.MD) | Fields collected/derived (the default schema) |
| [04 — Conversational Flow](04-conversational-flow.MD) | Turn-by-turn flow |
| [05 — Prompt Design](05-prompt-design.MD) | The four prompts (extraction, missing-field, question, report) |
| [06 — System Architecture](06-system-architecture.MD) | High-level architecture |
| [07 — Database Design](07-database-design.MD) | Tables and relationships |
| [08 — API Design](08-api-design.MD) | Original endpoint design |
| [10 — Implementation Plan](10-implementation-plan.MD) | Sequenced service-layer plan + locked decisions |
| [stages](stages.MD) | Milestone outline |

## Frontend docs

| Doc | What |
|-----|------|
| [frontend/01 — User Flow](frontend/01-user-flow.MD) | Landing → chat → report |
| [frontend/02 — Wireframe](frontend/02-wireframe.MD) | Layout sketches |
| [frontend/03 — UI Components](frontend/03-ui-components.MD) | Atomic-design component tree |
| [frontend/04 — Design System](frontend/04-design-system.MD) | Tokens and styling |
| [frontend/05 — Page Specification](frontend/05-page-specification.MD) | Per-page routes, components, API calls |

## Reading paths

- **Run it:** README → [09](09-build-and-run.MD) → [14](14-configuration-and-operations.MD)
- **Integrate:** [13 — API Reference](13-api-reference.MD)
- **Configure assessments:** [11](11-pipeline-config.MD) → [14 · Authoring templates](14-configuration-and-operations.MD)
- **Operate:** [12](12-admin-dashboard.MD) → [14](14-configuration-and-operations.MD)
