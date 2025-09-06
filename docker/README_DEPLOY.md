# FundChamps • Docker Deploy (Postgres + Redis + Gunicorn)

This folder ships a **push-button production-ish** stack.

## Files
- `Dockerfile` — multi-stage build on python:3.11-slim
- `docker-compose.yml` — services: db, redis, web (+ optional nginx)
- `entrypoint.sh` — waits for DB, runs `flask db upgrade`, boots Gunicorn
- `gunicorn.conf.py` — sane worker/thread defaults
- `.env.example` — copy to `.env` and fill secrets
- `nginx.conf` — optional proxy (HTTP)

## Quickstart

```bash
cd docker
cp .env.example .env
# edit .env, set SECRET_KEY, STRIPE_API_KEY, etc.

docker compose up --build
# app: http://localhost:8000 (direct) or http://localhost:8080 via nginx
```

## Migrations
Alembic/Flask-Migrate is invoked at boot:

```bash
docker compose exec web flask db migrate -m "init"  # first time
docker compose exec web flask db upgrade
```

## Notes
- The compose mounts your project `..:/app` for fast iteration.
- Set `WORKERS` and `THREADS` via `.env` to tune concurrency.
- For TLS, terminate at an upstream (Load Balancer, Caddy, Traefik, CDN).

## Health
- `/healthz` and `/metrics/health` endpoints are mapped by your app; use them behind your load balancer.
