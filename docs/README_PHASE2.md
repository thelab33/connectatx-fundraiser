# Phase 2 — MVP Polish Pack

This pack gives you two things right now:

1. **Duplicate tiers fix** — a script that removes accidental duplicate
   _Sponsorship Tiers_ sections and/or duplicate `id="tiers"` instances.
2. **Security & Tokens** — a drop‑in `security.py` to harden headers and a
   shared `tokens.css` to unify UI look/feel.

---

## 1) Fix duplicate tiers

```bash
# From your project root (the folder that contains "templates/")
python scripts/fix_duplicate_tiers.py .
```

What it does:

- If a single template file accidentally includes the tiers partial twice,
  extras are commented out.
- If multiple `id="tiers"` sections exist, the first keeps `id="tiers"` and
  later ones become `id="tiers-2"`, `id="tiers-3"`, … so anchors resolve to
  the first instance.
- Writes a JSON report to `fix_duplicate_tiers.report.json`.
- Original files are backed up with a `.bak` suffix next to each edited file.

> Tip: If your page legitimately needs another tiers grid, give it
> a different `id` and heading (e.g. `id="tiers-archive"`).

---

## 2) Security hardening (Flask)

1. Copy `security.py` into `app/` (so path: `app/security.py`).
2. In `app/__init__.py`, after you create the Flask app, add:
   ```python
   from app.security import install_security
   install_security(app)
   ```
3. If your app already sets CSP, merge policies accordingly. The CSP here
   supports your YouTube no-cookie iframe by default.

---

## 3) Design tokens

Add a single import for all templates/layouts, for example in your base:

```html
<link
  rel="stylesheet"
  href="{{ url_for('static', filename='css/tokens.css') }}"
/>
```

Use variables in your custom CSS:

```css
.my-card {
  border-radius: var(--fc-radius);
}
```

---

## Notes

- These changes are **non-destructive** and easy to revert via the `.bak` files.
- After running the tiers fix, search your codebase to ensure there’s only one
  intentional include of the tiers partial on a page:
  ```bash
  rg -n "include.*tiers|id=\"tiers\"" templates -S
  ```
