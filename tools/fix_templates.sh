#!/usr/bin/env bash
set -euo pipefail
# tools/fix_templates.sh
# Safe, idempotent fixes for template escaping and hero partial placement.
# Run from repo root: ./tools/fix_templates.sh
#
# Creates backups of altered files as <file>.bak.<timestamp>

TS=$(date +"%Y%m%dT%H%M%S")
ROOT="$(pwd)"
TEMPLATES_DIR="${ROOT}/app/templates"
PARTIALS_DIR="${TEMPLATES_DIR}/partials"
BACKUP_SUFFIX=".bak.${TS}"
PATCHED_HERO_SRC="$(mktemp -t hero_classic.XXXXXX.html)"

echo "Running template fixes (ts=${TS})"
echo "Repo root: ${ROOT}"
echo "Templates dir: ${TEMPLATES_DIR}"
echo

# Ensure partials dir exists
mkdir -p "${PARTIALS_DIR}"

backup_file() {
  local f="$1"
  if [ -f "$f" ]; then
    cp -a "$f" "${f}${BACKUP_SUFFIX}"
    echo "Backed up $f -> ${f}${BACKUP_SUFFIX}"
  fi
}

# 1) Ensure _core_helpers.html contains nonce_attr() macro
CORE_HELPERS="${PARTIALS_DIR}/_core_helpers.html"
if [ ! -f "${CORE_HELPERS}" ]; then
  echo "Creating ${CORE_HELPERS} (was missing) with nonce_attr macro..."
  cat > "${CORE_HELPERS}" <<'EOF'
{# core helpers used across partials - idempotent macro for CSP nonce #}
{% set NONCE = (NONCE if NONCE is defined and NONCE else (csp_nonce if csp_nonce is defined else '')) %}
{% macro nonce_attr(n=NONCE) -%}{% if n %}nonce="{{ n }}"{% endif %}{%- endmacro %}
EOF
  echo "Wrote ${CORE_HELPERS}"
else
  # backup then ensure macro exists (append if not)
  backup_file "${CORE_HELPERS}"
  if ! grep -q "macro nonce_attr" "${CORE_HELPERS}"; then
    echo "Appending nonce_attr macro to ${CORE_HELPERS}..."
    cat >> "${CORE_HELPERS}" <<'EOF'

{# Ensure nonce_attr exists (appended by fix script) #}
{% if False %}{% endif %} {# no-op to ensure valid Jinja context #}
{% macro nonce_attr(n=(NONCE if (NONCE is defined and NONCE) else (csp_nonce if (csp_nonce is defined) else ''))) -%}{% if n %}nonce="{{ n }}"{% endif %}{%- endmacro %}
EOF
  else
    echo "${CORE_HELPERS} already contains nonce_attr() — leaving intact."
  fi
fi

echo

# 2) Replace problematic "|e('js')" usages across templates -> "|tojson"
#    and convert common onerror fallback patterns to use tojson.
# We'll operate only inside app/templates to be safe.

echo "Searching for occurrences of |e('js') and replacing with |tojson..."
FOUND_EJS=$(grep -R --line-number --color=never "|e('js')" "${TEMPLATES_DIR}" || true)
if [ -n "$FOUND_EJS" ]; then
  echo "Found occurrences; backing up files and replacing."
  echo "$FOUND_EJS"
  # For each file with the pattern, perform in-place replacement (with backup).
  echo "$FOUND_EJS" | cut -d: -f1 | sort -u | while read -r f; do
    backup_file "$f"
    # Replace exactly |e('js') with |tojson
    perl -0777 -pe "s/\\|e\\('js'\\)/\\|tojson/gs" -i "$f"
    echo "Patched $f"
  done
else
  echo "No |e('js') occurrences found."
fi

echo

# 3) Fix common onerror fallback patterns that attempted to inject Jinja-escaped JS strings
#    Example: onerror="this.onerror=null;this.src='{{ (team.hero_fallback or '/static/images/team-default.jpg')|e('js') }}';"
#    -> onerror="this.onerror=null;this.src={{ (team.hero_fallback or '/static/images/team-default.jpg')|tojson }};"
#
# We'll search for onerror occurrences that contain |e('js') or similar and convert them.

echo "Normalizing <img onerror=...> fallbacks to use |tojson (safe quoting)..."
IMG_ONERROR_FILES=$(grep -R --line-number --color=never "onerror=.*|e('js')" "${TEMPLATES_DIR}" || true)
if [ -n "$IMG_ONERROR_FILES" ]; then
  echo "$IMG_ONERROR_FILES"
  echo "$IMG_ONERROR_FILES" | cut -d: -f1 | sort -u | while read -r f; do
    backup_file "$f"
    # Convert the pattern: this.src='{{ ... |e('js') }}';
    # to: this.src={{ ... |tojson }};
    # Use Perl to handle quoting robustly.
    perl -0777 -pe \
    "s/onerror\\s*=\\s*([\"'])\\s*this\\.onerror\\s*=\\s*null;\\s*this\\.src\\s*=\\s*'\\s*\\{\\{\\s*(.*?)\\s*\\|e\\('js'\\)\\s*\\}\\}\\s*'\\s*;?\\s*\\1/onerror=\\\"this.onerror=null;this.src={{ \$2 | tojson }};\\\"/gis" \
    -i "$f" || true

    # If any remaining |e('js') inside onerror attributes, replace generically
    perl -0777 -pe "s/\\{\\{\\s*(.*?)\\s*\\|e\\('js'\\)\\s*\\}\\}/{{ \$1|tojson }}/gs" -i "$f" || true

    echo "Normalized image onerror in $f"
  done
else
  echo "No image onerror patterns with |e('js') found."
fi

echo

# 4) Place/overwrite polished hero_classic.html into partials directory (backup first)
HERO_TARGET="${PARTIALS_DIR}/hero_classic.html"
echo "Installing polished hero partial to ${HERO_TARGET} (backup if exists)."
backup_file "${HERO_TARGET}"

cat > "${PATCHED_HERO_SRC}" <<'HERODATA'
{# Polished hero_classic.html — production-ready, CSP-safe, accessible hero partial #}
{% import 'partials/_core_helpers.html' as core %}
{% set TEAM_NAME  = team.name or team.team_name or 'Connect ATX Elite' %}
{% set ACCENT     = (team.theme_hex if team is defined and team.theme_hex else '#facc15') %}
{% set DONATE_URL = DONATE_URL if (DONATE_URL is defined and DONATE_URL) else (stripe_payment_link if stripe_payment_link is defined else (safe_url_for('main.donate') if (safe_url_for is defined and has_endpoint is defined and has_endpoint('main.donate')) else '/donate')) %}

<section class="fcx-hero fcx-hero--patched" style="--accent: {{ (ACCENT)|e }};" data-scrim="normal" role="region" aria-label="{{ TEAM_NAME|e }} fundraiser hero" data-team="{{ TEAM_NAME|e }}">
  <div class="fcx-hero__inner">
    <div class="fcx-hero__grid">
      <!-- HERO (left) -->
      <header class="fcx-hero__left" aria-hidden="false">
        <figure class="fcx-hero__media" role="group" aria-label="{{ TEAM_NAME|e }} hero">
          <div class="fcx-hero__frame" aria-hidden="true"></div>

          <picture class="fcx-lqip" aria-hidden="false">
            <source type="image/avif" srcset="{{ team.hero_avif or '/static/images/team.avif' }}">
            <source type="image/webp" srcset="{{ team.hero_webp or '/static/images/team.webp' }}">
            <img src="{{ team.hero_jpg or '/static/images/team.jpg' }}"
            alt="{{ TEAM_NAME|e }} team photo"
            class="fcx-hero__img"
            decoding="async"
            fetchpriority="high"
            sizes="(max-width: 950px) 100vw, 60vw"
            loading="eager"
            onerror="this.onerror=null;this.src={{ (team.hero_fallback or '/static/images/connect-atx-team.jpg')|tojson }};"
            data-fallback="{{ (team.hero_fallback or '/static/images/connect-atx-team.jpg')|e }}"
            />

          </picture>

          <div class="fcx-hero__ph"><div class="fcx-shimmer" aria-hidden="true"></div></div>

          <figcaption class="fcx-hero__overlay fcx-hero__overlay--centered flow">
            <span class="fcx-chip" aria-hidden="true">{{ TEAM_NAME|e }}</span>
            <h1 class="fcx-tagline">
              <span>Fuel the Season.</span>
              <span class="fcx-accent">Fund the Future.</span>
            </h1>
            <p class="fcx-sub">{{ SUBTITLE|default('Direct support for gear, travel, and tutoring—every dollar moves a kid forward.') }}</p>

            <ul class="fcx-kpis" role="list" aria-label="Team statistics">
              <li role="listitem"><span class="fcx-kpi-val"><b>{{ team.games_played or 35 }}</b></span><span class="fcx-kpi-label">Games Played</span></li>
              <li role="listitem"><span class="fcx-kpi-val"><b>{{ team.championships or 5 }}</b></span><span class="fcx-kpi-label">Championships</span></li>
              <li role="listitem"><span class="fcx-kpi-val"><b>{{ team.training_hours or 120 }}+</b></span><span class="fcx-kpi-label">Training Hours / Week</span></li>
            </ul>

            <nav class="fcx-cta" aria-label="Primary actions">
              <a href="#tiers" class="fcx-btn fcx-btn-ghost">🏀 Back Our Ballers</a>
              <a href="{{ DONATE_URL }}" class="fcx-btn fcx-btn-accent pulse" target="_blank" rel="noopener noreferrer">⛹️ Fuel the Season</a>
            </nav>

            <div class="fcx-hero-trust" aria-hidden="false">
              <span class="fcx-tax-badge">100% TAX DEDUCTIBLE</span>
              <span class="fcx-secure-badge">SECURE VIA STRIPE / PAYPAL</span>
            </div>

            <div class="fcx-qr fcx-qr--hero" aria-hidden="true">
              <img src="/static/images/qr.png" alt="Donate QR code" width="98" height="98" loading="lazy" />
              <div class="fcx-qr-cap"><strong>Scan to give</strong> — or press <kbd>D</kbd></div>
            </div>
          </figcaption>
        </figure>
      </header>
      <!-- Scoreboard panel will be included separately by index.html if enabled -->
    </div>
  </div>
</section>
HERODATA

# Move polished hero into partials (overwrite after backup)
mv "${PATCHED_HERO_SRC}" "${HERO_TARGET}"
echo "Installed polished hero partial -> ${HERO_TARGET}"

echo

# 5) Sanity: replace any remaining "|e('js')" in templates (catch-alls)
echo "Final pass: replace any leftover |e('js') with |tojson ..."
grep -R --line-number --color=never "|e('js')" "${TEMPLATES_DIR}" || true
# perform replacement globally (with backups)
for f in $(grep -R --line-number --color=never "|e('js')" "${TEMPLATES_DIR}" 2>/dev/null | cut -d: -f1 | sort -u); do
  backup_file "$f"
  perl -0777 -pe "s/\\|e\\('js'\\)/\\|tojson/gs" -i "$f"
  echo "Patched (final) $f"
done

echo

# 6) Report changed files and lines for review
echo "Summary of touched files (recent backups shown):"
ls -1 "${TEMPLATES_DIR}"/*.bak.* 2>/dev/null || true
ls -1 "${PARTIALS_DIR}"/*.bak.* 2>/dev/null || true

echo
echo "Quick grep preview for 'tojson' or onerror fallbacks in templates:"
grep -R --line-number --color=never "|tojson" "${TEMPLATES_DIR}" || true
grep -R --line-number --color=never "onerror=.*tojson" "${TEMPLATES_DIR}" || true

echo
echo "DONE. Suggested next steps:"
echo "  1) Inspect backups: ls -l app/templates/*.bak.* app/templates/partials/*.bak.*"
echo "  2) Start dev server and test rendering: flask run (or your usual dev command)"
echo "  3) Run local smoke test: pytest -q tests/test_hero_template.py  (if you have pytest/jinja2 installed)"
echo "  4) Manually test the hero image fallback by renaming hero image and ensuring onerror fallback fires."
echo
echo "If anything looks off, paste the output here (or the template snippet) and I'll iterate."

