# AI Conversational Assessment Agent

An AI-powered conversational assessment system that collects business information through natural conversations, extracts structured data, and generates business assessment reports with AI-driven recommendations.

## Features

- Natural conversational assessment
- Structured information extraction
- Dynamic follow-up questions
- PostgreSQL data storage
- AI-generated assessment reports

## Tech Stack

- Frontend: Next.js
- Backend: FastAPI
- AI: OpenAI (the docs reference "GPT-5.5"; use a real model id such as `gpt-4o`)
- Database: PostgreSQL
- Docker

## Project Structure

```text
.
├── backend/                # FastAPI application
│   ├── config.py           # Settings loaded from env / .env
│   ├── main.py             # App entrypoint (CORS + routers + /health)
│   ├── database/           # Engine, session, Base, init_db
│   ├── models/             # SQLAlchemy ORM models (5 tables) + enums
│   ├── schemas/            # Pydantic request/response schemas
│   ├── routers/            # API route handlers (7 endpoints)
│   ├── services/           # Business logic layer (currently stubs)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/               # Next.js application
│   ├── app/                # App-router pages (landing, assessment, report, 404)
│   ├── components/         # Atomic-design components (ui/assessment/chat/report/layout)
│   ├── lib/api.ts          # Typed API client
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docs/                   # Design documentation
└── docker-compose.yml      # db + backend + frontend
```

> **Status:** this is a scaffold. The structure, models, schemas, routes,
> config, and Docker setup are in place. The service layer methods are stubs
> (`NotImplementedError`) awaiting the business logic described in `docs/`.

## Getting Started

### With Docker Compose

```bash
cp backend/.env.example backend/.env   # set OPENAI_API_KEY
docker compose up --build
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000
- Postgres: localhost:5432

### Backend (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env    # edit DATABASE_URL, OPENAI_API_KEY
python -m backend.database.init_db      # create tables
uvicorn backend.main:app --reload
```

### Frontend (local)

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## API

Endpoints are served under `/api/v1` (see `docs/08-api-design.MD`):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/assessment/start` | Start a new assessment |
| POST | `/api/v1/chat` | Process one conversation turn |
| GET | `/api/v1/assessment/{id}` | Get assessment data |
| GET | `/api/v1/conversation/{id}` | Get conversation history |
| POST | `/api/v1/report/generate` | Generate the report |
| GET | `/api/v1/report/{id}` | Get the report |
| DELETE | `/api/v1/assessment/{id}` | Delete an assessment |
