#!/usr/bin/env bash
# Forgemaster — Elite UI/UX auto-fix & audit for Flask + Tailwind + JS
# Usage:
#   ./forgemaster.sh fix      # format/lint/build CSS+JS
#   ./forgemaster.sh images   # optimize images (WebP/AVIF) to images/optimized
#   ./forgemaster.sh patch    # patch <img> tags in templates (lazy/decoding/alt, rewrite to optimized if present)
#   ./forgemaster.sh audit    # generate accessibility & perf reports if local server is running
#   ./forgemaster.sh all      # run everything
set -Eeuo pipefail

ROOT="$(pwd)"
TEMPLATES_DIR="${TEMPLATES_DIR:-app/templates}"
CSS_DIR="${CSS_DIR:-app/static/css}"
JS_DIR="${JS_DIR:-app/static/js}"
IMG_DIR="${IMG_DIR:-app/static/images}"
REPORTS_DIR="${REPORTS_DIR:-reports}"
NOW_TAG="$(date +%Y%m%d-%H%M%S)"

log() { printf "\033[1;32m[FORGE]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[FORGE]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[FORGE]\033[0m %s\n" "$*"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { err "Missing required command: $1"; exit 1; }
}

ensure_node_stack() {
  need_cmd npm
  need_cmd npx
  if [ ! -f package.json ]; then
    log "No package.json found — initializing…"
    npm init -y >/dev/null
  fi
  log "Installing/ensuring dev deps…"
  npm i -D \
    prettier prettier-plugin-tailwindcss \
    stylelint stylelint-config-standard stylelint-config-tailwindcss postcss postcss-cli cssnano \
    eslint eslint-plugin-tailwindcss @html-eslint/eslint-plugin @html-eslint/parser \
    html-validate \
    tailwindcss @tailwindcss/typography @tailwindcss/forms \
    purgecss @squoosh/cli \
    lighthouse pa11y >/dev/null
}

ensure_python_tools() {
  need_cmd python3
  if ! python3 -c "import djlint" 2>/dev/null; then
    log "Installing djlint…"
    pip install --quiet djlint
  fi
}

ensure_configs() {
  mkdir -p "$REPORTS_DIR" "$CSS_DIR" "$JS_DIR" "$IMG_DIR"

  # Prettier
  if [ ! -f .prettierrc ]; then
cat > .prettierrc <<'JSON'
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "printWidth": 100,
  "singleQuote": true
}
JSON
    log "Wrote .prettierrc"
  fi

  # Stylelint
  if [ ! -f .stylelintrc.cjs ]; then
cat > .stylelintrc.cjs <<'JS'
module.exports = {
  extends: ["stylelint-config-standard", "stylelint-config-tailwindcss"],
  overrides: [{ files: ["**/*.html"], customSyntax: "postcss-html" }],
  rules: {
    "color-function-notation": "legacy",
    "alpha-value-notation": "number"
  }
};
JS
    log "Wrote .stylelintrc.cjs"
  fi

  # PostCSS
  if [ ! -f postcss.config.cjs ]; then
cat > postcss.config.cjs <<'JS'
module.exports = { plugins: { autoprefixer: {}, cssnano: { preset: "default" } } };
JS
    log "Wrote postcss.config.cjs"
  fi

  # Tailwind config
  if [ ! -f tailwind.config.js ]; then
cat > tailwind.config.js <<'JS'
module.exports = {
  content: ["app/templates/**/*.html", "app/static/js/**/*.{js,mjs,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { 50:"#FFFBEB",100:"#FEF3C7",300:"#FCD34D",500:"#F59E0B",600:"#D97706",900:"#78350F" }
      },
      fontFamily: {
        display: ["Inter","ui-sans-serif","system-ui"],
        body: ["Inter","ui-sans-serif","system-ui"]
      }
    }
  },
  plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")]
};
JS
    log "Wrote tailwind.config.js"
  fi

  # Tailwind source CSS
  if [ ! -f "${CSS_DIR}/tailwind.css" ]; then
