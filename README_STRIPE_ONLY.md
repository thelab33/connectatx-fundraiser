# Stripe-only Patch (FundChamps)

This patch removes **all PayPal code** and leaves Stripe as the only gateway.

## What it does
- Replaces `app/blueprints/fc_payments.py` with a **Stripe-only** blueprint (PaymentIntent + webhook).
- Replaces `app/routes/api.py` and removes PayPal endpoints/fields.
- Replaces `app/blueprints/health.py` and removes PayPal health checks.
- Adds helper script `tools/stripe_only.sh` to:
  - strip `paypalcheckoutsdk` from `requirements.txt` (if present)
  - update templates to say “Secure checkout via Stripe.” (instead of “Stripe / PayPal”)
  - verify that PayPal is fully removed

## Apply
```bash
unzip -o stripe_only_patch.zip -d ./

# optional: inspect what's inside
ls -R tools app

# run helper (safe; prompts before destructive edits)
bash tools/stripe_only.sh

# reinstall deps if you changed requirements
pip install -r requirements.txt

# restart your app and confirm routes
FLASK_APP=app:create_app flask routes | grep -i payments

# quick smoke tests
curl -sS http://localhost:5003/api/payments/config | jq
curl -sS http://localhost:5003/api/payments/readiness | jq
```

## Notes
- If any template still references `paypal_*` variables, it will simply render empty/False. The script tries to clean common strings.
- Webhook: keep forwarding only Stripe events you handle (e.g., `payment_intent.succeeded`, `charge.succeeded`).
