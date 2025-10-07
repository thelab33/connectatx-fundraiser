#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://localhost:5000}"

echo "↪ base: $BASE_URL"
python ci/smoke/wiring_smoketest.py || (echo "❌ wiring failed" && exit 1)

# Axe
npx -y @axe-core/cli "$BASE_URL" --exit 3 || (echo "❌ axe issues" && exit 1)

# Pa11y (AA)
npx -y pa11y "$BASE_URL" --standard WCAG2AA --threshold 3 || (echo "❌ pa11y issues" && exit 1)

# Lighthouse (perf+a11y+SEO)
npx -y lighthouse "$BASE_URL" \
  --only-categories=performance,accessibility,seo \
  --budgets-path=ci/lh/budgets.json \
  --chrome-flags="--headless --no-sandbox" \
  --quiet || (echo "❌ lighthouse issues" && exit 1)

echo "✅ Ship check passed"

