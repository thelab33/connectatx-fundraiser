# Starforge Elite — Hero Auto‑Enhance Kit

This mini‑toolchain for your FundChamps hero does three things fast:
1) **Forge responsive AVIF/WEBP** from your source hero image.
2) **Drop‑in Jinja snippets** to use the forged set automatically.
3) **Relocate the team name** into a *vertical brand spine* (surprise placement) with sleek CSS.

---

## 0) Install dependencies
```bash
cd path/to/your/repo
npm i -D sharp svgo
```

> **Why Sharp directly?** Your earlier `sharp-cli` failed due to wrong flags. We use a tiny Node script with the real API so it “just works”.

---

## 1) Forge your hero image set

By default we assume your image is at **`app/static/images/connect-atx-team.jpg`**.
If it’s at `static/images/connect-atx-team.jpg`, the script will auto‑detect and write to `static/images/hero/` instead.

```bash
node starforge-elite/scripts/starforge.mjs images
```

Outputs (created if missing):
```
app/static/images/hero/hero-1920.avif
app/static/images/hero/hero-1280.avif
app/static/images/hero/hero-960.avif
app/static/images/hero/hero-1920.webp
app/static/images/hero/hero-1280.webp
app/static/images/hero/hero-960.webp
app/static/images/hero/hero-lqip.txt   (base64 data URI for tiny preview)
```

You can override the source and output via env vars:
```bash
SRC="static/images/connect-atx-team.jpg" OUTDIR="static/images/hero" node starforge-elite/scripts/starforge.mjs images
```

---

## 2) (Optional) Optimize any SVG logos
```bash
npx svgo -f app/static/images -o app/static/images
```

---

## 3) Wire up the picture element (Jinja)

Add this where your `<picture>` was (or use it as an include):

```jinja
{% include "starforge/_hero_picture_refactor.html.jinja" %}
```

It uses your existing `hero_src` / `hero_src_mobile` variables, but **switches to the forged responsive set automatically** whenever the source filename contains `connect-atx-team.jpg`.

---

## 4) Vertical Brand Spine (relocates “Connect ATX Elite”)

Drop this *inside* your hero figure wrapper (e.g., as the first child of `.fc-hero-tilt` or `.fc-hero-card`):

```jinja
{% set _brand = team_name if team_name else "Connect ATX Elite" %}
{% include "starforge/_brand_spine.html.jinja" with context %}
```

Then include the CSS once on the page:
```html
<link rel="stylesheet" href="/starforge/brand-spine.css">
```

Or paste the CSS into your main stylesheet (content is in `css/brand-spine.css`).

---

## 5) Helpful NPM scripts (optional)
Add to your `package.json`:
```json
{
  "scripts": {
    "forge": "node starforge-elite/scripts/starforge.mjs images",
    "forge:lqip": "node starforge-elite/scripts/starforge.mjs lqip"
  }
}
```

Now:
```bash
npm run forge        # build AVIF/WEBP set
npm run forge:lqip   # regenerate the LQIP only
```

---

## Notes
- The forging script crops to **16:9 cover**, keeps the subject centered, and uses tuned quality (AVIF ~62, WEBP ~70).
- The brand spine is fully keyboard‑accessible on small screens (it becomes a top ribbon).
- No build system required — pure Node + CSS.
