"""
pytest wiring validator for FundChamps / SV-Elite
Run:
  BASE_URL=http://localhost:5000 API_TOKEN=... pytest -q
"""
import os
import pytest
import requests

BASE = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
TOKEN = os.getenv("API_TOKEN", "").strip()
TIMEOUT = float(os.getenv("WIRING_TIMEOUT", "8"))

def join(path: str) -> str:
    return BASE.rstrip("/") + (path if path.startswith("/") else "/" + path)

def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

@pytest.mark.parametrize("path", ["/", "/healthz", "/version"])
def test_html_endpoints(path):
    r = requests.get(join(path), timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code in (200, 301, 302)
    assert "Content-Security-Policy" in r.headers
    assert "X-Request-ID" in r.headers

def test_stats():
    r = requests.get(join("/stats"), timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code == 200
    assert "Content-Security-Policy" in r.headers
    assert "X-Request-ID" in r.headers
    assert "ETag" in r.headers
    assert "Cache-Control" in r.headers
    data = r.json()
    for k in ("team","raised","goal","percent","sponsors_total","sponsors_count"):
        assert k in data

@pytest.mark.parametrize("path", ["/api/status","/api/stats","/api/donors","/api/payments/readiness"])
def test_api_endpoints(path):
    r = requests.get(join(path), headers=auth_headers()|{"Accept":"application/json"}, timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code == 200
    assert "Content-Security-Policy" in r.headers
    assert "X-Request-ID" in r.headers
    assert r.headers.get("X-Content-Type-Options","").lower() == "nosniff"

def test_admin_gate():
    r = requests.get(join("/admin"), timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code in (200, 301, 302, 401, 403)
    assert "Content-Security-Policy" in r.headers
    assert "X-Request-ID" in r.headers

@pytest.mark.parametrize("present, path", [(True,"/sms/health"), (False,"/sms/webhook")])
def test_sms_endpoints_present_or_tolerated(present, path):
    # These routes are optional; if not present, we tolerate 404 (skip-like semantics).
    r = requests.request("GET" if path.endswith("health") else "POST",
                         join(path),
                         timeout=TIMEOUT,
                         allow_redirects=False,
                         headers={"Content-Type":"application/x-www-form-urlencoded"} if path.endswith("webhook") else None,
                         data={"Body":"Donate","From":"+15550000001","To":"+15550000002"} if path.endswith("webhook") else None)
    if r.status_code == 404:
        pytest.skip(f"{path} not configured")
    assert r.status_code == 200
    if path.endswith("webhook"):
        assert r.text.strip().startswith("<?xml")
        assert "<Response>" in r.text
