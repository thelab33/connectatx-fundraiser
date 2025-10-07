# Hero Compact-Pro v7.9 (CSP-safe Bundle)

Turnkey, production-ready hero for fundraising pages:

- Split partials (left story vs right rail)
- Compact meter with live hydration from `/api/totals`
- Quick amount chips (+25/+50/+100), QR, share, sticky donate
- Mobile-first, a11y-first, and Content-Security-Policy (CSP) safe

---

## 1) Files

```
templates/
  hero/
    _left.html
    _rail.html
    hero.html
static/
  css/
    hero-compact-pro.css
  js/
    hero-compact-pro.js
tests/
  e2e/
    hero.spec.ts
```

> Optional: include `static/js/qrcode.min.js` in your project (or vendor it) for QR generation.

---

## 2) Include in your base template

```jinja
{# in base.html (head) #}
<link rel="stylesheet" href="{{ url_for('static', filename='css/hero-compact-pro.css') }}">

{# before </body> #}
<script defer src="{{ url_for('static', filename='js/qrcode.min.js') }}"></script>
<script defer src="{{ url_for('static', filename='js/hero-compact-pro.js') }}"></script>
```

No inline scripts/styles required. Works with strict CSP like:

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self';
  img-src 'self' data:;
  connect-src 'self';
```

---

## 3) Render the hero where you need it

```jinja
{% include "hero/hero.html" %}
```

### Jinja variables supported (with sensible defaults)

- `theme_hex` (default `#facc15`)
- `team` object (`team.name`, `team.hero_bg`, etc.)
- `funds_raised`, `fundraising_goal`
- `fundraiser_title`, `fundraiser_title_2`, `meta_description`
- `cta_label`
- `stripe_payment_link` (or `/donate` route)
- `hero_image_url`, `hero_image_mobile_url`, `hero_alt`

---

## 4) Backend endpoints (Flask examples)

### `/api/totals`

Return up-to-date totals to hydrate the meter.

```python
from flask import Blueprint, jsonify

bp = Blueprint('api', __name__)

@bp.get('/api/totals')
def totals():
    total = get_total_raised()  # int
    goal  = get_goal_amount()   # int
    return jsonify({"total": int(total), "goal": int(goal)})
```

### `/donate` router (Stripe Checkout) — ensures quick-amount chips work even if you use Payment Links

```python
from flask import Blueprint, request, redirect, url_for, current_app
import stripe

bp = Blueprint('main', __name__)
stripe.api_key = current_app.config['STRIPE_SECRET']

@bp.get('/donate')
def donate():
    amt = request.args.get('amount', type=int)
    if not amt or amt < 5 or amt > 5000: amt = 25

    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=url_for('main.thanks', _external=True) + "?ok=1",
        cancel_url=url_for('main.home', _external=True),
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Donation"},
                "unit_amount": amt * 100
            },
            "quantity": 1
        }],
        allow_promotion_codes=True,
        metadata={"source": "hero"}
    )
    return redirect(session.url, code=303)
```

---

## 5) QA checklist (manual)

- Meter announces correct values in screen readers (`role="meter"`, `aria-valuetext`).
- Quick amounts rewrite links on `pointerdown` (check UTM params).
- QR shows when sidecard enters viewport; hides under 480px.
- Mobile sticky CTA is visible at <640px.
- `/api/totals` hydrates without layout shift.

---

## 6) Playwright test

Run Playwright after you start your dev server at `/`:

```bash
npx playwright test tests/e2e/hero.spec.ts
```

---

## 7) Extensibility hooks

- Dispatches `CustomEvent('fc:donate', { detail: { source:'hero', amount } })` on clicks — subscribe for analytics.
- Listens to `fc:meter:update` to update numbers programmatically.
- Uses `window.fc?.makeTrackedUrl(url, { from:'hero' })` if provided.

---

## 8) Notes on Stripe Payment Links

If you set `stripe_payment_link` to a Payment Link (e.g., `https://buy.stripe.com/...`), quick-amount chips will route through `/donate?amount=...` so you still get variable amounts. Main CTA will keep your Payment Link.

---
