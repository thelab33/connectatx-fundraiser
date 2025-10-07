# FundChamps Widgets Kit v1

Enterprise-ready, reusable widgets + a **Header — Elite Max v5.0** with slots for:
- Announcement ticker (live shoutouts, sponsor messages, system notices)
- Sponsor ribbon (tier-aware logos)
- QR modal (scan-to-give)
- Command palette & keyboard shortcuts

## Files
- `templates/partials/header_elitemax_v5.html` (drop-in header)
- `templates/partials/widgets/announcement_ticker.html`
- `templates/partials/widgets/sponsor_ribbon.html`
- `templates/partials/widgets/qr_modal.html`
- `templates/partials/widgets/command_palette.html`
- `static/css/fc-tokens.css` + `static/css/fc-widgets.css`
- `static/js/fc-widgets.js` (vanilla, ES module)

## Usage (Flask/Jinja)
```jinja
{% set ticker_items = [
  {"pill":"Local Brewery","text":"Cheers to champions — beer for the win!","icon":"🍻","href":"https://example.com"},
  {"pill":"Leaderboard","text":"Live shoutouts — top supporters!","icon":"🥇","href":"#leaderboard"}
] %}
{% include "partials/header_elitemax_v5.html" with context %}
{% include "partials/widgets/qr_modal.html" with context %}
{% include "partials/widgets/command_palette.html" with context %}
```

### JSON feed option
Provide `ticker_feed_url` pointing to `GET /api/ticker?campaign=...` that returns either an array or `{ "items": [...] }` of `{ pill, text, icon, href }`.

### CSP
Scripts use `type="module"` for `/static/js/fc-widgets.js`. If your CSP blocks external scripts, allow `'self'` for `script-src` or inline-hash. Inline snippets use `nonce_attr()` in templates.

### Keyboard
- `D` Donate (opens modal if present)
- `S` Share
- `L` Leaderboard
- `P` Pause ticker
- `K` Command palette

### Public API
`window.FCWidgets.init()` auto-runs; you can re-init parts with `FCWidgets.initTicker()`, etc.
`window.FundChampsHeader.setProgress({raised, goal})` and `setCTA({label, href})` are exposed by the header.