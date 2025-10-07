PY ?= python
PIP ?= pip

# Optional knobs
FLASK_HOST ?= 0.0.0.0
FLASK_PORT ?= 5000
FLASK_APP  ?= app:create_app

.PHONY: dev init db seed run lint test audit fmt verify verify-ribbon precommit ci clean freeze help

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
	FLASK_APP=$(FLASK_APP) FLASK_RUN_HOST=$(FLASK_HOST) FLASK_RUN_PORT=$(FLASK_PORT) flask run --debug

lint:
	ruff check app scripts tests
	bandit -q -r app || true

fmt:
	ruff check --fix app scripts tests || true

test:
	pytest -q

audit:
	$(PY) starforge_audit.py --config app.config.DevelopmentConfig || true

# ─────────────────────────────────────────────────────────────────────────────
# Structural guards: header ribbon & leaderboard rails + ID audit
# Fails the build if duplicates/invalid IDs are detected.
# ─────────────────────────────────────────────────────────────────────────────
verify:
	./scripts/check_ticker.sh
	./scripts/check_rail.sh
	@if [ -f audit_ids.py ]; then \
		$(PY) audit_ids.py > .id_audit_report.txt; \
		if grep -q "⚠" .id_audit_report.txt; then \
			echo "❌ ID audit failed"; exit 1; \
		else \
			echo "✅ ID audit passed"; \
		fi \
	else \
		echo "ℹ️ audit_ids.py not found — skipping ID audit"; \
	fi

# Run verify with the header ribbon enabled (expects one #hdr-ticker)
verify-ribbon:
	@EXPECTED_HDR_TICKER_COUNT=1 $(MAKE) verify

# Convenience: run your Husky pre-commit locally (same as a real commit)
precommit:
	./.husky/pre-commit

# Minimal CI pipeline (structural checks + lint + tests)
ci: verify lint test

# Ops helpers
clean:
	rm -f .id_audit_report.txt
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

freeze:
	$(PIP) freeze > requirements.txt

help:
	@echo "make dev            - install deps, init DB, seed, run dev server"
	@echo "make init           - install Python deps"
	@echo "make db             - create all tables"
	@echo "make seed           - seed demo data"
	@echo "make run            - start Flask dev server ($(FLASK_HOST):$(FLASK_PORT))"
	@echo "make lint           - ruff + bandit"
	@echo "make fmt            - ruff --fix"
	@echo "make test           - pytest"
	@echo "make audit          - starforge audit"
	@echo "make verify         - structural guards + ID audit"
	@echo "make verify-ribbon  - verify with EXPECTED_HDR_TICKER_COUNT=1"
	@echo "make precommit      - run Husky pre-commit hook manually"
	@echo "make ci             - verify + lint + test"
	@echo "make clean          - remove caches & report"
	@echo "make freeze         - pin requirements.txt"

