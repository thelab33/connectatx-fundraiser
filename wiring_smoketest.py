#!/usr/bin/env python3
"""
Wiring Smoke Test for FundChamps / SV-Elite stack
- One-file runner (no pytest required)
- Hits key HTML, API, Admin, and SMS endpoints
- Asserts basic headers (CSP, X-Request-ID, Cache-Control/ETag where applicable)
- Accepts Bearer token for /api if you enforce auth

Usage:
  python wiring_smoketest.py --base http://localhost:5000 --token "YOUR_API_TOKEN"
  # Or via env:
  BASE_URL=http://localhost:5000 API_TOKEN=YOUR_API_TOKEN python wiring_smoketest.py
"""
import argparse
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

DEFAULT_TIMEOUT = float(os.getenv("WIRING_TIMEOUT", "8"))
DEFAULT_BASE = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
DEFAULT_TOKEN = os.getenv("API_TOKEN", "").strip()

GREEN = "\033[92m"
YELL = "\033[93m"
RED   = "\033[91m"
DIM   = "\033[2m"
ENDC  = "\033[0m"

def color(s, c):
    return f"{c}{s}{ENDC}"

def join(base: str, path: str) -> str:
    return base.rstrip("/") + (path if path.startswith("/") else "/" + path)

def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}

def want_header(resp: requests.Response, name: str) -> bool:
    return any(h.lower() == name.lower() for h in resp.headers.keys())

def check_headers(resp: requests.Response, *, want_csp: bool = True, want_request_id: bool = True, want_nosniff: bool = False):
    ok = True
    if want_csp and not want_header(resp, "Content-Security-Policy"):
        ok = False
    if want_request_id and not want_header(resp, "X-Request-ID"):
        ok = False
    if want_nosniff and resp.headers.get("X-Content-Type-Options", "").lower() != "nosniff":
        ok = False
    return ok

def get_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return None

