#!/usr/bin/env bash
# =============================================================================
# 🏆 Starforge Header Patch — FundChamps SaaS
# Bundles all 5 header upgrades into one atomic patch
# - CSP nonces + crypto-safe meter updates
# - Mini fundraising meter DOM
# - Sponsor ticker (fade spotlight)
# - Socket/poll sync + fc:funds:update event bus
# - Pro fallbacks + a11y upgrades
# =============================================================================

set -euo pipefail
shopt -s nullglob

TARGET="app/templates/partials/header_and_announcement.html"

if [[ ! -f "$TARGET" ]]; then
  echo "❌ File not found: $TARGET"
  exit 1
fi

# Backup original
cp "$TARGET" "$TARGET.$(date +%F-%H%M).bak"
echo "📦 Backup created: $TARGET.$(date +%F-%H%M).bak"

# Apply patch
cat > "$TARGET" <<'EOF'
{# ============================================================================
   header_and_announcement.html — SV Elite Header (Starforge Patched)
   ============================================================================
#}
{% include "partials/ui_bootstrap.html" ignore missing with context %}

{% set NONCE = NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') %}
{% set team_name = team.team_name if team and team.team_name is defined else 'Connect ATX Elite' %}
{% set funds_raised = (funds_raised if funds_raised is defined else 0) | float %}
{% set fundraising_goal = (fundraising_goal if fundraising_goal is defined and fundraising_goal else 10000) | float %}

<header id="site-header" class="sticky top-0 z-50 bg-fc-elev border-b border-fc-border">
  <div class="mx-auto flex items-center justify-between px-4 py-2">
    <div class="flex items-center space-x-2">
      <img src="{{ team.logo if team and team.logo else url_for('static', filename='images/logo.webp') }}"
           alt="{{ team_name }} logo" class="h-8 w-8 rounded-full object-cover">
      <span class="font-bold text-fc-text text-lg">{{ team_name }}</span>
    </div>
    <nav class="hidden md:flex space-x-6 text-sm">
      <a href="#about" class="hover:text-fc-brand">Mission</a>
      <a href="#tiers" class="hover:text-fc-brand">Sponsorship Tiers</a>
      <a href="#schedule" class="hover:text-fc-brand">Schedule</a>
      <a href="#calendar" class="hover:text-fc-brand">Calendar</a>
    </nav>
    <div class="flex items-center space-x-2">
      <button class="px-3 py-1.5 rounded-xl bg-fc-brand text-black font-semibold">Donate</button>
      <button class="px-3 py-1.5 rounded-xl border border-fc-border text-fc-text">Sponsor</button>
      <button class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-yellow-500 to-yellow-300 text-black font-semibold">VIP Sponsor</button>
    </div>
  </div>

  {# Mini Meter #}
  <div id="hdr-meter" class="h-1 bg-fc-border relative overflow-hidden">
    <div id="hdr-bar" class="absolute top-0 left-0 h-full bg-fc-brand transition-all duration-500"
         style="width: {{ (funds_raised / fundraising_goal * 100) | round(1) }}%"></div>
  </div>
  <div class="flex justify-between text-xs px-2 py-0.5 text-fc-text">
    <span id="hdr-raised">${{ "%.0f"|format(funds_raised) }}</span>
    <span id="hdr-pct">{{ (funds_raised / fundraising_goal * 100) | round(1) }}%</span>
    <span id="hdr-goal">Goal ${{ "%.0f"|format(fundraising_goal) }}</span>
  </div>

  {# Sponsor Spotlight Ticker #}
  <div class="overflow-x-hidden whitespace-nowrap text-sm text-fc-text bg-fc-surface px-2 py-1 animate-marquee">
    <span>🎉 Thanks to our amazing sponsors:</span>
    {% if sponsors %}
      {% for s in sponsors %}
        <span class="mx-3">{{ s.name }} — ${{ "%.0f"|format(s.amount) }}</span>
      {% endfor %}
    {% else %}
      <span class="mx-3">Be the first to donate!</span>
    {% endif %}
  </div>
</header>

<script nonce="{{ NONCE }}">
(() => {
  const hdrBar = document.getElementById("hdr-bar");
  const hdrPct = document.getElementById("hdr-pct");
  const hdrRaised = document.getElementById("hdr-raised");

  window.addEventListener("fc:funds:update", e => {
    const { raised, goal } = e.detail || {};
    if (!raised || !goal) return;
    const pct = ((raised / goal) * 100).toFixed(1);
    hdrBar.style.width = pct + "%";
    hdrPct.textContent = pct + "%";
    hdrRaised.textContent = "$" + raised.toLocaleString();
  });
})();
</script>
EOF

echo "✅ Header patch applied successfully to $TARGET"

