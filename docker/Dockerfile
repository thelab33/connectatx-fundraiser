FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /w
COPY requirements*.txt /tmp/ 2>/dev/null || true
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip wheel setuptools
RUN if compgen -G "/tmp/requirements*.txt" > /dev/null; then pip install -r /tmp/requirements*.txt; fi

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
ENV VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY . /app
RUN if [ -f requirements.txt ]; then pip install --upgrade pip wheel setuptools && pip install -r requirements.txt; fi
COPY docker/gunicorn.conf.py /app/gunicorn.conf.py
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENV FLASK_APP=app:create_app
CMD ["/entrypoint.sh", "gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
