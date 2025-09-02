# FundChamps — Shopify‑grade Polish (v6)

This bundle gives you:
- **Macros:** `hero`, `tiers`, `about` as drop‑in includes.
- **Duplicate tiers fix:** a script & a tiny runtime guard.
- **Unified tokens:** `static/css/tokens.css`.
- **Security hardening:** `app/security.py` (HSTS, CSP nonce, etc.).
- **Stripe Webhooks skeleton:** `app/blueprints/stripe_webhooks.py` ready for real secrets.
- **CI sample:** `.github/workflows/ci.yml`

## Quick apply

1) Copy the contents of this zip into your project root (keep folders).
2) Wire security + stripe webhooks in your Flask app factory:
   ```py
   from app.security import install_security
   from app.blueprints.stripe_webhooks import bp as stripe_bp

   install_security(app)
   app.register_blueprint(stripe_bp, url_prefix="/stripe")
   ```
3) Include tokens in your base layout `<head>`:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='css/tokens.css') }}">
   ```
4) Use macros (replace any hardcoded tiers/about/hero blocks):
   ```jinja2
   {% from "macros/hero.html"  import render_hero %}
   {% from "macros/tiers.html" import render_tiers %}
   {% from "macros/about.html" import render_about %}

   {{ render_hero() }}
   {{ render_tiers(tiers, opts={'id':'tiers', 'brand_color': team.theme_color if team else '#facc15', 'currency': team.currency if team else 'USD', 'team_name': team.name if team else 'FundChamps'}) }}
   {{ render_about() }}
   ```
5) Remove duplicate tiers from source (recommended):
   ```bash
   python scripts/fix_duplicate_tiers.py app/templates --write
   ```
   If you still see duplicates in dev, the runtime guard hides exact dupes; check your template includes.

6) Stripe: set env vars in your runtime:
   ```bash
   export STRIPE_WEBHOOK_SECRET=whsec_...
   export STRIPE_API_KEY=sk_test_...
   ```

## Files
- `app/templates/macros/tiers.html` — flip‑card tiers (motion‑safe, ARIA), nonce‑aware.
- `app/static/js/tiers_dedupe.js`   — dev helper to hide exact duplicate #tiers blocks.
- `scripts/fix_duplicate_tiers.py`  — scans Jinja templates; keeps first #tiers section.
- `app/security.py`                 — security headers + CSP nonce context.
- `app/blueprints/stripe_webhooks.py` — minimal, safe verify & event stub.
- `app/static/css/tokens.css`       — design tokens (colors/spacing/type).
- `.github/workflows/ci.yml`        — basic lint/test scaffold.

---

**Note:** CSP here is conservative and includes a nonce for inline `<style nonce>`/`<script nonce>`. Adjust directives to match your CDN/analytics if needed.
