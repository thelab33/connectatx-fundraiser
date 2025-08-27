# Dockerfile
FROM node:20-slim AS web
WORKDIR /app/web
COPY web/package.json web/pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm i --frozen-lockfile
COPY web/ .
RUN pnpm build

FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS py
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv venv && . .venv/bin/activate && uv pip install -r requirements.txt
COPY . .
# Ship built assets into Flask static
COPY --from=web /app/web/dist/ /app/app/static/

# Runtime
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=py /app /app
RUN pip install --no-cache-dir gunicorn eventlet
EXPOSE 8080
CMD ["gunicorn","-k","eventlet","-w","1","-b","0.0.0.0:8080","app:create_app()"]

