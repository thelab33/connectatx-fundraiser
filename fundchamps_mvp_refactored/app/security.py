
import os, base64, secrets
from flask import g, request

def _nonce(nbytes=16):
    return base64.b64encode(secrets.token_bytes(nbytes)).decode('ascii')

def install_security(app):
    @app.before_request
    def _set_nonce():
        g.csp_nonce = _nonce()

    @app.context_processor
    def _inject_nonce():
        # Jinja helper: {{ csp_nonce() }}
        return {'csp_nonce': lambda: g.get('csp_nonce', '')}

    @app.after_request
    def _secure_headers(resp):
        # Basic hardening (tune for your stack/CDN/analytics)
        resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
        resp.headers.setdefault('X-Frame-Options', 'DENY')
        resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        resp.headers.setdefault('Permissions-Policy',
            "geolocation=(), camera=(), microphone=(), fullscreen=(self)")

        # HSTS (enable only behind HTTPS)
        if request.is_secure or os.getenv('FORCE_HSTS', '0') == '1':
            resp.headers.setdefault('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')

        # CSP with runtime nonce
        nonce = g.get('csp_nonce', '')
        # Adjust connect-src/img-src/script-src/style-src to your needs
        csp = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' https: data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "script-src 'self' 'nonce-{}'; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-src https:; "
            "upgrade-insecure-requests"
        ).format(nonce)
        # Only set if not already set by a proxy
        resp.headers.setdefault('Content-Security-Policy', csp)
        return resp
