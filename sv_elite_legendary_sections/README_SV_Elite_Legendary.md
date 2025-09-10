# SV‑Elite Legendary Sections — Drop‑In Partials
Version: 1.0 · Built: 2025-09-10 00:39 

This bundle contains premium, CSP‑safe, mobile‑first sections for your fundraising platform. Each partial is self‑contained with a `<style>` block and minimal JS (scoped + nonce‑friendly).

## What’s inside
- `header_and_announcement.html` — Sticky glass header with brand crest, primary nav, Donate/Sponsor CTAs, Stripe Secure pill, mobile sheet menu, and optional announcement bar.
- `hero_and_fundraiser.html` — Compact dashboard hero with inline quick amounts, live progress meter (ARIA), QR “Scan to Give,” text‑to‑give, and mobile sticky donate.
- `sponsor_leaderboard.html` — Real‑time marquee ticker with VIP pulses, pause/speed controls, offline queue, SR live regions, and API hydration seed.
- `newsletter.html` — Accessible `<dialog>` popup with dwell‑time + cooldown, typo‑fix suggestions, honeypot, and `fcNewsletter.open()/close()` API.
- `footer.html` — Ambient glow footer with Donate/Sponsor CTAs, Stripe flip‑seal, PCI note, powered‑by, and back‑to‑top progress button.

## Quick start (Flask/Jinja example)
1. Copy the partials into your templates folder.
2. In your layout, include them where you want the sections to render:
   ```jinja2
   {% include "header_and_announcement.html" %}
   {% include "hero_and_fundraiser.html" %}
   {% include "sponsor_leaderboard.html" %}
   ...
   {% include "footer.html" %}
   ```
3. Provide context variables (examples shown). All fields are optional with smart fallbacks:
   ```jinja2
   {% set team = {
     "team_name": "Connect ATX Elite",
     "team_slug": "connect-atx-elite",
     "theme_color": "#facc15",
     "logo_url": "/static/images/crest.png",
     "is_501c3": true,
     "contact_email": "hello@connectatx.org",
     "team_id": "atx‑elite‑u15"
   } %}
   {% set fundraising_goal = 35000 %}
   {% set funds_raised = 12450 %}
   {% set stripe_payment_link = "https://buy.stripe.com/test_xxx" %}
   {% set fundraiser_title = "Fuel the Season." %}
   {% set fundraiser_title_2 = "Fund the Future." %}
   {% set meta_description = "Direct support for gear, travel, and tutoring—every dollar moves a kid forward." %}
   {% set TEXT_KEYWORD = "ELITE" %}
   {% set TEXT_SHORTCODE = "44321" %}
   ```
4. (Optional) Hook up the Shoutouts API used by the leaderboard (`/api/shoutouts`) to return the latest sponsor messages:
   ```json
   [{"sponsor":"Acme Co.","msg":"backed the team!","tier":"Gold"}]
   ```

## Dependencies / Notes
- **No external JS required.** All scripts are inline, CSP‑nonce aware. If you enforce CSP, pass a `NONCE` into the template context or define a `csp_nonce()` macro.
- **Utilities:** The markup uses Tailwind‑style utility classes. You can run with Tailwind v3+ or keep as‑is; custom `<style>` blocks cover critical styles.
- **Accessibility:** Live regions, ARIA meters, focus‑traps, keyboardable controls, reduced‑motion fallbacks, and high‑contrast/forced‑colors supported.
- **Payments:** Donate buttons prefer a `stripe_payment_link`; otherwise they fall back to your `main.donate` endpoint.
- **Brand color:** Provide `theme_hex`/`team.theme_color` to tint accents.

## Copy & Tuning
Send me your exact copy (headlines, subheads, chip labels), goal/raised numbers, and any tier inventories or VIP badges. I’ll bake them into the partials and re‑ship a tailored bundle.

— Built with ❤️ for fast demos and real‑world launches.
