# FundChamps — Turnkey Fundraising Platform

Launch fundraisers, memberships, and sponsor leaderboards for youth teams, nonprofits, and clubs.

## Quick Start
See **BUILD.md** for setup. Seed sample data with:
```bash
python -m app.seed seeds/seed.json  # or flask seed load seeds/seed.json
```

## Roadmap / TODOs
- Stripe webhook hardening (idempotency keys, signature verify, retries)
- VIP leaderboard rules & tie-breakers
- Multi-tenant orgs, custom domains, theming
- Admin dashboard polish (impersonation, audit log)
- PII & security headers pass (CSP, HSTS, cookies)
- Email receipts & PDF invoices

_Last updated: 2025-08-30 04:36 UTC_
