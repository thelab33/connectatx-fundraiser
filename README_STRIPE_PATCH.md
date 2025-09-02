# Stripe Refactor Patch

This patch:
- Replaces **app/blueprints/fc_payments.py** with a Stripe-only, CSRF-exempt blueprint mounted at **/payments**.
- Adds a dev smoke page at **/dev/stripe_smoke** (template only; if you need a route, add one line below).
- Keeps ROI Redis counters (optional) and Socket.IO donation pings.

## Install
Unzip at repo root (so files land under `app/`):
```bash
unzip -o stripe_refactor_patch.zip -d ./
```

## Env (dev)
```bash
export STRIPE_SECRET_KEY=sk_test_xxx
export STRIPE_PUBLISHABLE_KEY=pk_test_xxx   # used by templates/smoke page
export API_TOKENS=devtoken                   # optional
export PAYMENTS_REQUIRE_BEARER=0             # set to 1 to enforce bearer on /payments/*
export REDIS_URL=redis://localhost:6379/0    # optional
```

## Routes
- POST **/payments/stripe/intent** → `{"client_secret": "...", "publishable_key": "..."}`
- POST **/payments/stripe/webhook** (set your endpoint in Stripe dashboard)
- GET  **/payments/health**

> Note: The earlier 404s were due to calling **/api/payments/stripe/intent**.
> This blueprint is mounted at **/payments** (as shown in your Flask route list).

## Quick Test
```bash
# confirm route exists
FLASK_APP=app:create_app flask routes | grep -i 'payments/stripe/intent'

# create an intent
curl -sS http://localhost:5003/payments/stripe/intent       -H 'Content-Type: application/json'       -d '{"amount":50,"currency":"usd","source":"api","description":"Fundraiser test"}' | jq
# if enforcing bearer:
#  -H 'Authorization: Bearer devtoken'
```

## Optional: add a temp route for the smoke page
In your main blueprint, add:
```python
@bp.get("/dev/stripe_smoke")
def stripe_smoke():
    return render_template("dev/stripe_smoke.html")
```

## Webhook (dev)
```bash
stripe listen --events payment_intent.succeeded,charge.succeeded \
  --forward-to http://localhost:5003/payments/stripe/webhook
```