class Runner:
    def __init__(self, base: str, token: str = ""):
        self.base = base.rstrip("/")
        self.token = token
        self.hard_fail = 0
        self.soft_warn = 0
        self.tests: List[Tuple[str, str, str]] = []  # (name, status, note)

    def log(self, name: str, ok: bool, note: str = "", warn: bool = False):
        status = color("OK", GREEN) if ok and not warn else (color("WARN", YELL) if warn else color("ERR", RED))
        if not ok and not warn:
            self.hard_fail += 1
        if warn:
            self.soft_warn += 1
        self.tests.append((name, status, note))

    def _req(self, method: str, path: str, *, headers: Optional[Dict[str, str]] = None, **kw):
        url = join(self.base, path)
        h = dict(headers or {})
        if path.startswith("/api"):
            h.setdefault("Accept", "application/json")
            h.update(auth_headers(self.token))
        try:
            resp = requests.request(method, url, headers=h, timeout=DEFAULT_TIMEOUT, allow_redirects=False, **kw)
            return resp, None
        except Exception as e:
            return None, str(e)

    # Tests
    def test_root(self):
        name = "GET /"
        resp, err = self._req("GET", "/")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True)
        note = f"status={resp.status_code}"
        self.log(name, ok, note)

    def test_health(self):
        name = "GET /healthz"
        resp, err = self._req("GET", "/healthz")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True, want_nosniff=False)
        data = get_json(resp) or {}
        ok = ok and (data.get("status") == "ok")
        self.log(name, ok, f"status={resp.status_code} body_keys={list(data.keys())}")

    def test_version(self):
        name = "GET /version"
        resp, err = self._req("GET", "/version")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True)
        data = get_json(resp) or {}
        ok = ok and ("version" in data)
        self.log(name, ok, f"status={resp.status_code} version={data.get('version')}")

    def test_stats(self):
        name = "GET /stats"
        resp, err = self._req("GET", "/stats")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True)
        ok = ok and ("ETag" in resp.headers and "Cache-Control" in resp.headers)
        data = get_json(resp) or {}
        must_keys = {"team","raised","goal","percent","sponsors_total","sponsors_count"}
        ok = ok and must_keys.issubset(set(data.keys()))
        self.log(name, ok, f"status={resp.status_code} etag={'ETag' in resp.headers} keys={list(data.keys())}")

    def test_api_status(self):
        name = "GET /api/status"
        resp, err = self._req("GET", "/api/status")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True, want_nosniff=True)
        data = get_json(resp) or {}
        ok = ok and (data.get("status") == "ok")
        self.log(name, ok, f"status={resp.status_code}")

    def test_api_stats(self):
        name = "GET /api/stats"
        resp, err = self._req("GET", "/api/stats")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True, want_nosniff=True)
        ok = ok and ("ETag" in resp.headers and "Cache-Control" in resp.headers)
        data = get_json(resp) or {}
        must = {"raised","goal","percent","leaderboard"}
        ok = ok and must.issubset(set(data.keys()))
        self.log(name, ok, f"status={resp.status_code} etag={'ETag' in resp.headers} keys={list(data.keys())}")

    def test_api_donors(self):
        name = "GET /api/donors"
        resp, err = self._req("GET", "/api/donors")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True, want_nosniff=True)
        # donors may be [] on fresh DB
        try:
            data = resp.json()
            ok = ok and isinstance(data, list)
        except Exception:
            ok = False
        self.log(name, ok, f"status={resp.status_code}")

    def test_api_payments(self):
        name = "GET /api/payments/readiness"
        resp, err = self._req("GET", "/api/payments/readiness")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True, want_nosniff=True)
        data = get_json(resp) or {}
        ok = ok and {"stripe_ready","stripe_public_key"}.issubset(data.keys())
        self.log(name, ok, f"status={resp.status_code}")

    def test_admin(self):
        name = "GET /admin"
        resp, err = self._req("GET", "/admin")
        if err or resp is None:
            self.log(name, False, err or "no response"); return
        # Accept 200 (open), 302 (login), or 401/403 (protected)
        ok = resp.status_code in (200,301,302,401,403)
        ok = ok and check_headers(resp, want_csp=True, want_request_id=True)
        self.log(name, ok, f"status={resp.status_code}")

    def test_sms_health(self):
        name = "GET /sms/health"
        resp, err = self._req("GET", "/sms/health")
        if err or resp is None:
            # health is optional → warn, not hard fail
            self.log(name, True, f"skipped: {err}", warn=True); return
        ok = (resp.status_code == 200) and check_headers(resp, want_csp=True, want_request_id=True)
        self.log(name, ok, f"status={resp.status_code}")

    def test_sms_webhook(self):
        name = "POST /sms/webhook"
        resp, err = self._req("POST", "/sms/webhook",
                              headers={"Content-Type": "application/x-www-form-urlencoded"},
                              data={"Body":"Donate", "From":"+15555550123", "To":"+15555550999"})
        if err or resp is None:
            # optional → warn, not hard fail
            self.log(name, True, f"skipped: {err}", warn=True); return
        txt = resp.text.strip()
        ok = (resp.status_code == 200) and txt.startswith("<?xml") and "<Response>" in txt
        self.log(name, ok, f"status={resp.status_code} body_len={len(txt)}")

    def run(self):
        print(f"\nWiring Smoke Test → base={self.base!r} token={'yes' if self.token else 'no'} timeout={DEFAULT_TIMEOUT}s\n")
        start = time.time()

        self.test_root()
        self.test_health()
        self.test_version()
        self.test_stats()
        self.test_api_status()
        self.test_api_stats()
        self.test_api_donors()
        self.test_api_payments()
        self.test_admin()
        self.test_sms_health()
        self.test_sms_webhook()

        dur = (time.time() - start) * 1000.0
        for name, status, note in self.tests:
            print(f"{status:>8}  {name:<28} {DIM}{note}{ENDC}")
        print("\nSummary: " +
              color(f"{len(self.tests)} checks", GREEN) + " — " +
              color(f"{self.hard_fail} errors", RED) + ", " +
              color(f"{self.soft_warn} warnings", YELL) +
              f"  ({dur:.0f}ms)")

        return 0 if self.hard_fail == 0 else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE, help="Base URL (default: %(default)s)")
    ap.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token for /api/* (optional)")
    args = ap.parse_args()
    r = Runner(args.base, args.token)
    rc = r.run()
    sys.exit(rc)

if __name__ == "__main__":
    main()