cat > "${CSS_DIR}/tailwind.css" <<'CSS'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* App-level tokens & tiny fixes */
:root { --ring: theme(colors.brand.500); }
.focus-ring { @apply focus-visible:outline-none focus-visible:ring-2 ring-offset-2 ring-brand-500; }
CSS
    log "Created ${CSS_DIR}/tailwind.css"
  fi
}

task_fix() {
  ensure_node_stack
  ensure_python_tools
  ensure_configs

  log "Prettier — format & Tailwind class sort"
  npx prettier -w "${TEMPLATES_DIR}/**/*.html" "${CSS_DIR}/**/*.css" "${JS_DIR}/**/*.{js,mjs,ts,tsx}"

  log "djlint — Jinja/HTML reformat + lint fix"
  djlint "${TEMPLATES_DIR}" --profile=jinja --reformat --lint --fix --preserve-blank-lines || true

  log "Stylelint — CSS & <style> blocks"
  npx stylelint "${CSS_DIR}/**/*.css" "${TEMPLATES_DIR}/**/*.html" --fix --custom-syntax postcss-html || true

  log "ESLint — JS auto-fix"
  # If no eslint config, use a sane default on-the-fly
  if [ ! -f .eslintrc.cjs ] && [ ! -f .eslintrc.json ]; then
cat > .eslintrc.cjs <<'JS'
module.exports = {
  env: { browser: true, es2022: true },
  parserOptions: { ecmaVersion: 2022, sourceType: "module" },
  plugins: ["tailwindcss"],
  extends: ["eslint:recommended"],
  rules: { "no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }] }
};
JS
    log "Wrote .eslintrc.cjs"
  fi
  npx eslint "${JS_DIR}/**/*.{js,mjs,ts,tsx}" --fix || true

  log "Tailwind — build & minify"
  npx tailwindcss -c tailwind.config.js -i "${CSS_DIR}/tailwind.css" -o "${CSS_DIR}/tw.build.css" --minify

  log "PostCSS — autoprefix + cssnano → app.min.css"
  npx postcss "${CSS_DIR}/tw.build.css" -u autoprefixer cssnano -o "${CSS_DIR}/app.min.css" --no-map

  log "PurgeCSS (report only) — unused selectors"
  npx purgecss \
    --css "${CSS_DIR}/app.min.css" \
    --content "${TEMPLATES_DIR}/**/*.html" "${JS_DIR}/**/*.{js,ts,tsx,mjs}" \
    --safelist "/(hx-|x-)/" \
    --rejected > "${REPORTS_DIR}/unused-css-${NOW_TAG}.txt" || true

  log "Fix: DONE → CSS to load in templates is ${CSS_DIR}/app.min.css"
}

task_images() {
  ensure_node_stack
  mkdir -p "${IMG_DIR}/optimized"
  log "Squoosh — optimizing images to ${IMG_DIR}/optimized"
  npx @squoosh/cli --webp auto --avif auto --oxipng auto -d "${IMG_DIR}/optimized" "${IMG_DIR}"/**/*.{png,jpg,jpeg} || true
  log "Images optimized."
}

task_patch() {
  ensure_python_tools
  log "Patching <img> tags in ${TEMPLATES_DIR} (lazy/decoding/alt, smart skip for above-the-fold)…"
  python3 - <<'PY'
import os, re, shutil, sys, time
ROOT = os.getcwd()
TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "app/templates")
IMG_DIR = os.environ.get("IMG_DIR", "app/static/images")
OPT_DIR = os.path.join(IMG_DIR, "optimized")
SKIP_CLASSES = ("no-lazy","hero","logo","avatar","above-the-fold","preload")
IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.MULTILINE)

def has_attr(tag, name):
    return re.search(rf'\b{name}\s*=\s*["\']', tag, re.IGNORECASE) is not None

