#!/usr/bin/env python3
"""
forge_prestige_patch.py — SV-Elite Partial Upgrader (Overlay Sweep)
- Auto-updates ALL overlay partials with SaaS-ready markup
- Creates timestamped backups for rollback
"""

import shutil, time
from pathlib import Path

PARTIALS_DIR = Path("app/templates/partials")

# 🔑 Elite replacements for ALL overlay partials
PATCHES = {
    "hero_and_fundraiser.html": """{# =====================================================================
   FundChamps — HERO + FUNDRAISER (SV-Elite)
   Full overlay hero: bg + overlay + meter + CTA
   ===================================================================== #}
<section id="hero" class="relative z-20 bg-black text-white">
  <div class="absolute inset-0">
    <img src="{{ heroBg|default(url_for('static', filename='images/hero.webp')) }}" alt="" class="w-full h-full object-cover">
    <div class="absolute inset-0 bg-black/70"></div>
  </div>
  <div class="relative max-w-5xl mx-auto px-4 py-24 text-center">
    <img src="{{ logoSrc|default(url_for('static', filename='images/logo.webp')) }}" alt="{{ teamName }} logo" class="mx-auto h-24 mb-6">
    <h1 class="text-4xl md:text-5xl font-extrabold mb-4">{{ teamName }}</h1>
    <p class="text-lg opacity-80 mb-6">Fuel the journey. Every dollar brings us closer.</p>
    <div id="fundraiser-meter" class="bg-zinc-800 rounded-xl overflow-hidden h-6 mb-4">
      <div class="bg-[color:var(--fc-brand)] h-6" style="width: {{ rawPct|default(0) }}%"></div>
    </div>
    <div class="flex justify-center gap-3">
      <a href="#donate" class="px-5 py-2 bg-[color:var(--fc-brand)] text-black font-semibold rounded-lg">Donate</a>
      <a href="#sponsor" class="px-5 py-2 bg-zinc-800 rounded-lg">Sponsor</a>
    </div>
  </div>
</section>
""",

    "about_section.html": """{# =====================================================================
   FundChamps — About Section (SV-Elite)
   ===================================================================== #}
<section id="about" class="relative z-10 bg-zinc-950 text-white py-16">
  <div class="max-w-6xl mx-auto px-4 text-center">
    <h2 class="text-3xl font-bold mb-6">Our Mission</h2>
    <p class="max-w-2xl mx-auto opacity-80">We’re building more than athletes — we’re building leaders. Your support helps cover travel, gear, and academics for every player.</p>
  </div>
</section>
""",

    "tiers.html": """{# =====================================================================
   FundChamps — Sponsorship Tiers (SV-Elite)
   ===================================================================== #}
<section id="tiers" class="relative z-10 bg-black text-white py-16">
  <div class="max-w-6xl mx-auto px-4">
    <h2 class="text-3xl font-bold text-center mb-8">Sponsorship Tiers</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="p-6 rounded-2xl bg-zinc-900 shadow-lg">
        <h3 class="text-xl font-semibold mb-2">Bronze</h3>
        <p class="opacity-70 mb-3">$250 donation</p>
        <button class="px-4 py-2 bg-[color:var(--fc-brand)] text-black rounded-lg">Join</button>
      </div>
      <div class="p-6 rounded-2xl bg-zinc-900 shadow-lg border-2 border-[color:var(--fc-brand)]">
        <h3 class="text-xl font-semibold mb-2">Silver</h3>
        <p class="opacity-70 mb-3">$500 donation</p>
        <button class="px-4 py-2 bg-[color:var(--fc-brand)] text-black rounded-lg">Join</button>
      </div>
      <div class="p-6 rounded-2xl bg-zinc-900 shadow-lg">
        <h3 class="text-xl font-semibold mb-2">Gold</h3>
        <p class="opacity-70 mb-3">$1000 donation</p>
        <button class="px-4 py-2 bg-[color:var(--fc-brand)] text-black rounded-lg">Join</button>
      </div>
    </div>
  </div>
</section>
""",

    "sponsor_hub.html": """{# =====================================================================
   FundChamps — Sponsor Hub (SV-Elite)
   ===================================================================== #}
<section id="sponsor-hub" class="relative z-10 bg-zinc-950 text-white py-16">
  <div class="max-w-7xl mx-auto px-4">
    <h2 class="text-3xl font-bold mb-6">Sponsor Hub</h2>
    <p class="opacity-70 mb-6">Celebrate the partners who power our journey.</p>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-zinc-900 rounded-lg p-4 text-center">Acme Corp</div>
      <div class="bg-zinc-900 rounded-lg p-4 text-center">Jane D.</div>
      <div class="bg-zinc-900 rounded-lg p-4 text-center">Smith & Co.</div>
      <div class="bg-zinc-900 rounded-lg p-4 text-center">Your Brand Next!</div>
    </div>
  </div>
</section>
""",

    "sponsor_wall.html": """{# =====================================================================
   FundChamps — Sponsor Wall (SV-Elite)
   ===================================================================== #}
<section id="sponsor-wall" class="relative z-10 bg-black text-white py-16">
  <div class="max-w-7xl mx-auto px-4">
    <h2 class="text-3xl font-bold mb-8 text-center">Sponsor Wall</h2>
    <div class="grid grid-cols-2 md:grid-cols-5 gap-6">
      <div class="h-24 flex items-center justify-center bg-zinc-900 rounded-xl">Logo 1</div>
      <div class="h-24 flex items-center justify-center bg-zinc-900 rounded-xl">Logo 2</div>
      <div class="h-24 flex items-center justify-center bg-zinc-900 rounded-xl">Logo 3</div>
      <div class="h-24 flex items-center justify-center bg-zinc-900 rounded-xl">Logo 4</div>
      <div class="h-24 flex items-center justify-center bg-zinc-900 rounded-xl">Logo 5</div>
    </div>
  </div>
</section>
"""
}

def patch_file(filename, new_content):
    path = PARTIALS_DIR / filename
    if not path.exists():
        print(f"❌ {filename} not found, skipping.")
        return
    backup = path.with_suffix(path.suffix + f".bak-" + time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, backup)
    path.write_text(new_content, encoding="utf-8")
    print(f"✅ Patched {filename} (backup: {backup.name})")

if __name__ == "__main__":
    for fn, content in PATCHES.items():
        patch_file(fn, content)
    print("\n🎉 Overlay partials upgraded to SV-Elite.")
    print("↩ To rollback: copy .bak file back into place.")

