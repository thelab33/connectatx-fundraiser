# tests/conftest.py
# --- ensure project root is importable as a package ---
import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------------

import os
import importlib
import http.cookies
import pytest

# =========================
# Flask app / client setup
# =========================
@pytest.fixture(scope="session")
def app():
    """
    Create the Flask app for tests.
    We keep CSRF ENABLED to validate enforcement in tests.
    """
    from app import create_app

    flask_app = create_app("app.config.DevelopmentConfig")

    # Test-safe overrides
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=True,        # we want CSRF ON for these tests
        SERVER_NAME="localhost",      # so cookies like csrf_token bind correctly
        PREFERRED_URL_SCHEME="http",
        PROPAGATE_EXCEPTIONS=True,
        SECRET_KEY=os.environ.get("SECRET_KEY", "test-secret-key"),
    )

    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    ctx.pop()


@pytest.fixture()
def client(app):
    """Standard Flask test client bound to the session app."""
    return app.test_client()


# =========================
# CSRF token fixture
# =========================
@pytest.fixture()
def csrf_token(client, app):
    """
    Visit '/' to set the CSRF cookie and return its signed value.
    Also syncs the raw token into the Flask session so Flask-WTF
    validates it correctly.
    """
    resp = client.get("/")  # sets Set-Cookie for csrf_token / csrf_access_token

    # Parse Set-Cookie headers
    cookies = http.cookies.SimpleCookie()
    getlist = getattr(resp.headers, "getlist", None)
    set_cookie_headers = getlist("Set-Cookie") if getlist else [resp.headers.get("Set-Cookie")]
    for header in filter(None, set_cookie_headers):
        cookies.load(header)

    morsel = cookies.get("csrf_token") or cookies.get("csrf_access_token")
    if not morsel:
        pytest.fail("CSRF cookie not found after GET /")

    signed = morsel.value

    # Store cookie on client
    client.set_cookie(morsel.key, signed, path="/")

    # Derive raw token (before the first '.') and sync into session
    raw = signed.split(".")[0].strip('"')
    with client.session_transaction() as sess:
        sess["csrf_token"] = raw

    return signed


# ==========================================
# Reset helpers for clean state
# ==========================================
@pytest.fixture(autouse=True)
def fresh_helpers_module(monkeypatch):
    """
    Reload app.helpers to ensure a clean module state for each test,
    and reset the module-level _seq_counter used by emit_funds_update.
    """
    import app.helpers as helpers
    importlib.reload(helpers)
    try:
        helpers._seq_counter = 0  # type: ignore[attr-defined]
    except Exception:
        pass
    return helpers

