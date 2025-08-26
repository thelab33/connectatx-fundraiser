# FundChamps Audit Report

_Generated: 2025-08-23T00:48:43.348380Z_

**Summary:** 7/14 checks passed.

## ✅ PASS — Required partials exist

All present

**Advice:** Create/restore the missing partials or update includes to match existing filenames

## ✅ PASS — Template include paths resolve

Resolved 36 includes

**Advice:** Rename or fix the include paths; or ensure those partials exist under app/templates/

## ✅ PASS — About macro file present

shared/components/about_section.html

**Advice:** Place your about_section macro at shared/components/about_section.html or update import paths.

## ✅ PASS — Hero glass class present

**Files:**
- `partials/hero_and_fundraiser.html`

**Advice:** Add class="hero-glass" to the main hero card wrapper.

## ✅ PASS — Hero meter elements present

**Files:**
- `partials/hero_and_fundraiser.html`

**Advice:** Ensure the progress bar uses id="fundraiser-meter" and inner fill id="fc-bar".

## ❌ FAIL — Single CSS stylesheet loaded in base.html

Found 0 CSS links: []

**Advice:** Load only one built stylesheet, e.g., css/dist/app.min.css with cache-busting.

## ❌ FAIL — Tailwind entry exists (src/index.css)

src/index.css

**Advice:** Create src/index.css importing tokens + components; build to dist/app.min.css.

## ❌ FAIL — Orphan CSS files (ok to delete/move)

- fc_prestige.css
- header-safe.css
- _legacy_input.css
- input.css
- tiers-elite.css
- elite-upgrades.css
- output.css
- impact-lockers.css
- brand.tokens.css
- tailwind.min.css
- fc_prestige-header.css
- archive/_legacy_input.css
- src/base.css
- src/components.css
- src/input.css

**Advice:** Move needed rules into src/ and remove legacy outputs (output.css, tailwind.min.css, backups).

## ✅ PASS — :focus-visible duplicated across header styles

Found in: header-safe.css

**Advice:** Keep a single authoritative focus-visible block in src/components/header.css

## ❌ FAIL — Hero CSS module present

src/components/hero.css

**Advice:** Add src/components/hero.css to restore glass overlay & proportional meters.

## ❌ FAIL — Payments API blueprint endpoints

payments_config: MISSING; checkout: MISSING; thanks: MISSING; stats: MISSING

**Advice:** Add app/blueprints/payments.py with /api/payments/config, /api/checkout, /api/thanks, /api/stats.

## ❌ FAIL — .env contains required keys

Missing: FUNDRAISING_GOAL, TEAM_NAME

**Advice:** Add the missing keys; use live keys in production.

## ❌ FAIL — Optional STRIPE_PAYMENT_LINK set

Not set

**Advice:** If set, Quick Donate can redirect instantly to Stripe hosted page.

## ✅ PASS — Header mini meter styles present

Found in: header-safe.css

**Advice:** Ensure #hdr-meter .track and .fill are defined (responsive width/height).
