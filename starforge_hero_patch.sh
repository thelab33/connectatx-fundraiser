#!/usr/bin/env bash
set -euo pipefail

echo "╭──────────────────────────────────────────────╮"
echo "│  🌄 Starforge Hero Patch — SV Elite Hero     │"
echo "╰──────────────────────────────────────────────╯"

BASE=${BASE:-app/templates/home.html}
TS=$(date +%Y%m%d-%H%M%S)

# Auto-detect if BASE not provided
if [ ! -f "$BASE" ]; then
  BASE=$(grep -RIl --exclude="*.bak*" --include="*.html" "FC:HERO_SV_ELITE" app/templates | head -1 || true)
fi
[ -z "$BASE" ] && { echo "❌ Could not locate hero template"; exit 1; }

echo "→ Target hero template: $BASE"
cp "$BASE" "$BASE.bak.$TS"

awk -v block="$(cat <<'JINJA'
<!-- FC:HERO_SV_ELITE — contained bg + live fundraising meter -->
{% include "partials/ui_bootstrap.html" ignore missing with context %}

{% set NONCE     = NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') %}
{% set team_name = (team.team_name if team and team.team_name is defined else 'Connect ATX Elite') %}
{% set theme_hex = (team.theme_color if team and team.theme_color else '#f59e0b') %}

{% set funds_raised     = (funds_raised if funds_raised is defined else 0) | float %}
{% set fundraising_goal = (fundraising_goal if fundraising_goal is defined and fundraising_goal else 10000) | float %}
{% set fundraiser_deadline = (fundraiser_deadline if fundraiser_deadline is defined else none) %}
{% set pct = (100 * funds_raised / fundraising_goal) | round(1) if fundraising_goal > 0 else 0 %}

<section id="fc-hero"
         class="relative overflow-clip min-h-[82vh] sm:min-h-[88vh]"
         aria-labelledby="fc-hero-title"
         style="--fc-hero-accent: {{ theme_hex }};">
  <!-- Background -->
  <div class="absolute inset-0">
    <picture>
      {% if hero_bg_avif %}<source srcset="{{ hero_bg_avif }}" type="image/avif" sizes="100vw">{% endif %}
      {% if hero_bg_webp %}<source srcset="{{ hero_bg_webp }}" type="image/webp" sizes="100vw">{% endif %}
      <img id="fc-hero-img"
           src="{{ hero_bg }}"
           alt="{{ team_name }} team photo"
           width="1920" height="1080"
           class="h-full w-full object-cover"
           style="object-position: {{ hero_focus }};"
           loading="eager" decoding="async" fetchpriority="high" sizes="100vw">
    </picture>
    <div class="absolute inset-0 bg-black/60"></div>
  </div>

  <!-- Content -->
  <div class="relative z-10 flex flex-col items-center justify-center text-center px-6 py-20 sm:py-32">
    <h1 id="fc-hero-title" class="text-4xl sm:text-6xl font-extrabold text-white drop-shadow">
      {{ team_name }} — Fundraiser
    </h1>
    <p class="mt-4 text-lg sm:text-xl max-w-2xl text-gray-200">
      Back our journey — every sponsor fuels the championship run.
    </p>

    <!-- Live Fundraiser Meter -->
    <div class="mt-8 w-full max-w-2xl">
      {% include "partials/fundraiser_meter.html" with context %}
    </div>

    {% if fundraiser_deadline %}
      <p class="mt-6 text-sm text-gray-300">
        Campaign ends on {{ fundraiser_deadline.strftime("%B %d, %Y") }}
      </p>
    {% endif %}
  </div>
</section>
JINJA
)" '
/FC:HERO_SV_ELITE/ {print block; skip=1; next}
/<\/section>/ && skip {skip=0; next}
!skip {print}
' "$BASE" > "$BASE.tmp" && mv "$BASE.tmp" "$BASE"

echo "✅ Hero block patched into: $BASE"

