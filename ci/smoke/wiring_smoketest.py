#!/usr/bin/env python3
import os, sys, argparse, json, time
import requests

OK = (200, 301, 302, 307, 308)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.getenv("BASE_URL","http://localhost:5000"))
    ap.add_argument("--token", default=os.getenv("API_TOKEN",""))
    ap.add_argument("--timeout", type=float, default=float(os.getenv("TEST_TIMEOUT","5")))
    args = ap.parse_args()
    base = args.base.rstrip("/")
    tok  = args.token.strip()
    H = {"Authorization": f"Bearer {tok}"} if tok else {}
    print(f"↪ base: {base}")
    failures = []
    def req(method, path, **kw):
        url = base + ("" if path.startswith("/") else "/") + path
        try:
            r = requests.request(method, url, timeout=args.timeout, allow_redirects=False, headers=H|kw.get("headers",{}), data=kw.get("data"))
            ok = r.status_code in OK
            print(f"{method} {path:28} → {r.status_code} {'OK' if ok else 'FAIL'}")
            if not ok: failures.append((method, url, r.status_code, r.text[:200]))
        except Exception as e:
            failures.append((method, url, "ERR", str(e)))
            print(f"{method} {path:28} → ERR  {e}")
    # hits
    for p in ["/", "/healthz", "/version", "/stats"]:
        req("GET", p)
    for p in ["/api/status","/api/stats","/api/donors","/api/payments/readiness"]:
        req("GET", p, headers={"Accept":"application/json"})
    req("GET", "/admin")
    # sms (optional)
    req("GET", "/sms/health")
    req("POST","/sms/webhook", headers={"Content-Type":"application/x-www-form-urlencoded"},
        data={"Body":"Donate","From":"+15550000001","To":"+15550000002"})
    if failures:
        print("\n❌ wiring smoke test FAILED")
        for m,u,c,_ in failures:
            print(f"- {m} {u} → {c}")
        sys.exit(1)
    print("\n✅ wiring looks good!")

if __name__ == "__main__":
    main()
