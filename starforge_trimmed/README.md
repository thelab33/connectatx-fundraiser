# FundChamps • Starforge Trimmed Patch (v2)

Purpose: a **minimal, premium, PDF-like** landing with just the essentials:
**Hero card, Tiers, Impact, Header/About, Footer** — readable, brandable, and print-friendly.

## What’s inside

- `app/static/css/starforge.min.css` – single-file tokens + layout + print styles
- Components (Jinja partials):
  - `app/templates/components/hero_card.html`
  - `app/templates/components/tiers_grid.html`
  - `app/templates/components/impact_grid.html`
  - `app/templates/components/header_about.html`
  - `app/templates/components/footer_min.html`
- `snippets/include_calls.md` – exactly how to include each section
- `scripts/apply_patch_min.sh` – copies files & injects CSS link into `layout.html`

## Apply

```bash
unzip fundchamps_starforge_trimmed_patch_v2.zip -d starforge_trimmed
cd starforge_trimmed
export TARGET_ROOT=/path/to/your/project   # or run from project root and omit
bash scripts/apply_patch_min.sh
```

## Use in your home template

Paste these includes in order (see `snippets/include_calls.md` for the exact lines):

1. `hero_card.html`
2. `tiers_grid.html`
3. `impact_grid.html`
4. `header_about.html`
5. `footer_min.html` (or keep your existing footer)

## Theming

Change the one variable in CSS:

```css
:root {
  --brand: 50 100% 58%;
} /* H S L */
```
