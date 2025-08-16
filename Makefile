PY?=python
PIP?=pip

.PHONY: dev init db seed run lint test audit fmt

dev: init db seed run

init:
	$(PIP) install -U pip wheel
	$(PIP) install -r requirements.txt

db:
	$(PY) -c "from app import create_app; from app.extensions import db; a=create_app(); \
from app.models import *; \
with a.app_context(): db.create_all()"

seed:
	$(PY) scripts/seed_demo.py

run:
	FLASK_APP=app:create_app FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5000 flask run --debug

lint:
	ruff check app scripts tests
	bandit -q -r app || true

fmt:
	ruff check --fix app scripts tests || true

test:
	pytest -q

audit:
	$(PY) starforge_audit.py --config app.config.DevelopmentConfig || true

