#!/usr/bin/env bash
# ===============================================================
#  FundChamps • Starforge build + deploy (robust edition)
# ===============================================================

set -euo pipefail
ROOT_DIR="$(pwd)"
VITE_ROOT="src"       # where index.html lives
OUT_DIR="dist"        # final build output
S3_BUCKET="s3://your-cdn-bucket"

echo "▶ Using Node 20 LTS …"
if ! command -v nvm &>/dev/null; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"
fi
nvm install 20 >/dev/null
nvm use 20      >/dev/null

echo "▶ Cleaning lock-file / modules …"
rm -rf node_modules package-lock.json "$OUT_DIR"
npm install --silent

echo "▶ Type-check & lint (non-blocking) …"
npm exec --silent -- eslint                   . || true
npm exec --silent -- prettier --check "**/*"  || true

echo "▶ Building with Vite …"
npm exec -- vite build \
  --config vite.config.js \
  --root "$VITE_ROOT" \
  --base "/" \
  --outDir "$OUT_DIR"

echo "▶ Extracting critical CSS …"
npm exec -- critters "$OUT_DIR/index.html" --public-path / --inline

echo "▶ Purging & minifying CSS …"
# Safelist ALL component scopes so dynamic / Jinja-generated classes survive
SAFELIST='/^hero__/','/^chip/','/^vip__/','/^btn--/','/^meter--spark$/'
npm exec -- purgecss \
  --css   "$OUT_DIR/assets/*.css" \
  --content "$OUT_DIR/**/*.html" \
  --safelist "$SAFELIST" \
  --output "$OUT_DIR/assets"

echo "▶ Running Lighthouse smoke (optional) …"
if command -v google-chrome &>/dev/null; then
  npx --yes http-server "$OUT_DIR" -p 5080 >/dev/null 2>&1 &
  SERVE_PID=$!
  npm exec -- lighthouse http://localhost:5080 --quiet \
    --preset=desktop -o html -o-path "$OUT_DIR/lh-report.html" \
    --chrome-flags="--headless" || true
  kill "$SERVE_PID"
fi

echo "▶ Generating CSP header …"
npm exec -- @dylanaung/csp-gen \
  "'self'" https://checkout.stripe.com https://www.paypal.com https://cdn.skypack.dev \
  > "$OUT_DIR/_csp.txt"

echo "▶ Syncing to $S3_BUCKET …"
AWS_PAGER="" aws s3 sync "$OUT_DIR" "$S3_BUCKET" \
  --acl public-read \
  --cache-control "max-age=31536000,immutable" \
  --delete

echo -e "\n✅ Build + deploy finished successfully!"
echo "   • Output: $OUT_DIR"
echo "   • CSP:    $OUT_DIR/_csp.txt"

