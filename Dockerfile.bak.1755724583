# ───── Starforge Champion Dockerfile ─────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create a non-root user (security best practice)
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port for Gunicorn
EXPOSE 8000

CMD ["gunicorn", "-k", "eventlet", "-b", "0.0.0.0:8000", "--workers=1", "run:app"]
