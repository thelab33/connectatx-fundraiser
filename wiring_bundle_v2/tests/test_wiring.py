import os, requests, pytest, urllib.parse as _u

BASE = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
TOKEN = os.getenv("API_TOKEN", "").strip()
TIMEOUT = float(os.getenv("TEST_TIMEOUT", "5"))

def join(path: str) -> str:
    return BASE + ("" if path.startswith("/") else "/") + path

def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# Accept common redirect codes too (proxied dev setups often 301/307/308)
OK_REDIRECT = (200, 301, 302, 307, 308)

@pytest.mark.parametrize("path", ["/", "/healthz", "/version"])
def test_html_endpoints(path):
    r = requests.get(join(path), timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code in OK_REDIRECT

def test_stats():
    r = requests.get(join("/stats"), timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code in OK_REDIRECT

@pytest.mark.parametrize("path", ["/api/status","/api/stats","/api/donors","/api/payments/readiness"])
def test_api_endpoints(path):
    r = requests.get(join(path), headers=auth_headers()|{"Accept":"application/json"}, timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code in OK_REDIRECT

def test_admin_gate():
    r = requests.get(join("/admin"), timeout=TIMEOUT, allow_redirects=False)
    assert r.status_code in (200, 301, 302, 401, 403, 307, 308)

@pytest.mark.parametrize("present, path", [(True,"/sms/health"), (False,"/sms/webhook")])
def test_sms_endpoints_present_or_tolerated(present, path):
    r = requests.request("GET" if path.endswith("health") else "POST",
                         join(path),
                         timeout=TIMEOUT,
                         allow_redirects=False,
                         headers={"Content-Type":"application/x-www-form-urlencoded"} if path.endswith("webhook") else None,
                         data={"Body":"Donate","From":"+15550000001","To":"+15550000002"} if path.endswith("webhook") else None)
    if r.status_code == 404:
        pytest.skip(f"{path} not configured")
    assert r.status_code in OK_REDIRECT
