# FundChamps • Starforge v2.1 Micro‑Polish Patch
This tiny patch delivers the last 5%: equalized cards, cleaner progress labels, a mobile thumb‑reach dock, and a print‑perfect finish.

## What it does
- Appends **v2.1 micro‑polish CSS** to `app/static/css/starforge.min.css`
- Adds new partial: `app/templates/partials/mobile_dock.html`
- Includes ready‑to‑paste snippets for **hero inner**, **tier card block**, and **impact card block**

## Quick apply
```bash
unzip fundchamps_starforge_v2_1_patch.zip -d starforge_v2_1
cd starforge_v2_1
export TARGET_ROOT=/path/to/your/project   # run in project root and omit this
bash scripts/apply_patch_v2_1.sh
```

Then, in your landing template, add the dock include near the end of the page (before `endblock`):
```jinja
{% include "partials/mobile_dock.html" ignore missing %}
```

## Manual placement (optional)
- **Hero**: open `app/templates/partials/hero_and_fundraiser.html` and replace the inner content with `snippets/hero_and_fundraiser__inner.html`
- **Tiers**: inside your tier loop, use the structure from `snippets/tiers__card_block.html` to equalize heights and align CTAs.
- **Impact**: for each bucket card, use `snippets/impact__card_block.html`

All snippets are CSP‑safe and print‑friendly.
