#!/usr/bin/env python3
"""
FundChamps Wiring Smoke Test
---------------------------------
Lightweight endpoint check for all core routes.
- Skips removed readiness endpoint
- Colored output + summary
"""

import os
import sys
import argparse
import requests

OK = {200, 301, 302, 307, 308}

# ANSI colors for pretty output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.getenv("BASE_URL", "http://localhost:5000"))
    ap.add_argument("--token", default=os.getenv("API_TOKEN", ""))
    ap.add_argument("--timeout", type=float, default=float(os.getenv("TEST_TIMEOUT", "5")))
    args = ap.parse_args()

    base = args.base.rstrip("/")
    headers = {"Authorization": f"Bearer {args.token.strip()}"} if args.token else {}

    print(f"↪ base: {base}")

    failures = []

    def req(method: str, path: str, **kw):
        url = f"{base}{path if path.startswith('/') else '/' + path}"
        try:
            r = requests.request(
                method,
                url,
                timeout=args.timeout,
                allow_redirects=False,
                headers={**headers, **kw.get("headers", {})},
                data=kw.get("data"),
            )
            ok = r.status_code in OK
            color = GREEN if ok else RED
            print(f"{method:<4} {path:<30} → {color}{r.status_code}{RESET} {'OK' if ok else 'FAIL'}")
            if not ok:
                failures.append((method, url, r.status_code, r.text[:200]))
        except Exception as e:
            failures.append((method, url, "ERR", str(e)))
            print(f"{method:<4} {path:<30} → {YELLOW}ERR{RESET}  {e}")

    # Core pages
    for path in ["/", "/healthz", "/version", "/stats"]:
        req("GET", path)

    # API routes (no more readiness)
    for path in ["/api/status", "/api/stats", "/api/donors"]:
        req("GET", path, headers={"Accept": "application/json"})

    # Admin redirect check
    req("GET", "/admin")

    # SMS health + webhook
    req("GET", "/sms/health")
    req(
        "POST",
        "/sms/webhook",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"Body": "Donate", "From": "+15550000001", "To": "+15550000002"},
    )

    # Results summary
    print("\n──────────────────────────────────────")
    if failures:
        print(f"{RED}❌ wiring smoke test FAILED{RESET}")
        for m, u, c, _ in failures:
            print(f"- {m} {u} → {c}")
        sys.exit(1)
    else:
        print(f"{GREEN}✅ all routes responded successfully!{RESET}")


if __name__ == "__main__":
    main()

