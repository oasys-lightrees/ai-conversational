# Build & Run Guide

## Purpose

This document is a step-by-step guide for building and running the
**AI Conversational Assessment Agent** from a fresh checkout. It covers both the
Docker Compose path (recommended) and the local development path for the backend
and frontend individually.

> **Status reminder:** the repository is currently a scaffold. The structure,
> models, schemas, routes, config, and Docker setup are in place, but the service
> layer methods raise `NotImplementedError`. The application will build, start,
> and serve `/health`, `/docs`, and the frontend pages, but the assessment/chat/
> report endpoints will error until the service logic (described in `docs/`) is
> implemented.

---

## Prerequisites

| Tool | Version | Needed for |
|------|---------|------------|
| Docker + Docker Compose | 24+ / Compose v2 | Compose path (all-in-one) |
| Python | 3.12+ (`requires-python >=3.12`) | Backend local path |
| Node.js | 20+ | Frontend local path |
| PostgreSQL | 16 | Backend local path (or use the Compose `db`) |
| OpenAI API key | — | AI features (chat / extraction / report) |

Clone the repository and `cd` into it before running any commands below:

```bash
git clone <repo-url> ai-conversational
cd ai-conversational
```

---

## Architecture at a Glance

```text
frontend (Next.js :3000)  ──HTTP──▶  backend (FastAPI :8000)  ──▶  db (Postgres :5432)
                                          │
                                          └──▶ OpenAI API
```

Three services, wired together in `docker-compose.yml`:

- **db** — `postgres:16-alpine`, database/user/password all `assessment`.
- **backend** — FastAPI app built from `backend/Dockerfile`, served by uvicorn.
- **frontend** — Next.js app built from `frontend/Dockerfile` (standalone output).

---

## Option A — Docker Compose (recommended)

This is the fastest way to get all three services running together.

### Step 1 — Configure the backend environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set your OpenAI key. At minimum:

```dotenv
OPENAI_API_KEY=sk-your-real-key
```

> Note: `docker-compose.yml` sets `DATABASE_URL`, `OPENAI_MODEL`, and
> `CORS_ORIGINS` for the backend service directly, and reads `OPENAI_API_KEY`
> / `OPENAI_MODEL` from your shell environment (`${OPENAI_API_KEY:-}`). You can
> export them in your shell instead of relying on `backend/.env`:
>
> ```bash
> export OPENAI_API_KEY=sk-your-real-key
> export OPENAI_MODEL=gpt-4o        # optional; defaults to gpt-4o
> ```

### Step 2 — Build and start

```bash
docker compose up --build
```

This will:

1. Pull and start Postgres, waiting for its healthcheck (`pg_isready`).
2. Build the backend image and start uvicorn on port 8000.
3. Build the frontend image and start Next.js on port 3000.

### Step 3 — Create the database tables

The backend image does **not** run migrations automatically. In a second
terminal, create the tables inside the running backend container:

```bash
docker compose exec backend python -m backend.database.init_db
```

You should see `Database tables created.`

### Step 4 — Verify

| Service | URL |
|---------|-----|
| Backend health | http://localhost:8000/health → `{"status":"ok"}` |
| Backend API docs | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| Postgres | `localhost:5432` (user/pass/db = `assessment`) |

### Step 5 — Stop / clean up

```bash
docker compose down            # stop containers
docker compose down -v         # also remove the db_data volume (wipes data)
```

---

## Option B — Local development

Run each service directly on your machine. Useful for hot-reload and debugging.

### B1 — Database

You still need a Postgres 16 instance. The simplest option is to start just the
Compose `db` service:

```bash
docker compose up -d db
```

This exposes Postgres on `localhost:5432` with user/password/database all set to
`assessment`, which matches the default `DATABASE_URL`.

Alternatively, point `DATABASE_URL` at any existing Postgres instance.

### B2 — Backend (FastAPI)

Run all commands from the **repository root** (the app is imported as the
`backend` package, e.g. `backend.main:app`).

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
cp backend/.env.example backend/.env
#    Edit backend/.env: set OPENAI_API_KEY and confirm DATABASE_URL
#    (default points at localhost:5432, which matches the Compose db service)

# 4. Create database tables
python -m backend.database.init_db

# 5. Start the API with auto-reload
uvicorn backend.main:app --reload
```

The backend is now on http://localhost:8000 (docs at `/docs`, health at
`/health`).

### B3 — Frontend (Next.js)

In a separate terminal:

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env.local
#    NEXT_PUBLIC_API_BASE_URL defaults to http://localhost:8000/api/v1,
#    which matches the local backend above.

# 3. Start the dev server
npm run dev
```

The frontend is now on http://localhost:3000.

To build/run a production bundle locally instead:

```bash
npm run build
npm run start
```

---

## Configuration Reference

### Backend (`backend/.env` / environment)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `false` | FastAPI debug mode |
| `DATABASE_URL` | `postgresql+psycopg://assessment:assessment@localhost:5432/assessment` | SQLAlchemy connection URL (host is `db` under Compose) |
| `OPENAI_API_KEY` | _(empty)_ | Required for AI features |
| `OPENAI_MODEL` | `gpt-4o` | Chat/completion model (docs mention "GPT-5.5", which is not a real id) |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed frontend origins |

### Frontend (`frontend/.env.local` / environment)

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Base URL the API client calls |

---

## API Endpoints (once services are up)

All endpoints are served under the `/api/v1` prefix (see `docs/08-api-design.MD`):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/assessment/start` | Start a new assessment |
| POST | `/api/v1/chat` | Process one conversation turn |
| GET | `/api/v1/assessment/{id}` | Get assessment data |
| GET | `/api/v1/conversation/{id}` | Get conversation history |
| POST | `/api/v1/report/generate` | Generate the report |
| GET | `/api/v1/report/{id}` | Get the report |
| DELETE | `/api/v1/assessment/{id}` | Delete an assessment |

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `NotImplementedError` from an endpoint | Expected — service layer is still a stub. Only `/health`, `/docs`, and page rendering work end-to-end. |
| Backend can't connect to the database | Ensure Postgres is running and `DATABASE_URL` matches. Under Compose the host must be `db`, not `localhost`. |
| `relation "..." does not exist` | Tables not created — run `python -m backend.database.init_db` (Step 3 / B2.4). |
| `ModuleNotFoundError: backend` | Run backend commands from the repository root, not from inside `backend/`. |
| Frontend can't reach the API / CORS errors | Confirm `NEXT_PUBLIC_API_BASE_URL` and that the frontend origin is listed in `CORS_ORIGINS`. |
| OpenAI auth errors | Set a valid `OPENAI_API_KEY`; confirm `OPENAI_MODEL` is a real model id. |
| Port already in use (3000/8000/5432) | Stop the conflicting process or remap ports in `docker-compose.yml`. |
