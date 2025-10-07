# scripts/upscale.sh
#!/usr/bin/env bash
set -euo pipefail

# ---------- tiny helpers ----------
blue()  { printf "\033[1;34m%s\033[0m\n" "$*"; }
green() { printf "\033[1;32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[1;33m%s\033[0m\n" "$*"; }
red()   { printf "\033[1;31m%s\033[0m\n" "$*"; }

step()  { blue "$*"; }
ok()    { green "$*"; }
warn()  { yellow "$*"; }
fail()  { red "$*"; }

node_major() { node -p "process.versions.node.split('.')[0]"; }

have_local() {
  # usage: have_local <binName>
  [ -x "node_modules/.bin/$1" ]
}

run_local() {
  # usage: run_local <binName> [args...]
  "node_modules/.bin/$1" "${@:2}"
}

# ---------- repo paths ----------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC="$ROOT/app/static"
CSS_DIR="$STATIC/css"
IMG_DIR="$STATIC/images"
TPL_DIR="$ROOT/app/templates"
BASE_HTML="$TPL_DIR/base.html"
SITEMAP_OUT="$STATIC/sitemap.xml"

SITE_URL="${SITE_URL:-http://localhost:8080}"

echo
blue "🔧 Upscale started @ $(date)"
echo "ROOT=$ROOT"
echo "SITE_URL=$SITE_URL"
echo

mkdir -p "$CSS_DIR/min" "$CSS_DIR/purged" "$IMG_DIR/optimized" "$STATIC"

