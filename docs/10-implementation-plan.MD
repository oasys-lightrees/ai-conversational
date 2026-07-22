# Implementation Plan — Service Layer

## Purpose

This document sequences the work needed to turn the scaffold into a working
application. It focuses on the backend **service layer** (`backend/services/`),
whose methods currently raise `NotImplementedError`, and the routers that call
them. It is grounded in the existing models (`backend/models/`), schemas
(`backend/schemas/`), and the design docs (`docs/03`, `docs/04`, `docs/05`).

The guiding principle is **build the foundations first, then a single vertical
slice** (start → chat turn → persisted data), and leave report generation last
because it consumes a *completed* assessment.

---

## Dependency Graph

```text
        OpenAIService (complete_json / complete_text)
                     │
        ┌────────────┼───────────────┬───────────────┐
        ▼            ▼               ▼               ▼
 ExtractionService  StateService   (question gen)   ReportService
        │            │               │               │
        └────────────┴───────┬───────┘               │
                             ▼                        │
                       ChatService ────────────┐      │
                             │                 │      │
                             ▼                 ▼      ▼
                    AssessmentService    Conversation persistence
                             │
                             ▼
                        PostgreSQL
```

`AssessmentService` (pure persistence) and `OpenAIService` (the single AI
choke point) are the two foundations. Everything else depends on one or both.

---

## Phase 0 — Test harness & fixtures (prerequisite)

There is currently no `tests/` directory. Add one before writing logic so each
phase is verifiable.

- `tests/conftest.py` — a SQLite (or ephemeral Postgres) session fixture bound
  to `Base.metadata`, plus a `TestClient` fixture.
- A **fake `OpenAIService`** that returns canned dicts/strings, so extraction,
  state, chat, and report can be tested without network or an API key.
- `pip install pytest httpx` (add to a `requirements-dev.txt`).

> Note: `AssessmentData` uses Postgres `JSONB` and `UUID` column types. If tests
> run on SQLite these need type shims, or run tests against the Compose `db`.
> Decide this here (see Open Questions).

**Exit criteria:** `pytest` runs green against an empty test.

---

## Phase 1 — Foundations

### 1a. `OpenAIService`

Implement the two wrappers (the client is already lazily wired):

- `complete_json(system_prompt, user_prompt) -> dict`
  - Call `client.chat.completions.create(...)` with
    `response_format={"type": "json_object"}`.
  - `json.loads` the message content; raise a typed error on parse failure.
- `complete_text(system_prompt, user_prompt) -> str`
  - Same call without JSON mode; return `choices[0].message.content`.

Add: model from `self.model`, temperature control, and a narrow retry/error
wrapper so callers see one exception type.

**Tests:** monkeypatch the `client` property; assert prompt assembly and
parse/error paths. No live calls.

### 1b. `AssessmentService`

Pure persistence — **no AI, no API key needed**, so this is the safest first
real code.

- `create()` → insert `Assessment(status=IN_PROGRESS, completion_percentage=0)`
  **and** its `AssessmentData` row; commit; return the `Assessment`.
- `get(id)` → query with `data` loaded; return `None` if absent.
- `update_data(id, fields)` → merge a dict of extracted fields onto the
  `AssessmentData` row (only known columns), recompute
  `completion_percentage`, bump `updated_at`; commit.
- `delete(id)` → delete (cascades to data/conversations/report) **or** set
  `status=ABANDONED` (see Open Questions).

**Field mapping is the crux here** — the extractor speaks the schema-doc
vocabulary, the DB uses column names + enums. Centralize a mapping:

| Extracted key (docs) | DB column | Notes |
|----------------------|-----------|-------|
| `location` | `property_location` | rename |
| `property_type: "Villa"` | `property_type` = `PropertyType.VILLA` | string → enum, upper-case |
| `booking_channels` | `booking_platforms`? | naming overlap — reconcile |
| branch fields (`target_launch_date`, …) | *no column exists* | see Gap G1 |

**Tests:** round-trip create → update_data → get; enum coercion; unknown keys
ignored.

**Exit criteria:** `POST /assessment/start` and `GET /assessment/{id}` work
end-to-end against the DB with **no OpenAI key set**.

---

## Phase 2 — Extraction & State

### 2a. `ExtractionService.extract(user_message, current_state) -> dict`

- Build the Prompt 1 system prompt from `docs/05` (extract many fields, ignore
  filler, normalize, never invent).
- Call `openai.complete_json`.
- Post-process: coerce strings to enum members, drop keys not in the schema,
  keep values that are still uncertain out.

### 2b. `StateService`

Requires a **canonical required-field definition** (does not exist in code yet):

- Always required: `property_type`, `property_location`, `business_stage`
  (per `docs/03`).
- Conditionally required: the branch fields keyed off `business_stage`
  (Planning / Idle / Underperforming / Operating).

Implement:
- `missing_fields(state) -> list[str]` — required minus present.
- `completion_percentage(state) -> int` — present required / total required.
- `current_stage(state) -> str` — map filled sections to the flow in `docs/03`
  (Property Profile → Business Stage → Branch → Operations → … → Complete).

