# Production deploy — nginx reverse proxy + certbot (TLS)

Runs the full stack behind an nginx reverse proxy with automatic HTTPS from
Let's Encrypt. Only nginx is exposed (ports 80/443); the backend, frontend, and
database are reachable on the internal Docker network only.

```text
Internet ──▶ nginx (80/443, TLS)
                ├─ /api/  ─▶ backend:8000  (FastAPI)
                ├─ /health ▶ backend:8000
                └─ /      ─▶ frontend:3000 (Next.js)
             certbot ──▶ renews the certificate; nginx reloads every 6h
```

## Prerequisites

- A host with Docker + Docker Compose and ports **80/443 open**.
- A **DNS A record** pointing your domain at the host (must resolve before you
  request a certificate).

## First-time setup

From this `deploy/` directory:

```bash
export DOMAIN=example.com
export EMAIL=you@example.com          # optional, for expiry notices
export OPENAI_API_KEY=sk-...          # required for chat + report
export ADMIN_API_KEY=choose-a-secret  # required for /admin
# export POSTGRES_PASSWORD=...        # optional; defaults to "assessment"

# 1. Build images (frontend bakes in https://$DOMAIN/api/v1)
docker compose -f docker-compose.prod.yml build

# 2. Obtain the certificate and start nginx
#    (tip: run once with STAGING=1 first to avoid rate limits while testing)
./init-letsencrypt.sh

# 3. Start the whole stack
docker compose -f docker-compose.prod.yml up -d

# 4. One-time: create tables + seed templates
docker compose -f docker-compose.prod.yml exec backend python -m backend.database.init_db
```

Your app is now at `https://$DOMAIN`, admin at `https://$DOMAIN/admin`.

## Notes

- **Renewal is automatic** — the `certbot` service renews twice daily and nginx
  reloads every 6h to pick up new certs.
- **Certificates live in `deploy/certbot/`** (bind-mounted) and are git-ignored —
  never commit them.
- **Changing the domain** requires rebuilding the frontend (the API URL is baked
  in at build time) and re-running `init-letsencrypt.sh`.
- **Secrets**: prefer exporting from your secrets manager (SSM/Secrets Manager)
  over a plaintext `.env`. See [`../docs/16-deployment.MD`](../docs/16-deployment.MD).
