#!/usr/bin/env python3
"""
FundChamps — Refactor index.html (SV-Prestige)
- Writes app/templates/index.html (idempotent, with sentinel)
- Ensures base.html (or layout.html) has a `{% block hero %}{% endblock %}`
- Removes any hero partial includes from base/layout to avoid duplicates
- Adds SEO/head upgrades, section flags, a11y structure
"""
from __future__ import annotations
import re, sys, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
INDEX_PATHS = [ROOT/"app/templates/index.html", ROOT/"app/templates/home.html"]
BASE_PATHS  = [ROOT/"app/templates/base.html", ROOT/"app/templates/layout.html"]

SENTINEL = "<!-- FC:INDEX_SV_PRESTIGE v2 -->"
HERO_INCLUDE_REGEX = re.compile(
    r'{%\s*include\s+"partials/(?:hero[_-].*?|hero|hero_and_fundraiser)\.html"[^%]*%}',
    re.I
)

INDEX_CONTENT = f"""{SENTINEL}
{{% extends "base.html" %}}

{{% block title %}}{{{{ team_name if team_name is defined else 'Connect ATX Elite' }}}} — Home{{% endblock %}}
{{% block h1 %}}{{{{ team_name if team_name is defined else 'Connect ATX Elite' }}}} — Fundraising Home{{% endblock %}}

{{% block head %}}
  {{{{ super() }}}}
  {{% if team and team.hero_bg is defined and team.hero_bg %}}
    <link rel="preload" as="image" href="{{{{ team.hero_bg }}}}" fetchpriority="high" imagesizes="100vw">
  {{% endif %}}
  {{% if stripe_publishable_key %}}<link rel="preconnect" href="https://js.stripe.com" crossorigin>{{% endif %}}
  <meta name="description" content="Support {{{{ team_name if team_name is defined else 'Connect ATX Elite' }}}} — help fund travel, uniforms, and training. Every dollar makes a difference.">
  {{% if request is defined %}}<link rel="canonical" href="{{{{ request.base_url }}}}">{{% endif %}}
  <meta property="og:title" content="{{{{ team_name if team_name is defined else 'Connect ATX Elite' }}}} — Fundraiser">
  <meta property="og:description" content="Back our team — goal-driven fundraiser with secure checkout.">
  {{% if team and team.hero_bg %}}<meta property="og:image" content="{{{{ team.hero_bg }}}}">{{% endif %}}
  <meta name="twitter:card" content="summary_large_image">
  <script nonce="{{{{ NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') }}}}" type="application/ld+json">
  {{
    {{
      {
        "@" : "http://schema.org",
        "@context": "http://schema.org",
        "@type": "SportsTeam",
        "name": (team_name if team_name is defined else "Connect ATX Elite"),
        "sport": "Basketball",
        "memberOf": {{ "@type": "Organization", "name": "Connect ATX Elite" }},
        "url": (request.base_url if request is defined else ""),
        "logo": (team.logo if team and team.logo is defined else "/static/images/logo.webp")
      }
    } | tojson | safe
  }}
  </script>
{{% endblock %}}

{{% block hero %}}
  {{% include "partials/hero_and_fundraiser.html" ignore missing with context %}}
  {{% if FLAGS is not defined or FLAGS.meter_strip is not defined or FLAGS.meter_strip %}}
    {{% include "partials/meter_strip.html" ignore missing with context %}}
  {{% endif %}}
{{% endblock %}}

{{% block content %}}
  {{% set _flags = FLAGS if FLAGS is defined else namespace() %}}

  <!-- 0) Mission -->
  {{% if _flags.mission is not defined or _flags.mission %}}
  <section id="mission" aria-labelledby="mission-heading" class="py-12 sm:py-16">
    <h2 id="mission-heading" class="sr-only">Our Mission</h2>
    {{% include "partials/about_section.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 1) Program Stats & Calendar -->
  {{% if _flags.program_stats is not defined or _flags.program_stats %}}
  <section id="program-stats" aria-labelledby="program-stats-heading" class="py-12 sm:py-16 bg-neutral-50/60">
    <h2 id="program-stats-heading" class="sr-only">Program Stats & Calendar</h2>
    {{% include "partials/program_stats_and_calendar.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 2) Sponsorship Tiers -->
  {{% if _flags.tiers is not defined or _flags.tiers %}}
  <section id="tiers" aria-labelledby="tiers-heading" class="py-12 sm:py-16">
    <h2 id="tiers-heading" class="sr-only">Sponsorship Tiers</h2>
    {{% include "partials/tiers.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 3) Sponsor Hub -->
  {{% if _flags.sponsor_hub is not defined or _flags.sponsor_hub %}}
  <section id="sponsor-hub" aria-labelledby="sponsor-hub-heading" class="py-12 sm:py-16">
    <h2 id="sponsor-hub-heading" class="sr-only">Sponsor Hub</h2>
    {{% include "partials/sponsor_hub.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 4) Sponsor Spotlight -->
  {{% if _flags.sponsor_spotlight is not defined or _flags.sponsor_spotlight %}}
  <section id="sponsor-spotlight" aria-labelledby="sponsor-spotlight-heading" class="py-12 sm:py-16 bg-neutral-50/60">
    <h2 id="sponsor-spotlight-heading" class="sr-only">Sponsor Spotlight</h2>
    {{% include "partials/sponsor_spotlight.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 5) Sponsor Wall Widget -->
  {{% if _flags.sponsor_wall_widget is not defined or _flags.sponsor_wall_widget %}}
  <section id="sponsor-wall-widget" aria-labelledby="sponsor-wall-widget-heading" class="py-10">
    <h2 id="sponsor-wall-widget-heading" class="sr-only">Sponsor Wall (Widget)</h2>
    {{% include "partials/sponsor_wall_widget.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 6) Sponsor Wall (full) -->
  {{% if _flags.sponsor_wall is not defined or _flags.sponsor_wall %}}
  <section id="sponsor-wall" aria-labelledby="sponsor-wall-heading" class="py-12 sm:py-16">
    <h2 id="sponsor-wall-heading" class="sr-only">Sponsor Wall</h2>
    {{% include "partials/sponsor_wall.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  <!-- 7) Newsletter -->
  {{% set show_news = (_flags.newsletter_section if _flags.newsletter_section is defined else true) %}}
  {{% if show_news %}}
  <section id="newsletter" aria-labelledby="newsletter-heading" class="py-12 sm:py-16 bg-neutral-50/60">
    <h2 id="newsletter-heading" class="sr-only">Newsletter</h2>
    <div id="newsletter-anchor" aria-hidden="true"></div>
    {{% include "partials/newsletter.html" ignore missing with context %}}
  </section>
  {{% endif %}}

  {{% include "partials/layout_bands.html" ignore missing with context %}}
{{% endblock %}}

{{% block scripts %}}
  {{{{ super() }}}}
  {{% include "partials/sticky_cta_manager.html" ignore missing with context %}}
  {{% if FLAGS is defined and FLAGS.ai_concierge %}}
    {{% include "partials/ai_concierge.html" ignore missing with context %}}
  {{% endif %}}
{{% endblock %}}
"""