def get_attr(tag, name):
    m = re.search(rf'\b{name}\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
    return m.group(1) if m else None

def set_or_add_attr(tag, name, value):
    if has_attr(tag, name):  # replace
        return re.sub(rf'(\b{name}\s*=\s*["\'])([^"\']*)(["\'])', rf'\1{value}\3', tag, flags=re.IGNORECASE)
    # insert before closing >
    return re.sub(r">\s*$", f' {name}="{value}">', tag)

def should_skip(tag):
    cls = get_attr(tag, "class") or ""
    cls_l = [c.strip().lower() for c in re.split(r"\s+", cls) if c.strip()]
    return any(k in cls_l for k in SKIP_CLASSES)

def rewrite_src_if_optimized(tag):
    src = get_attr(tag, "src")
    if not src or "static/images" not in src or "/optimized/" in src:
        return tag
    # Compute candidate in optimized dir
    base = src.split("/static/images/",1)[-1]
    candidate_dir = os.path.join(OPT_DIR, os.path.dirname(base))
    filename = os.path.basename(base)
    # Try same name (e.g., png → webp/avif) preference webp then avif then original
    name, ext = os.path.splitext(filename)
    for cand in (name + ".webp", name + ".avif", filename):
        cand_path = os.path.join(OPT_DIR, os.path.dirname(base), cand)
        if os.path.exists(cand_path):
            new_src = src.replace("/static/images/", "/static/images/optimized/").rsplit("/",1)[0] + "/" + cand
            return set_or_add_attr(tag, "src", new_src)
    return tag

files_changed = 0
tags_changed = 0
bak_tag = time.strftime("%Y%m%d-%H%M%S")

for root, _, files in os.walk(TEMPLATES_DIR):
    for fn in files:
        if not fn.endswith(".html"): continue
        path = os.path.join(root, fn)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        original = text
        def _transform(m):
            global tags_changed
            tag = m.group(0)
            if should_skip(tag):
                return tag
            t = tag
            if not has_attr(t, "loading"):
                t = set_or_add_attr(t, "loading", "lazy")
            if not has_attr(t, "decoding"):
                t = set_or_add_attr(t, "decoding", "async")
            if not has_attr(t, "alt"):
                t = set_or_add_attr(t, "alt", "")
                t = set_or_add_attr(t, "data-alt-todo", "true")
            t = rewrite_src_if_optimized(t)
            if t != tag:
                tags_changed += 1
            return t
        text = IMG_TAG.sub(_transform, text)
        if text != original:
            shutil.copy2(path, f"{path}.{bak_tag}.bak")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            files_changed += 1

print(f"✅ Patched files: {files_changed}, <img> tags updated: {tags_changed}")
print("ℹ️  Skip keywords for above-the-fold: class='no-lazy|hero|logo|avatar|above-the-fold|preload'")
print("ℹ️  If optimized images exist, src was rewritten to /static/images/optimized/…")
PY
}

is_port_open() {
  curl -sSf "http://localhost:5000" >/dev/null 2>&1
}

task_audit() {
  ensure_node_stack
  mkdir -p "$REPORTS_DIR"
  if is_port_open; then
    log "pa11y — accessibility HTML report"
    npx pa11y http://localhost:5000 --reporter html --threshold 0 > "${REPORTS_DIR}/pa11y-${NOW_TAG}.html" || true

    log "Lighthouse — perf/SEO/best-practices"
    npx lighthouse http://localhost:5000 \
      --only-categories=performance,accessibility,best-practices,seo \
      --output html --output-path "${REPORTS_DIR}/lighthouse-${NOW_TAG}.html" >/dev/null || true
  else
    warn "Local server not reachable at http://localhost:5000 — skipping pa11y/lighthouse. Start Flask and re-run './forgemaster.sh audit'."
  fi
  log "Audit reports saved in ${REPORTS_DIR}/"
}

case "${1:-all}" in
  fix)    task_fix ;;
  images) task_images ;;
  patch)  task_patch ;;
  audit)  task_audit ;;
  all)
    task_fix
    task_images
    task_patch
    task_audit
    ;;
  *)
    err "Unknown command: ${1}. Use fix|images|patch|audit|all"
    exit 1
    ;;
esac

log "Done."