**Tests:** table-driven — partial states → expected missing set / percentage /
stage. No AI needed for the rule-based parts.

---

## Phase 3 — Chat orchestration (the vertical slice)

### `ChatService.handle_message(assessment_id, message) -> ChatResponse`

Order (from `chat_service.py` docstring + `docs/05`):

1. Persist the user message (`Conversation`, role=USER).
2. `extraction.extract(message, current_state)`.
3. `assessments.update_data(id, extracted)`.
4. `state.missing_fields(...)` / `completion_percentage(...)`.
5. If complete → closing message + mark `status=COMPLETED`, set `completed_at`.
   Else → **Prompt 3 next-question** via `openai.complete_text`
   (assessment state + missing fields + history).
6. Persist the assistant reply (role=ASSISTANT); return
   `ChatResponse(reply, completion_percentage, next_stage)`.

### `ChatService.history(id) -> list[ConversationMessage]`

Ordered query by `created_at`.

**Tests:** with the fake `OpenAIService`, drive a scripted multi-turn
conversation; assert data accrues, percentage rises, and completion flips.

**Exit criteria:** `POST /chat` and `GET /conversation/{id}` work end-to-end.

---

## Phase 4 — Report generation

### `ReportService.generate(assessment_id) -> Report`

- Guard: assessment must be `COMPLETED`.
- Prompt 4 (`docs/05`) → structured JSON with the report sections + a list of
  recommendations.
- Persist `Report` + `Recommendation` rows; return the `Report`.
- Map JSON → the actual `Report` columns (`executive_summary`,
  `business_analysis`, `operational_analysis`, `technology_analysis`,
  `ai_readiness`, `recommendations_summary`, `next_steps`). Note these differ
  from the section names in `docs/05` (Gap G3).

`get(report_id)` → query with recommendations loaded.

**Exit criteria:** `POST /report/generate` then `GET /report/{id}` return a
populated report for a completed assessment.

---

## Phase 5 — Wire the routers

Replace each router's `raise NotImplementedError` with a call into the matching
service, mapping ORM objects to the response schemas and translating
`None`/not-found into `404` and guard failures into `409/400`.

**Exit criteria:** every row in the `docs/08` endpoint table returns its
documented shape; add API-level tests via `TestClient`.

---

## Sequencing Summary

| Phase | Deliverable | Needs API key? | Unblocks |
|-------|-------------|:---:|----------|
| 0 | Test harness + fake OpenAI | no | everything |
| 1a | `OpenAIService` | no (mocked) | 2, 3, 4 |
| 1b | `AssessmentService` | **no** | 3, first demo |
| 2 | Extraction + State | yes (real extract) | 3 |
| 3 | `ChatService` (slice) | yes | product core |
| 4 | `ReportService` | yes | final output |
| 5 | Routers | — | public API |

---

## Known Gaps & Risks (to resolve while implementing)

- **G1 — Branch fields have no columns.** `docs/03` defines Planning / Idle /
  Underperforming / Operating branch fields (`target_launch_date`,
  `investment_budget`, `reason_not_operating`, `main_obstacle`,
  `expansion_plan`, `automation_interest`) but `AssessmentData` has no columns
  for most of them. Either add columns or add a `JSONB` catch-all
  (e.g. `branch_data`). This blocks `StateService` conditional-required logic.
- **G2 — AI-readiness sub-scores missing.** `docs/03` lists
  `digital_maturity_score`, `process_standardization`, `data_availability`,
  `automation_readiness`; the model only has `ai_readiness_score`. Decide
  whether to compute-and-store the sub-scores or drop them.
- **G3 — Report section names differ** between `docs/05` (Current Situation,
  Key Challenges, Expected Benefits…) and the `Report` columns. Pick one
  vocabulary and map explicitly.
- **G4 — Vocabulary drift** between extractor output and DB: `location` vs
  `property_location`, `booking_channels` vs `booking_platforms`, string vs
  enum casing. A single mapping module avoids scattering this.
- **G5 — Model id.** Docs say "GPT-5.5" (not real); config defaults to
  `gpt-4o`. Confirm the intended model and that it supports JSON mode.
- **G6 — Language.** Prompts must reply in Bahasa Indonesia while field names
  stay English (`docs/05`). Bake this into the system prompts, and test it.

---

## Open Questions

1. **Test DB:** SQLite with type shims (fast, but `JSONB`/`UUID` need handling)
   or Postgres via Compose (accurate, slower)? Recommend Postgres for fidelity.
2. **Delete semantics:** hard delete (row + cascade) or soft
   (`status=ABANDONED`)? The DELETE endpoint returns `204` either way.
3. **Completion source of truth:** `StateService.completion_percentage`
   computes it; `Assessment.completion_percentage` stores it. Confirm
   `update_data` is the only writer.
4. **Branch fields (G1):** dedicated columns or a `JSONB` blob? This choice
   shapes Phase 1b and Phase 2.
