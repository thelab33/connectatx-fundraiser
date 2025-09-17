FundChamps — Turnkey Patch
===========================
Date: 2025-09-17T17:09:48.380455Z

What this patch does
--------------------
1) Fixes failing tests:
   - `app/models/example.py`: real SQLAlchemy model with soft-delete + timestamps.
   - `app/helpers.py`:
     * adds `emit_funds_update(...)` used by tests
     * makes `_calc_next_milestone_gap(...)` return ("gap", "Goal") when the next milestone is the goal.
   - `app/services/payments.py`:
     * `create_paypal_order` now returns `{"order_id": ...}`
     * `capture_paypal_order` now returns `{"status": ..., "amount": ...}` (float), as tests expect.

2) CSP polishing:
   - Adds a nonce to the last un-nonced `<script>` in `base.html` (`qr-init-shim.js`).

3) UX polish:
   - Adds a tiny a11y hint wired to your hotkey: the Donate button is now `aria-describedby="donate-kbd-hint"`
     with a visually-hidden note: “Tip: Press D to donate from anywhere on this page.”

Files included
--------------
- app/models/example.py
- app/helpers.py        (appended function + milestone tweak)
- app/services/payments.py
- app/templates/base.html
- app/templates/partials/hero_and_fundraiser.html

How to apply
------------
From your repo root:

    unzip -o fundchamps_patch_2025-09-17.zip

Or copy files into place manually keeping identical paths.

After applying:
---------------
- Run: `pytest -q`  (the seven previously failing tests should pass)
- Run: `python3 starforge_audit.py --config app.config.DevelopmentConfig`
  (CSP warnings should drop; large CSS warning remains until you split/minify CSS.)

Rollback
--------
Your originals remain in git. If needed:
    git restore app/helpers.py app/models/example.py app/services/payments.py app/templates/base.html app/templates/partials/hero_and_fundraiser.html
