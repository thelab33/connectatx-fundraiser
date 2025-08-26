#!/usr/bin/env bash
set -euo pipefail

# FundChamps Repo Audit — duplicates & overlaps finder
# Usage: bash audit_repo.sh [root_dir]
root="${1:-.}"

echo "==> Auditing repo at: $root"
echo ""

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

say() { printf "\n\033[1;33m### %s\033[0m\n" "$*"; }
p() { printf "%s\n" "$*"; }

# Helpers
grepcode() {
  if [ $have_rg -eq 1 ]; then
    rg --hidden --line-number --no-heading --color=never "$@" "$root" || true
  else
    grep -RIn --exclude-dir=".git" "$@" "$root" || true
  fi
}

findfiles() {
  # find files by name pattern (case insensitive where possible)
  if command -v fd >/dev/null 2>&1; then
    fd -H -I -t f "$1" "$root" || true
  else
    find "$root" -type f -iname "$1" 2>/dev/null || true
  fi
}

say "Python app entrypoints & configs"
findfiles "run.py"
findfiles "wsgi.py"
findfiles "config.py"
grepcode "class Config"
grepcode "SQLALCHEMY_DATABASE_URI"
grepcode "STRIPE_PUBLISHABLE_KEY|STRIPE_PAYMENT_LINK_URL|PAYPAL_DONATE_URL|TEAM_PAYMENT_LINKS_JSON|API_SECRET"

say "Flask app factory & DB init"
grepcode "def create_app"
grepcode "SQLAlchemy\\("
grepcode "^db\\s*=\\s*SQLAlchemy\\(\\)"

say "Blueprints"
grepcode "Blueprint\\("

say "Routes (decorators)"
grepcode "@(app\\.route|[A-Za-z_]+_bp\\.(get|post|put|delete|route))\\("

say "Potential duplicate endpoints"
grepcode "/api/impact-buckets"
grepcode "/api/payments/config"
grepcode "/donate"
grepcode "/sponsor"

say "Models duplicates (ImpactBucket, others)"
grepcode "class\\s+ImpactBucket\\b"
grepcode "__tablename__\\s*=\\s*[\"']impact_buckets[\"']"

say "Templates (looking for duplicates of base/index/partials)"
findfiles "base.html"
findfiles "index.html"
findfiles "donate.html"
findfiles "tiers.html"
findfiles "footer.html"
findfiles "header*.html"
findfiles "hero*.html"
findfiles "impact*locker*.html"
grepcode "{%\\s*include\\s*[\"']partials/impact_"

say "Static assets (hero/og images)"
findfiles "images/*hero*"
findfiles "images/*og*"

say ".env files & dotenvs"
findfiles ".env*"
grepcode "load_dotenv|dotenv_values"

say "Duplicate filenames by basename (helps spot shadows)"
# Print basenames that appear more than once
if command -v awk >/dev/null 2>&1; then
  find "$root" -type f -not -path "*/.git/*" -printf "%f\t%p\n" 2>/dev/null | awk -F'\t' '{count[$1]++; paths[$1]=paths[$1] ORS $2} END {for (k in count) if (count[k]>1) {print "DUP\t" k paths[k]}}' | sort || true
else
  p "(Install GNU findutils + awk to see basename duplicates)"
fi

echo ""
echo "==> Done. Review sections above for duplicates/overlaps."
