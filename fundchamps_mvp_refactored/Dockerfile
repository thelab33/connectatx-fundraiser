# Multi-stage: build assets, then runtime
FROM node:20-slim AS assets
WORKDIR /app
COPY package*.json ./
RUN npm ci || true
COPY static ./static
COPY tailwind.config.js postcss.config.js vite.config.js ./
RUN [ -d static ] && npm run build || echo "No static dir; skipping build"

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .
# Bring in built assets
COPY --from=assets /app/static/build ./static/build

EXPOSE 8000
CMD gunicorn -w 2 -k gthread -b 0.0.0.0:8000 'app:create_app()'
