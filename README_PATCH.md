# FundChamps Cleanup Patch

This patch streamlines `app/routes` and moves all write-side payments to `app/blueprints/fc_payments.py`.

## What changes

- Replaces `app/routes/api.py` with a **read-only** API (status, stats, donors, impact-buckets, payments/config + readiness).
- Adds `tools/cleanup_routes.sh` to safely remove legacy/duplicate route files:
  - `app/routes/routes.py` (legacy shim)
  - `app/routes/stripe.py` (duplicate Stripe router)
  - any `mixins.py.bak-*`
  - `__pycache__` folders
  - (interactive) asks before removing `donations.py`
- Adds `tools/verify_cleanup.py` to find lingering imports/URLs that still reference the removed Stripe routes.

## Apply

```bash
unzip -o fundchamps_cleanup_patch.zip -d ./
# review changes if you use git
bash tools/cleanup_routes.sh

# optional sanity check (shows warnings if old imports/urls are still used)
python3 tools/verify_cleanup.py
```

## Expected blueprints after cleanup

- `app/blueprints/fc_payments.py` → create PaymentIntents + webhooks + PayPal (server-side, write endpoints)
- `app/blueprints/fc_metrics.py` → impressions/clicks + weekly ROI snapshot
- `app/blueprints/health.py` → health/ready/live/status
- `app/routes/main.py` → homepage + static pages + stats JSON for widgets
- `app/routes/api.py` → read-only RESTX endpoints (docs, status, stats, donors, impact-buckets, payments config/readiness)
