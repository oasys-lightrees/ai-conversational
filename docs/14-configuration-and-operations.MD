# Configuration & Operations

How to configure, run, secure, and extend the system in practice. For build
steps see [`docs/09-build-and-run.MD`](09-build-and-run.MD); for the API see
[`docs/13-api-reference.MD`](13-api-reference.MD).

---

## Environment variables

Backend (`backend/.env` or the process environment; see `backend/.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `false` | FastAPI debug mode |
| `DATABASE_URL` | `postgresql+psycopg://assessment:assessment@localhost:5432/assessment` | SQLAlchemy URL. Host is `db` under Compose. |
| `OPENAI_API_KEY` | _(empty)_ | Required for chat + report; other features work without it. |
| `OPENAI_MODEL` | `gpt-4o` | Model id (must support JSON mode). |
| `OPENAI_TIMEOUT` | `30` | Per-request timeout (seconds). |
| `OPENAI_MAX_RETRIES` | `2` | SDK retry count. |
| `OPENAI_TEMPERATURE` | `0.2` | Default sampling temperature (per-call overrides exist). |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins. |
| `ADMIN_API_KEY` | _(empty)_ | Enables the admin API. **Empty = admin disabled (503).** |

Frontend (`frontend/.env.local`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend base URL (baked at build time). |

---

## Database & seeding

`init_db` creates all tables **and seeds the built-in templates** (idempotent):

```bash
python -m backend.database.init_db
```

There are no migrations yet (dev uses `create_all`). For a schema change during
development, recreate: `docker compose down -v && python -m backend.database.init_db`.
For production, introduce Alembic (flagged in `docs/10`).

Seeded templates: **Default (Hospitality, ID)** — the default — and
**Hospitality (EN)** (`backend/pipeline/seed.py`).

---

## Admin access

The admin API uses a **shared key** (`ADMIN_API_KEY`).

- Set `ADMIN_API_KEY` in the backend environment (Compose passes it through).
- In the UI, visit `/admin`, and log in with that key; it is stored in the
  browser and sent as `Authorization: Bearer <key>` on every admin request.
- Requests without the key → `401`; if the server has no key configured →
  `503` (admin disabled).

This is a single-operator model. For multiple admins / audit, upgrade to a
user table + JWT (Option B in `docs/12`).

---

## Authoring assessment templates

A template is a stored `PipelineConfig` that drives extraction, required-field
logic, question generation, and the report. Author them in the admin dashboard
(**Templates → New**) or via `POST /admin/templates`.

### The `PipelineConfig`

- **knowledge** — domain context injected into all prompts.
- **style** — LIA's persona/tone.
- **language** — `id` or `en`; drives the language LIA responds in (and the
  static closing/fallback copy).
- **fields** — the list of `FieldSpec`s to collect.

### `FieldSpec`

| Field | Meaning |
|-------|---------|
| `name` | Machine key (matches an `AssessmentData` column → typed storage; otherwise dynamic JSON). |
| `label`, `description` | Human label and extraction hint. |
| `type` | `string` / `integer` / `decimal` / `boolean` / `list` / `enum`. |
| `enum_options` | Allowed values (required for `enum`). |
| `aliases` | Alternate input keys the model might emit. |
| `required` | Always required. |
| `required_when` | Conditional: `{field: [values]}` — required when `field` is one of `values`. Enables branch logic. |
| `section` | Grouping / conversation stage. |

### Validation (server-side, `422` on failure)

- at least one field; unique field names;
- `enum` fields must have `enum_options`;
- `required_when` must reference a real field name.

### Snapshot semantics

The chosen template's config is **snapshotted onto the assessment at start**.
Editing a template afterwards does **not** change in-flight assessments — they
keep the config they began with, so reports stay reproducible. Deleting a
template referenced by any assessment is blocked (`409`).

### Field builder scope

The admin field builder edits name, type, section, required, label,
description, and enum options. `required_when` (branch logic) and `aliases` are
supported by the API/config but not yet by the builder UI — set them via the
API for now.

---

## Running the tests

```bash
# backend — Postgres required (JSONB/UUID; see docs/10 Decision D2)
pip install -r backend/requirements.txt -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://assessment:assessment@localhost:5432/assessment
pytest -q

# frontend
cd frontend && npm install && npm run build   # type-check + production build
```

The suite covers pure logic, DB-backed services, and the HTTP API (including
admin auth, template CRUD validation, and metrics).

---

## Operational notes

- **No `OPENAI_API_KEY`**: the app runs; `/chat` and `/report/generate` will
  error when they call the model. This is expected, not a failure of the app.
- **Language end-to-end**: the UI ID/EN toggle switches app chrome; LIA's
  *content* language follows the selected template's `language`. Pick an EN
  template (or author one) for an English conversation and report.
- **Latency/cost**: a normal chat turn makes two model calls (extract, then
  question); a completing turn makes one; report generation makes one. All go
  through `OpenAIService` with a shared timeout/retry policy.
