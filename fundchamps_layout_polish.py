import shutil

# ==== CONFIG ====
SOURCE_FILE = 'app/templates/index.html'    # Adjust as needed
BACKUP_FILE = SOURCE_FILE + '.bak'
OUTPUT_FILE = SOURCE_FILE                   # Overwrite the original
# =================

AGENCY_LAYOUT = """\
{# ============================================================================
index.html • FundChamps x Connect ATX Elite — $100K Agency Layout
• Hero split (overlap), staggered tiers grid, impact/about columns
• “Nike-ified” brand energy, not a boring stack!
============================================================================ #}
{% extends "base.html" %}
{% from "partials/_core_helpers.html" import nonce_attr %}

{% set ACCENT = team.theme_color or '#b91c1c' %} {# Red (Connect ATX Elite) #}
{% set SECONDARY = '#facc15' %} {# Gold accent #}
{% set BG_DARK = '#18181b' %}
{% set BG_MEDIUM = '#232127' %}
{% set BG_LIGHT = '#faf8f6' %}
{% set TEXT_MAIN = '#fff' %}
{% set TEXT_ACCENT = SECONDARY %}

{% block title %}{{ fundraiser_title or 'Connect ATX Elite FundChamps' }}{% endblock %}

{% block extra_styles %}
<style {{ nonce_attr(NONCE) }}>
.bg-elite-dark   { background: {{ BG_DARK }}; }
.bg-elite-med    { background: {{ BG_MEDIUM }}; }
.bg-elite-gold   { background: {{ SECONDARY }}; }
.bg-elite-light  { background: {{ BG_LIGHT }}; }
.text-elite-accent { color: {{ SECONDARY }}; }
.swoosh-divider {
  background: linear-gradient(135deg, {{ ACCENT }} 50%, transparent 80%);
  clip-path: polygon(0 100%, 100% 80%, 100% 100%, 0 100%);
  height: 54px; width: 100vw; margin-top: -48px;
  z-index: 5; position: relative;
}
.staggered-hero   { margin-top: -70px; }
.staggered-tiers .card-pop { z-index: 2; box-shadow: 0 8px 40px #0008; transform: scale(1.08) translateY(-16px);}
.staggered-tiers .card-edge { opacity:.88; filter: blur(.5px);}
.section-overlap  { margin-top: -54px; z-index: 10; position: relative; }
@media (max-width: 900px) {
  .staggered-hero { margin-top: 0; }
  .section-overlap { margin-top: 0;}
}
</style>
{% endblock %}

{% block content %}
<main id="main" class="font-sans antialiased bg-elite-dark text-white">

  {% include "partials/sponsor_leaderboard.html" ignore missing with context %}

  <!-- ========== 1. HERO: Split & Overlapping ========== -->
  <section class="relative min-h-[580px] bg-[radial-gradient(ellipse_65%_90%_at_60%_10%,#58131330_0%,transparent_85%),{{ BG_DARK }}] pt-12 pb-20 flex items-center z-10">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row gap-12 items-center justify-between px-6">
      <div class="w-full md:w-1/2 relative z-10">
        {% include "partials/hero_and_fundraiser.html" ignore missing with context %}
      </div>
      <div class="w-full md:w-1/2 staggered-hero relative z-10">
        {% include "partials/impact_donate_card.html" ignore missing with context %}
      </div>
    </div>
    <div class="swoosh-divider"></div>
  </section>

  <!-- ========== 2. TIERS: Staggered Agency Grid ========== -->
  <section class="relative staggered-tiers bg-elite-dark py-24 z-20">
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 items-end">
      <div class="card-edge md:translate-y-4">
        {% include "partials/tier_card_bronze.html" ignore missing with context %}
      </div>
      <div class="card-pop">
        {% include "partials/tier_card_gold.html" ignore missing with context %}
      </div>
      <div class="card-edge md:translate-y-4">
        {% include "partials/tier_card_silver.html" ignore missing with context %}
      </div>
    </div>
    <div class="max-w-2xl mx-auto mt-8">
      {% include "partials/tier_card_custom.html" ignore missing with context %}
    </div>
  </section>

  <!-- ========== 3. IMPACT: Goal & KPIs Side-By-Side ========== -->
  <section class="relative bg-elite-med py-20 section-overlap z-30">
    <div class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
      <div>
        {% include "partials/impact_goal_meter.html" ignore missing with context %}
      </div>
      <div class="flex flex-col gap-6">
        {% include "partials/impact_kpis.html" ignore missing with context %}
      </div>
    </div>
    <div class="swoosh-divider" style="background:linear-gradient(120deg,{{ SECONDARY }} 65%,transparent 85%);margin-top:50px;"></div>
  </section>

  <!-- ========== 4. ABOUT: Side-by-Side Columns ========== -->
  <section class="relative bg-elite-dark py-24 z-40">
    <div class="max-w-5xl mx-auto flex flex-col md:flex-row gap-10 items-center">
      <div class="flex-1">
        {% include "partials/about_media.html" ignore missing with context %}
      </div>
      <div class="flex-1">
        {% include "partials/about_content.html" ignore missing with context %}
      </div>
    </div>
  </section>

</main>
{% endblock %}
"""

def main():
    # Backup
    shutil.copyfile(SOURCE_FILE, BACKUP_FILE)
    print(f"✅ Backed up your original as {BACKUP_FILE}")

    # Overwrite with new layout
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(AGENCY_LAYOUT)
    print(f"🚀 Updated {OUTPUT_FILE} with agency-grade layout!\n\n✨ Open it in your editor or refresh your site.")

if __name__ == '__main__':
    main()

