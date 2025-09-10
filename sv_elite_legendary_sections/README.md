# SV-Elite 7.9.3 — Compact-Pro (Split Partials)

This package drops a polished, CSP-safe hero section with a compact donation rail into your Jinja app.

## Files
- `templates/hero_and_fundraiser.html` — Wrapper that includes the two partials and contains CSS + script tags.
- `templates/hero/_story_left_compact.html` — Left story block (badge, titles, subtitle, chips, CTAs).
- `templates/hero/_donation_rail_compact.html` — Right rail (meter, QR + Donate Now, text-to-give, sponsor link, pills).
- `static/js/hero_compact_pro.module.js` — Behavior (reveal, share, meter animate, /api/totals hydrate, QR peer-aware).
- `static/js/qrcode.min.js` — Placeholder. Optional vendor; if missing, fallback UI renders “Open Donate / Copy Link”.

## Backend expectations
- Optional **totals hydrate** endpoint: `GET /api/totals` returns
  ```json
  { "total": 5820, "goal": 10000 }
  ```
  If absent, initial Jinja values are used.

## Integration
1. Copy the `templates/` and `static/` folders into your project.
2. Render `templates/hero_and_fundraiser.html` in your page where the hero should appear.
3. Ensure your CSP allows the module script with `nonce` (already set via `{{ NONCE }}`) and loads `/static/js/hero_compact_pro.module.js`.
4. Provide Jinja vars (optional defaults included):
   - Theme: `theme_hex`
   - Org/team: `team.name` or `team.team_name`
   - Content: `fundraiser_title`, `fundraiser_title_2`, `meta_description`, `cta_label`
   - Links: `stripe_payment_link` or fallback `safe_url_for('main.donate')`
   - Totals: `funds_raised`, `fundraising_goal`
   - Text-to-give: `TEXT_KEYWORD`, `TEXT_SHORTCODE`
   - Announcement/Countdown: `announcement_text`, `event_datetime_iso`

## Notes
- Mobile: QR auto-hides <480px; sticky Donate shows <640px.
- Accessibility: proper `role="meter"`, `aria-valuetext`, and polite live updates.
- UTM decoration: Donate links are auto-decorated with source/medium/campaign and quick-amount when clicked.
