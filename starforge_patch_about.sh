#!/usr/bin/env bash
set -euo pipefail

echo "╭──────────────────────────────────────────────╮"
echo "│  📜 Starforge About+Mission Patch — SV Elite │"
echo "╰──────────────────────────────────────────────╯"

BASE=${BASE:-app/templates/home.html}
TS=$(date +%Y%m%d-%H%M%S)

# Auto-detect fallback if not set
if [ ! -f "$BASE" ]; then
  BASE=$(grep -RIl --exclude="*.bak*" --include="*.html" "FC:ABOUT_MISSION" app/templates | head -1 || true)
fi
[ -z "$BASE" ] && { echo "❌ Could not locate About+Mission template"; exit 1; }

echo "→ Target template: $BASE"

# Backup first
cp "$BASE" "$BASE.bak.$TS"

# Replace block safely with Perl heredoc
perl -0777 -i -pe "$(cat <<'PERL'
s{<!-- FC:ABOUT_MISSION.*?</section>}{
<!-- FC:ABOUT_MISSION — Creative About & Mission Block -->
<section aria-labelledby="about-mission-heading" class="relative py-20 px-4 sm:px-8 bg-gradient-to-b from-zinc-950 via-black to-zinc-950 rounded-3xl shadow-2xl overflow-hidden" id="about-and-mission" role="region" tabindex="-1">

  <!-- Floating SVG Accents -->
  <img aria-hidden="true" class="absolute left-0 top-14 w-24 md:w-36 opacity-70 animate-spin-slow pointer-events-none select-none" src="{{ url_for('static', filename='basketball-accent.svg') }}" />
  <img aria-hidden="true" class="absolute right-0 bottom-14 w-20 md:w-32 opacity-50 animate-spin-reverse-slow pointer-events-none select-none" src="{{ url_for('static', filename='basketball-accent.svg') }}" />

  <!-- Player Mosaic -->
  <div aria-label="Our Players" class="grid grid-cols-3 sm:grid-cols-5 gap-3 max-w-3xl mx-auto py-8 relative z-10" role="list">
    {% for p in about %}
    <div class="player-card" role="listitem" tabindex="0">
      <img alt="{{ p.name }} – Connect ATX Elite player" class="rounded-xl shadow-lg transition-transform duration-300 hover:scale-105 focus:scale-105 focus:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400" src="{{ url_for('static', filename=p.img) }}" />
      <h4 class="text-center mt-2 font-semibold text-lg">{{ p.name }}</h4>
    </div>
    {% endfor %}
  </div>

  <!-- About & Mission Text -->
  <div class="max-w-4xl mx-auto text-center py-2 px-2 space-y-6 relative z-10">
    <h2 class="text-2xl sm:text-3xl font-extrabold bg-gradient-to-r from-gold via-yellow-400 to-gold bg-clip-text text-transparent animate-shine drop-shadow-md" id="about-mission-heading" tabindex="0">
      {{ mission_heading or "More Than Basketball — We’re Family On A Mission" }}
    </h2>
    <p class="text-xl sm:text-2xl font-semibold text-white opacity-90" tabindex="0">
      <span class="text-yellow-400 font-bold">{{ brand_name or "Connect ATX Elite" }}</span> is more than a team—it's a family-powered movement...
    </p>
    <blockquote class="text-lg text-yellow-200 opacity-90 italic max-w-3xl mx-auto" tabindex="0">
      “{{ mission_quote or "Family means showing up, believing in each other, and making sure no one is left behind." }}”
      <footer class="text-gold font-semibold mt-2"> — {{ mission_quote_author or "Coach Angel Rodriguez" }}</footer>
    </blockquote>
  </div>

  <!-- Stats + CTA + Video (to be expanded in full) -->
  <div class="text-center my-10">
    <button id="storyBtn" type="button">Watch Our Story</button>
  </div>

</section>
}gms
PERL
)" "$BASE"

echo "✅ About+Mission block patched into: $BASE"

