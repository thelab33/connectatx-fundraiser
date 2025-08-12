#!/usr/bin/env bash
set -euo pipefail
F=app/templates/partials/sponsor_wall_widget.html
mkdir -p "$(dirname "$F")"
cp "$F" "$F.$(date +%F-%H%M).bak" 2>/dev/null || true
cat > "$F" <<'HTML'
{# =========================================
   FundChamps — Sponsor Wall (Elite, SaaS-ready)
   - Safe fallbacks + demo seed
   - Tier filters (chips)
   - Accessible, CSP-safe, scoped styles/JS
   ========================================= #}

{% set team_name     = team.team_name if team and team.team_name else 'Connect ATX Elite' %}
{% set brand_color   = (team.theme_color if team and team.theme_color else '#facc15') %}
{% set asset_version = asset_version|default(None) %}

{# Expected list of dicts: name, logo, url, amount, tier #}
{% set _src = sponsors if sponsors is defined else [] %}
{% set sponsors_list = _src if _src else [] %}

{# Demo seed if empty #}
{% if sponsors_list|length == 0 %}
  {% set sponsors_list = [
    {"name":"ESPN","logo":"https://upload.wikimedia.org/wikipedia/commons/2/2f/ESPN_wordmark.svg","url":"https://espn.com","amount":5000,"tier":"Platinum"},
    {"name":"H-E-B","logo":"https://upload.wikimedia.org/wikipedia/commons/2/2f/HEB_logo.svg","url":"https://heb.com","amount":2500,"tier":"Gold"},
    {"name":"NIKE","logo":"https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg","url":"https://nike.com","amount":1500,"tier":"Silver"}
  ] %}
{% endif %}

{# Tier set #}
{% set tiers = ['Platinum','Gold','Silver','Bronze','Community'] %}
{% set norm = lambda s: (s or '')|string %}

<section id="sponsor-wall" class="mx-auto w-full max-w-6xl px-4 md:px-6" role="region" aria-labelledby="sponsor-wall-heading">
  <style>
    #sponsor-wall .chips button{border:1px solid color-mix(in srgb, {{ brand_color }} 35%, transparent);background:color-mix(in srgb, {{ brand_color }} 12%, transparent);padding:.35rem .7rem;border-radius:9999px;font-weight:700}
    #sponsor-wall .chips button[aria-pressed="true"]{background:color-mix(in srgb, {{ brand_color }} 60%, #fff); color:#111}
    #sponsor-wall .card{background:rgba(15,15,15,.72);border:1px solid color-mix(in srgb, {{ brand_color }} 18%, transparent);border-radius:1rem;box-shadow:0 10px 36px rgba(250,204,21,.12)}
    #sponsor-wall .logo{height:36px;width:auto;background:#fff;padding:.35rem .6rem;border-radius:.5rem;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}
    #sponsor-wall .badge{border:1px solid color-mix(in srgb, {{ brand_color }} 35%, transparent);background:color-mix(in srgb, {{ brand_color }} 12%, transparent)}
    @media (prefers-reduced-motion:reduce){ #sponsor-wall .fade{transition:none!important} }
  </style>

  <h2 id="sponsor-wall-heading" class="text-center text-xl font-black text-yellow-300 mb-3">Our Sponsors</h2>

  <!-- Filters -->
  <nav class="chips mb-4 flex flex-wrap items-center justify-center gap-2" role="toolbar" aria-label="Filter sponsors by tier">
    <button type="button" class="fade" data-tier="all" aria-pressed="true">All</button>
    {% for t in tiers %}<button type="button" class="fade" data-tier="{{ t }}" aria-pressed="false">{{ t }}</button>{% endfor %}
  </nav>

  <!-- Grid -->
  <ul class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-5" role="list" aria-live="polite" aria-atomic="true">
    {% for s in sponsors_list|sort(attribute='amount', reverse=True) %}
      <li class="card p-4 flex flex-col gap-3" data-tier="{{ s.tier or 'Community' }}">
        <div class="flex items-center gap-3">
          <img class="logo" src="{{ s.logo or (url_for('static', filename='images/logo.webp', v=asset_version) if asset_version else url_for('static','images/logo.webp')) }}"
               alt="{{ s.name }} logo" loading="lazy" decoding="async" />
          <div class="min-w-0">
            <div class="font-extrabold text-yellow-200 leading-tight truncate">{{ s.name }}</div>
            <div class="inline-flex items-center gap-2 text-[11px] text-yellow-100/80">
              <span class="badge rounded-full px-2 py-0.5">{{ s.tier or 'Community' }}</span>
              {% if s.amount %}<span>${{ '{:,.0f}'.format(s.amount) }}</span>{% endif %}
            </div>
          </div>
        </div>
        <div class="mt-auto flex items-center gap-2">
          <a href="{{ s.url or '#' }}" rel="noopener sponsored" target="_blank"
             class="inline-flex items-center justify-center rounded-lg bg-yellow-300 px-3 py-1.5 text-sm font-black text-black">Visit</a>
          <button type="button" class="inline-flex items-center justify-center rounded-lg border border-yellow-400/60 bg-yellow-300/10 px-3 py-1.5 text-sm font-bold text-yellow-200"
                  data-open-donate-modal data-amount="{{ (s.amount and (s.amount/10)|int) or 100 }}">Match</button>
        </div>
      </li>
    {% endfor %}
  </ul>
</section>

<script nonce="{{ csp_nonce() if csp_nonce is defined else '' }}">
(() => {
  const root = document.getElementById('sponsor-wall'); if (!root || root.__init) return; root.__init = true;

  // Tier filtering
  const chips = root.querySelectorAll('.chips [data-tier]');
  const cards = root.querySelectorAll('[data-tier]:not(.chips [data-tier])');

  function setFilter(val){
    chips.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.tier === val)));
    cards.forEach(card => {
      const on = (val === 'all') || (card.dataset.tier === val);
      card.style.display = on ? '' : 'none';
    });
  }
  chips.forEach(btn => btn.addEventListener('click', () => setFilter(btn.dataset.tier)));
  setFilter('all');

  // Donate “Match” buttons
  root.addEventListener('click', (e)=>{
    const btn = e.target.closest('[data-open-donate-modal]'); if (!btn) return;
    e.preventDefault();
    const amt = parseInt(btn.getAttribute('data-amount')||'0',10) || undefined;
    (window.openDonationModal?.({ amount: amt })) ?? window.dispatchEvent(new CustomEvent('fc:donate:open', { detail:{ amount: amt }}));
  });
})();
</script>
HTML
echo "✅ Wrote $F"