# 1) Minify CSS
step "1) Minifying CSS → css/min"
if have_local lightningcss; then
  for css in "$CSS_DIR"/*.css; do
    [ -f "$css" ] || continue
    base="$(basename "$css" .css)"
    run_local lightningcss "$css" -m --minify -o "$CSS_DIR/min/$base.min.css" || true
  done
  ok "✓ CSS minified (lightningcss)"
else
  if have_local postcss; then
    run_local postcss "$CSS_DIR/input.css" -o "$CSS_DIR/min/app.min.css" || true
    ok "✓ CSS minified with postcss+cssnano"
  else
    warn "• Skipping minify (no lightningcss/postcss)"
  fi
fi

# 2) Purge unused CSS
step "2) Purging unused CSS (purgecss) → css/purged"
if have_local purgecss; then
  run_local purgecss \
    --content "$TPL_DIR/**/*.html" "$TPL_DIR/**/*.jinja" \
    --css "$CSS_DIR/*.css" "$CSS_DIR/min/*.css" \
    --safelist "/is-|has-/" \
    -o "$CSS_DIR/purged" || true
  ok "✓ Purge complete"
else
  warn "• Skipping purge (purgecss not found)"
fi

# 3) SVGO (only if there are svgs)
step "3) Optimizing SVGs (svgo)"
if have_local svgo; then
  if find "$IMG_DIR" -type f -name '*.svg' | read; then
    run_local svgo -f "$IMG_DIR" --multipass || true
    ok "✓ SVGs optimized"
  else
    warn "• No SVGs found; skipping"
  fi
else
  warn "• Skipping SVG optimize (svgo not found)"
fi

# 4) Images → AVIF/WebP
step "4) Converting JPG/PNG → AVIF/WebP (optional)"
OUT_OPT="$IMG_DIR/optimized"
mkdir -p "$OUT_OPT"
if have_local squoosh-cli && [ "$(node_major)" -lt 20 ]; then
  find "$IMG_DIR" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 \
    | xargs -0 -I{} "node_modules/.bin/squoosh-cli" --force --avif --webp -d "$OUT_OPT" "{}" || true
  ok "✓ Images converted with @squoosh/cli"
elif [ -f "$ROOT/scripts/img-optimize.mjs" ]; then
  node "$ROOT/scripts/img-optimize.mjs" "$IMG_DIR" "$OUT_OPT" || true
  ok "✓ Images converted with sharp"
else
  warn "• Skipping image conversion (no squoosh on Node ≥20; sharp script not present)"
fi

# 5) Favicons / manifest (optional)
step "5) Generating favicons + manifest (optional)"
if have_local pwa-asset-generator; then
  mkdir -p "$STATIC/favicons"
  SRC_IMG="${FAVICON_SRC:-$IMG_DIR/logo.webp}"
  [ -f "$SRC_IMG" ] && run_local pwa-asset-generator "$SRC_IMG" "$STATIC/favicons" \
    -m "$STATIC/favicons/manifest.json" --favicon --padding "10%" --opaque false || true
  ok "✓ Favicons/manifest attempted"
else
  warn "• Skipping favicon generation (pwa-asset-generator not found)"
fi

# 6) Critical CSS (optional)
step "6) Inlining Critical CSS (optional)"
if have_local critical; then
  for page in "$TPL_DIR/index.html" "$TPL_DIR/fundraiser.html" "$TPL_DIR/donate.html" "$TPL_DIR/sponsor.html"; do
    [ -f "$page" ] || continue
    run_local critical --html "$page" --inline --base "$ROOT" --width 1366 --height 900 --extract || true
  done
  ok "✓ Critical inlined (best-effort)"
else
  warn "• Skipping critical (critical not found)"
fi

# 7) Precompress
step "7) Brotli + gzip precompression"
if command -v brotli >/dev/null 2>&1; then
  find "$STATIC" -type f \( -name '*.css' -o -name '*.js' -o -name '*.svg' -o -name '*.json' -o -name '*.xml' -o -name '*.txt' -o -name '*.woff2' \) -print0 \
    | xargs -0 -I{} sh -c 'brotli -f -Z "{}" 2>/dev/null || true; gzip -f -9 "{}" 2>/dev/null || true'
  ok "✓ Precompressed assets"
else
  warn "• Skipping brotli (not installed)"
fi

# 8) Service worker
step "8) Generating service worker (workbox)"
if have_local workbox; then
  run_local workbox generateSW workbox.config.cjs || true
  ok "✓ Service worker generated"
else
  warn "• Skipping service worker (workbox-cli not found)"
fi

# 9) Sitemap
step "9) Generating sitemap.xml"
if have_local sitemap-generator; then
  run_local sitemap-generator "$SITE_URL" --filepath "$SITEMAP_OUT" --strip-querystring || true
  ok "✓ Sitemap (cli) → $SITEMAP_OUT"
else
  # fallback to local script if present
  if [ -f "$ROOT/scripts/gen-sitemap.mjs" ]; then
    node "$ROOT/scripts/gen-sitemap.mjs" "$SITE_URL" "$SITEMAP_OUT" || true
    ok "✓ Sitemap (fallback) → $SITEMAP_OUT"
  else
    warn "• Skipping sitemap (no CLI and no fallback script)"
  fi
fi

# 10) Perf hints
step "10) Injecting preconnect/preload hints into base.html (idempotent)"
HINT_BLOCK='<!-- perf hints (auto) -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/static/ux/fonts/Inter-Variable.woff2" crossorigin>'
if [ -f "$BASE_HTML" ] && ! grep -q "perf hints (auto)" "$BASE_HTML"; then
  cp "$BASE_HTML" "$BASE_HTML.bak-$(date +%Y%m%d-%H%M%S)"
  awk -v block="$HINT_BLOCK" '
    BEGIN{done=0}
    /<head[^>]*>/ && !done { print; print block; done=1; next }
    { print }
  ' "$BASE_HTML" > "$BASE_HTML.tmp" && mv "$BASE_HTML.tmp" "$BASE_HTML"
  ok "✓ Perf hints injected"
else
  warn "• Perf hints already present or base.html missing; skipping"
fi

echo
ok "✅ Upscale finished."
echo " • Minified CSS:       $CSS_DIR/min"
echo " • Purged CSS:         $CSS_DIR/purged"
echo " • Optimized images:   $IMG_DIR/optimized"
echo " • Favicons/manifest:  $STATIC/favicons"
echo " • Service worker:     $STATIC/sw.js"
echo " • Sitemap:            $STATIC/sitemap.xml"
echo " • base.html updated:  perf preconnect/preload hints"
