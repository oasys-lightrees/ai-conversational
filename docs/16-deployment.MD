# Deployment (AWS)

How to deploy the three services (Next.js frontend, FastAPI backend,
PostgreSQL) on AWS. For local setup see [`09-build-and-run.MD`](09-build-and-run.MD);
for env vars see [`14-configuration-and-operations.MD`](14-configuration-and-operations.MD).

## Resource profile

The app is **I/O-bound, not compute-bound** — the LLM runs on OpenAI's servers,
so the app processes mostly wait on network. A chat turn makes two sequential
OpenAI calls; a completing turn one; report generation one. Size for **memory
and request concurrency**, not CPU. Scale on concurrency; the real ceiling is
OpenAI latency and rate limits, not local CPU.

## Instance sizing

| Setup | Recommendation | Notes |
|-------|----------------|-------|
| Single-box (MVP/demo) | **`t4g.medium`** (2 vCPU / 4 GB, ARM) or `t3.medium` | Runs all three containers via Compose. 4 GB is the comfortable floor (Next build + Postgres + Python). Avoid 2 GB. |
| Backend task (Fargate/App Runner) | **0.5 vCPU / 1 GB** | Scale out on concurrency, not CPU. |
| Frontend task | **0.5 vCPU / 1 GB** | Or host statically (see below). |
| Database | **RDS `db.t4g.micro` / `small`** | Don't run Postgres in a container for real data. |
| Disk (single-box) | 20–30 GB gp3 | Plenty for images + a demo DB. |

---

## Option A — Single EC2 + Docker Compose (fastest)

Best for a demo or low-traffic pilot.

1. **Launch** a `t4g.medium` (Amazon Linux 2023 / Ubuntu), 20–30 GB gp3.
   Security group: 80/443 inbound (and 22 for admin). Do **not** expose 8000/5432.
2. **Install Docker + Compose**, then clone the repo and check out `main`.
3. **Secrets** — store `OPENAI_API_KEY` and `ADMIN_API_KEY` in **SSM Parameter
   Store** (SecureString) and export them at deploy time; don't bake them into
   the image or commit them.
4. **Build the frontend with the public API URL** — `NEXT_PUBLIC_API_BASE_URL`
   is baked at build time, so it must point at the public backend URL, e.g.
   `https://api.example.com/api/v1` (see "Frontend base URL" below).
5. **Start** and **initialize the database** (one-off, no migrations yet):
   ```bash
   export OPENAI_API_KEY=... ADMIN_API_KEY=...
   docker compose up -d --build
   docker compose exec backend python -m backend.database.init_db
   ```
6. **TLS + routing** — put a reverse proxy in front (Caddy/Nginx with Let's
   Encrypt, or an ALB + ACM certificate) terminating HTTPS and routing to the
   frontend (:3000) and backend (:8000).
7. Set `CORS_ORIGINS` to the real frontend origin (not `localhost:3000`).

> The Compose `db` is fine for a demo. For anything you can't lose, point
> `DATABASE_URL` at RDS instead (below).

---

## Option B — Managed services (recommended for production)

No instances to manage; scales on traffic.

- **Backend** → **App Runner** or **ECS Fargate** from the backend image
  (`backend/Dockerfile`). Health check path `/health`. Inject secrets from
  Secrets Manager / SSM. Set `DATABASE_URL`, `CORS_ORIGINS`, `OPENAI_API_KEY`,
  `ADMIN_API_KEY`.
- **Frontend** → either an ECS/App Runner service from `frontend/Dockerfile`
  (Next standalone), or a static/SSR host (Amplify Hosting, or S3 + CloudFront).
  Whatever the path, build with `NEXT_PUBLIC_API_BASE_URL` set to the backend's
  public URL.
- **Database** → **RDS for PostgreSQL 16** (`db.t4g.micro`+). Put the backend in
  the same VPC/subnets; allow 5432 only from the backend's security group.
  Enable automated backups.
- **Edge** → CloudFront in front of the frontend; ALB (or App Runner's built-in
  HTTPS) in front of the backend; ACM for certificates.

Autoscaling: target **request count / concurrency per task**, not CPU.

---

## Cross-cutting requirements

### Secrets
`OPENAI_API_KEY`, `ADMIN_API_KEY`, and the DB password belong in **SSM Parameter
Store** or **Secrets Manager**, injected as env vars at runtime — never in the
image, repo, or Compose file.

### Frontend base URL (build-time)
`NEXT_PUBLIC_API_BASE_URL` is compiled into the frontend bundle. You must set it
**when building the frontend image/site**, pointing at the public backend URL
(including the `/api/v1` suffix). Changing it later requires a rebuild.

### Database initialization & migrations
There are no migrations yet — `init_db` runs `create_all` + seeds the templates.
Run it **once** against the target database after first deploy (a one-off ECS
task, `docker compose exec`, or a short job). **Before production**, add Alembic
so schema changes don't require recreating the DB (flagged in
[`10-implementation-plan.MD`](10-implementation-plan.MD)).

### CORS & HTTPS
Set `CORS_ORIGINS` to the exact frontend origin(s). Terminate TLS at the
proxy/edge; the app services can speak plain HTTP inside the VPC.

### Health checks
Backend exposes `GET /health` → `{"status":"ok"}` — use it for ALB/App Runner /
container health checks.

### OpenAI considerations
Throughput is bounded by your OpenAI rate limits and per-call latency, not the
instance. If turns feel slow or 429s appear, that's OpenAI — raise limits or add
backoff, don't upsize the instance. `OPENAI_TIMEOUT` / `OPENAI_MAX_RETRIES` are
tunable via env.

---

## Deploy checklist

- [ ] Secrets in SSM/Secrets Manager (`OPENAI_API_KEY`, `ADMIN_API_KEY`, DB creds)
- [ ] `DATABASE_URL` → RDS (production) or Compose `db` (demo only)
- [ ] Frontend built with the correct `NEXT_PUBLIC_API_BASE_URL`
- [ ] `CORS_ORIGINS` = real frontend origin
- [ ] TLS/HTTPS at the edge; 8000/5432 not publicly exposed
- [ ] `python -m backend.database.init_db` run once against the target DB
- [ ] `GET /health` wired to health checks
- [ ] `/admin` reachable and login works with `ADMIN_API_KEY`

## Rough cost (us-east-1, on-demand, ballpark)

- Single `t4g.medium` + 30 GB gp3: ~**$30–35/mo**.
- Managed: App Runner (backend) + Amplify/CloudFront (frontend) + RDS
  `db.t4g.micro`: ~**$40–70/mo** at low traffic, scaling with usage.