def backup(path: Path):
    if not path.exists(): return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    shutil.copy2(path, bak)
    print(f"• Backup → {bak}")

def write_index(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        txt = p.read_text(encoding="utf-8")
        if SENTINEL in txt:
            print(f"✓ {p.name} already SV-Prestige; skipping")
            return
        backup(p)
    p.write_text(INDEX_CONTENT, encoding="utf-8")
    print(f"✓ Wrote SV-Prestige index → {p}")

def strip_hero_from_base(p: Path):
    if not p.exists(): return
    txt = p.read_text(encoding="utf-8")
    found = HERO_INCLUDE_REGEX.findall(txt)
    changed = False
    if found:
        txt = HERO_INCLUDE_REGEX.sub("", txt)
        changed = True

    # Ensure `{% block hero %}{% endblock %}` exists once after header include or before <main>
    if "{% block hero %}" not in txt:
        hook = re.search(r'{%\s*include\s+"partials/header[^"]*"\s+[^%]*%}', txt)
        if hook:
            idx = hook.end()
            txt = txt[:idx] + "\n{% block hero %}{% endblock %}\n" + txt[idx:]
        else:
            m = re.search(r"<main[^>]*>", txt, re.I)
            if m:
                idx = m.end()
                txt = txt[:idx] + "\n{% block hero %}{% endblock %}\n" + txt[idx:]
            else:
                # prepend as a safe fallback
                txt = "{% block hero %}{% endblock %}\n" + txt
        changed = True

    if changed:
        backup(p)
        p.write_text(txt, encoding="utf-8")
        print(f"✓ Updated {p.name}: removed hero include(s) and ensured hero block")
    else:
        print(f"✓ {p.name} already clean")

def main():
    wrote_any = False
    # 1) Refactor index/home
    for p in INDEX_PATHS:
        write_index(p)
        wrote_any = wrote_any or p.exists()

    # 2) Clean and prep base/layout
    for p in BASE_PATHS:
        strip_hero_from_base(p)

    if not wrote_any:
        print("⚠️ Could not find index/home path; wrote to default:", INDEX_PATHS[0])
    print("✅ Done. Only one hero will render, and the page is SV-Prestige ready.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)
