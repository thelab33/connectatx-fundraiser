import pytest
from flask_wtf.csrf import generate_csrf


def _set_csrf(client):
    """Use Flask-WTF generate_csrf to wire session + cookie correctly."""
    with client.session_transaction() as sess:
        token = generate_csrf()       # creates signed token
        sess["csrf_token"] = token    # Flask-WTF will store raw automatically
    # Mirror what Flask normally does: set cookie to same token
    client.set_cookie("csrf_token", token)
    return token


def test_csrf_enforced(client):
    r = client.post("/metrics/click", json={"path": "/"})
    assert r.status_code in (400, 403)


def test_csrf_ok_with_header(client):
    token = _set_csrf(client)
    r = client.post(
        "/metrics/click",
        json={"path": "/ok"},
        headers={"X-CSRFToken": token},
    )
    assert r.status_code == 200

