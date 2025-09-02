# app/security.py — tiny, dependency-free security hardening
from flask import request, g

DEFAULT_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'nonce-{nonce}'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data: https:; "
    "connect-src 'self' https:; "
    "frame-src https://www.youtube-nocookie.com; "
    "object-src 'none'; base-uri 'self'; form-action 'self'"
)

def install_security(app, *, csp=DEFAULT_CSP):
    @app.after_request
    def _secure(resp):
        # Content Security Policy with dynamic nonce
        nonce = getattr(g, "csp_nonce", None) or getattr(request, "csp_nonce", None) or ""
        resp.headers["Content-Security-Policy"] = csp.format(nonce=nonce)
        # Other headers
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
        resp.headers.setdefault("Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=()")
        resp.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        resp.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        # Reasonable HSTS (enable only when HTTPS is guaranteed)
        if request.headers.get("X-Forwarded-Proto", request.scheme) == "https":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        return resp
    return app
