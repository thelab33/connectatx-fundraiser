#!/usr/bin/env bash
set -euo pipefail
F=app/templates/partials/header_sponsor_ticker.html
mkdir -p "$(dirname "$F")"
cp "$F" "$F.$(date +%F-%H%M).bak" 2>/dev/null || true
cat > "$F" <<'HTML'
{# ===========================================================
   FundChamps — Header Sponsor Ticker (Elite)
   - Seamless looping ribbon (pause on hover/focus)
   - Save-Data + reduced-motion aware
   - Optional fetch refresh (hx optional)
   =========================================================== #}

{% set brand_color   = (team.theme_color if team and team.theme_color else '#facc15') %}
{% set asset_version = asset_version|default(None) %}

{# expects: sponsors (list of { name, logo, url }) #}
{% set items = sponsors if sponsors is defined and sponsors else [] %}
{% if items|length == 0 %}
  {% set items = [
    {"name":"ESPN","logo":"https://upload.wikimedia.org/wikipedia/commons/2/2f/ESPN_wordmark.svg","url":"https://espn.com"},
    {"name":"NIKE","logo":"https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg","url":"https://nike.com"}
  ] %}
{% endif %}

<div id="sponsor-ticker"
     class="relative z-40 w-full border-y"
     style="border-color: color-mix(in srgb, {{ brand_color }} 20%, transparent)"
     role="region" aria-label="Sponsor ticker">
  <style>
    #sponsor-ticker{background:rgba(0,0,0,.6);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
    #sponsor-ticker .rail{display:flex;gap:2rem;align-items:center;white-space:nowrap;will-change:transform}
    #sponsor-ticker .logo{height:22px;width:auto;background:#fff;padding:.25rem .5rem;border-radius:.5rem;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}
    @keyframes st-marquee { from{ transform: translateX(0) } to{ transform: translateX(-50%) } }
    #sponsor-ticker .marquee{display:flex;gap:2rem;animation: st-marquee 22s linear infinite}
    #sponsor-ticker:hover .marquee, #sponsor-ticker:focus-within .marquee{animation-play-state:paused}
    @media (prefers-reduced-motion:reduce){ #sponsor-ticker .marquee{animation:none} }
    .save-data #sponsor-ticker .marquee{animation:none}
  </style>

  <div class="overflow-hidden py-1.5">
    <div class="rail marquee" data-rail aria-live="polite" aria-atomic="true">
      {% for s in items %}
        <a href="{{ s.url or '#' }}" class="inline-flex items-center gap-2" target="_blank" rel="noopener sponsored" aria-label="{{ s.name }}">
          <img class="logo" src="{{ s.logo or (url_for('static','images/logo.webp',v=asset_version) if asset_version else url_for('static','images/logo.webp')) }}" alt="{{ s.name }} logo" loading="lazy" decoding="async" />
          <span class="text-[11px] text-yellow-100/90">{{ s.name }}</span>
        </a>
      {% endfor %}
      {# duplicate for seamless loop #}
      {% for s in items %}
        <a href="{{ s.url or '#' }}" class="inline-flex items-center gap-2" target="_blank" rel="noopener sponsored" aria-label="{{ s.name }}">
          <img class="logo" src="{{ s.logo or (url_for('static','images/logo.webp',v=asset_version) if asset_version else url_for('static','images/logo.webp')) }}" alt="{{ s.name }} logo" loading="lazy" decoding="async" />
          <span class="text-[11px] text-yellow-100/90">{{ s.name }}</span>
        </a>
      {% endfor %}
    </div>
  </div>
</div>

<script nonce="{{ csp_nonce() if csp_nonce is defined else '' }}">
(() => {
  const root = document.getElementById('sponsor-ticker'); if (!root || root.__init) return; root.__init = true;

  // Save-Data flag from documentElement if present
  if (navigator.connection?.saveData) document.documentElement.classList.add('save-data');

  // Defensive: remove exact duplicate anchor+src combos in the first half
  const rail = root.querySelector('[data-rail]');
  if (rail){
    const seen = new Set();
    Array.from(rail.children).slice(0, Math.floor(rail.children.length/2)).forEach(a=>{
      const key = (a.querySelector('img')?.src || '') + '|' + (a.getAttribute('href')||'#');
      if (seen.has(key)) a.remove(); else seen.add(key);
    });
  }
})();
</script>
HTML
echo "✅ Wrote $F"
