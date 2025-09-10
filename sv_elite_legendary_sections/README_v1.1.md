# SV-Elite Legendary Sections — v1.1
Built: 2025-09-10 01:17 

What's new in v1.1
- Patched hero with focal controls, overlay-side toggle, and desktop overlay guard
- Robust hero image src + dimensions to prevent layout shift
- QR auto-hides if missing
- Donate + amount chips send UTM params; chips keep existing query strings
- Panel width tuned: clamp(280px, 26vw, 340px)

Quick include (Jinja):
  {% include "header_and_announcement.html" %}
  {% include "hero_and_fundraiser_v2.html" %}
  {% include "sponsor_leaderboard.html" %}
  {% include "newsletter.html" %}
  {% include "footer.html" %}

Per-photo tuning (on <section class="fc-hero">):
  data-overlay="right" or "left"
  style="--hero-focal-x: 20%; --hero-focal-y: 50%; --overlay-w: clamp(280px,26vw,340px); --overlay-gap:24px;"
