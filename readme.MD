# AI Conversational Assessment Agent

An AI-powered system that assesses a property business through a natural
conversation. "LIA" collects information turn by turn, extracts it into a
structured schema, tracks completion, and generates a business assessment report
with prioritized recommendations. The whole pipeline is **configurable per
assessment** via templates, and an **admin dashboard** lets operators author
templates and monitor activity — no code changes required.

> **Status:** feature-complete MVP. The AI features require an `OPENAI_API_KEY`;
> everything else (admin, template management, browsing) works without one.

## Features

- **Conversational assessment** — one question at a time, in Bahasa Indonesia or
  English, adapting to the user's answers.
- **Structured extraction** — each turn extracts fields into a defined schema
  (hybrid storage: typed columns + a dynamic JSON area).
- **Dynamic follow-ups** — rule-based required-field/branch logic decides what to
  ask next; the model phrases the question.
- **AI report** — an executive summary, section-by-section analysis, and
  priority-ranked recommendations.
- **Configurable pipeline** — set the domain **knowledge**, **style/persona**,
  **language**, and the **fields to extract** per assessment via templates.
- **Admin dashboard** — template CRUD with a field builder, an assessments
  browser (data + transcript + report), and metrics. Shared-key auth.
- **Bilingual UI** — ID/EN toggle across the public app.

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | Next.js 15 (App Router), React 19, Tailwind, next-themes, lucide-react |
| Backend | FastAPI, SQLAlchemy 2, Pydantic v2 |
| AI | OpenAI (default `gpt-4o`) |
| Database | PostgreSQL 16 |
| Infra | Docker Compose |

## Architecture

The AI pipeline has two flows, both routed through a single `OpenAIService`
choke point. See [`docs/`](docs/) for details.

**Chat turn** (`/chat`): persist message → **extract** (Prompt 1, JSON) → **map**
to columns/JSON → **recompute** required/completion/stage (rule-based) → **ask
the next question** (Prompt 3) or **close out** when complete.

**Report** (`/report/generate`): guard on `COMPLETED` → **generate** the report
(Prompt 4, JSON) → persist sections + recommendations.

Every stage is driven by a `PipelineConfig` (knowledge, style, language,
fields), snapshotted onto each assessment at start.

## Project structure

```text
.
├── backend/
│   ├── main.py                 # FastAPI app (CORS + routers + /health)
│   ├── config.py               # Settings (env / .env)
│   ├── database/               # engine, session, init_db (+ seed)
│   ├── models/                 # ORM: assessment, conversation, report, template
│   ├── schemas/                # Pydantic request/response models
│   ├── pipeline/               # PipelineConfig, FieldSpec, DEFAULT_CONFIG, FieldMapper, seed
│   ├── services/               # extraction, state, chat, report, assessment, template, openai
│   └── routers/                # assessment, chat, conversation, report, template, admin/
├── frontend/
│   ├── app/                    # public pages + /admin route group
│   ├── components/             # ui/ chat/ report/ assessment/ landing/ layout/ admin/
│   ├── hooks/                  # useAssessment, useReport
│   └── lib/                    # api, adminApi, i18n, session, ...
├── docs/                       # design + reference documentation
└── docker-compose.yml          # db + backend + frontend
```

## Getting started

### Docker Compose (recommended)

```bash
export OPENAI_API_KEY=sk-...        # required for chat + report
export ADMIN_API_KEY=choose-a-key   # required to use /admin
docker compose up --build

# one-time: create tables and seed the built-in templates
docker compose exec backend python -m backend.database.init_db
```

- App: http://localhost:3000
- Admin: http://localhost:3000/admin (log in with `ADMIN_API_KEY`)
- API docs: http://localhost:8000/docs

### Local development

See [`docs/09-build-and-run.MD`](docs/09-build-and-run.MD) for the backend
(uvicorn) and frontend (npm) local setup.

## API

Served under `/api/v1`. Full details in
[`docs/13-api-reference.MD`](docs/13-api-reference.MD).

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/assessment/start` | — | Start an assessment (optional `template_id`) |
| POST | `/chat` | — | Process one conversation turn |
| GET | `/assessment/{id}` | — | Get collected data |
| GET | `/conversation/{id}` | — | Get transcript |
| POST | `/report/generate` | — | Generate the report |
| GET | `/report/{id}` | — | Get the report |
| DELETE | `/assessment/{id}` | — | Delete an assessment |
| GET | `/templates`, `/templates/{id}` | — | List/get templates (for the picker) |
| `*` | `/admin/**` | Bearer | Template CRUD, assessments browser, metrics |

## Configuration

Key environment variables (full list in
[`docs/14-configuration-and-operations.MD`](docs/14-configuration-and-operations.MD)):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | local Postgres | SQLAlchemy URL (`db` host under Compose) |
| `OPENAI_API_KEY` | _(empty)_ | Required for AI features |
| `OPENAI_MODEL` | `gpt-4o` | Chat/report model |
| `ADMIN_API_KEY` | _(empty)_ | Enables the admin API; empty = disabled |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins |

## Testing

```bash
# backend — requires Postgres (see docs/10 Decision D2)
pip install -r backend/requirements.txt -r requirements-dev.txt
DATABASE_URL=postgresql+psycopg://assessment:assessment@localhost:5432/assessment pytest

# frontend
cd frontend && npm install && npm run build
```

94 backend tests (pure + DB-backed + API) run against real Postgres.

## Documentation

See the [`docs/`](docs/README.md) index for the design docs, API reference,
configuration guide, and the frontend docs.
