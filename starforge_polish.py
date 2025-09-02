#!/usr/bin/env python3
# Starforge Polish — Flask/Jinja Hero Finisher
# - Asset pipeline (AVIF/WEBP)
# - CSP (nonce + headers)
# - SSE endpoint (optional)
# - Idempotent, file-safe backups
#
# Usage examples:
#   python starforge_polish.py assets --source-image ./team.jpg
#   python starforge_polish.py csp --app-file app.py --apply
#   python starforge_polish.py sse --app-file app.py --apply
#   python starforge_polish.py partial --path templates/partials/_fc_hero.html.jinja
#   python starforge_polish.py audit --app-file app.py --home-template templates/pages/home.html.jinja

from __future__ import annotations
import argparse, os, sys, re, shutil, textwrap, datetime
from pathlib import Path

# ---------- Optional image libs ----------
AVIF_OK = False
try:
    # pip install pillow pillow-avif-plugin
    from PIL import Image, ImageOps
    try:
        import pillow_avif  # noqa: F401  (module name when installed via pillow-avif-plugin)
        AVIF_OK = True
    except Exception:
        # If plugin isn't present, we'll still do WEBP.
        pass
except Exception:
    Image = None

ROOT = Path.cwd()

# ---------- Utilities ----------
def info(msg): print(f"   • {msg}")
def warn(msg): print(f" ! {msg}")
def ok(msg):   print(f" ✓ {msg}")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        ts  = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = path.with_name(path.name + f".{ts}.bak")
        shutil.copy2(path, bak)
        info(f"Backed up: {path} -> {bak}")

def write_if_missing(path: Path, content: str):
    if path.exists():
        ok(f"Exists: {path} (unchanged)")
        return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    ok(f"Wrote: {path}")
    return True

def upsert_file(path: Path, content: str, only_if_missing=False):
    ensure_dir(path.parent)
    if only_if_missing and path.exists():
        ok(f"Exists: {path} (unchanged)")
        return False
    backup(path)
    path.write_text(content, encoding="utf-8")
    ok(f"Wrote: {path}")
    return True

# ---------- Commands ----------
def cmd_assets(args):
    if Image is None:
        warn("Pillow not available. Install: pip install pillow pillow-avif-plugin")
        sys.exit(1)

    src = Path(args.source_image)
    if not src.exists():
        warn(f"Source image not found: {src}")
        sys.exit(1)

    out_dir = ROOT / "static" / "images" / "hero"
    ensure_dir(out_dir)

    widths = [1920, 1280, 960]
    try:
        im = Image.open(src).convert("RGB")
    except Exception as e:
        warn(f"Failed to open image: {e}")
        sys.exit(1)

    for w in widths:
        im_resized = ImageOps.contain(im, (w, int(w*9/16)), method=Image.LANCZOS)
        webp_path = out_dir / f"hero-{w}.webp"
        im_resized.save(webp_path, format="WEBP", quality=82, method=6)
        ok(f"WEBP: {webp_path}")

        if AVIF_OK:
            avif_path = out_dir / f"hero-{w}.avif"
            # Pillow-AVIF quality 0-100 (lower is more compressed). 50-60 is a good balance.
            im_resized.save(avif_path, format="AVIF", quality=55)
            ok(f"AVIF: {avif_path}")
        else:
            info("AVIF: skipped (install pillow-avif-plugin to enable)")

    # Friendly fallback used by the template when no custom URL is provided
    fallback = ROOT / "static" / "images" / "connect-atx-team.jpg"
    ensure_dir(fallback.parent)
    if not fallback.exists():
        im_fallback = ImageOps.contain(im, (1600, 900), method=Image.LANCZOS)
        im_fallback.save(fallback, format="JPEG", quality=88, optimize=True, progressive=True)
        ok(f"Fallback JPEG: {fallback}")
    else:
        ok(f"Fallback exists: {fallback}")

    ok("Asset pipeline complete.")

def _inject_nonce_and_csp(app_text: str) -> str:
    """Idempotently insert nonce helpers + CSP after_request into a Flask app.py text."""
    added = False

    if "def set_nonce(" not in app_text:
        block = textwrap.dedent("""
        import secrets
        from flask import g

        @app.before_request
        def set_nonce():
            g.csp_nonce = secrets.token_urlsafe(16)

        @app.context_processor
        def inject_nonce():
            return {"NONCE": g.get("csp_nonce", "")}
        """).strip()
        app_text += "\n\n" + block + "\n"
        added = True

    if "def add_starforge_csp(" not in app_text:
        block = textwrap.dedent("""
        @app.after_request
        def add_starforge_csp(resp):
            try:
                from flask import g
                nonce = getattr(g, "csp_nonce", "")
            except Exception:
                nonce = ""
            policy = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'nonce-{nonce}'; "
                "img-src 'self' https: data: blob:; "
                "font-src 'self' https: data:; "
                "connect-src 'self' https: /sse/donations; "
                "frame-src https://pay.stripe.com; "
                "object-src 'none'; base-uri 'self'; form-action 'self' https://pay.stripe.com; "
                "upgrade-insecure-requests"
            )
            resp.headers.setdefault("Content-Security-Policy", policy)
            return resp
        """).strip()
        app_text += "\n\n" + block + "\n"
        added = True

    return app_text, added

def cmd_csp(args):
    app_file = Path(args.app_file)
    if not app_file.exists():
        warn(f"App file not found: {app_file}")
        sys.exit(1)
    text = app_file.read_text(encoding="utf-8")
    new_text, added = _inject_nonce_and_csp(text)
    if not added:
        ok("CSP + nonce already present (no changes).")
        return
    if args.apply:
        upsert_file(app_file, new_text)
        ok("CSP/nonce applied to app.")
    else:
        info("Preview (use --apply to write):\n")
        print(new_text)

def cmd_sse(args):
    app_file = Path(args.app_file)
    if not app_file.exists():
        warn(f"App file not found: {app_file}")
        sys.exit(1)
    text = app_file.read_text(encoding="utf-8")
    if "/sse/donations" in text:
        ok("SSE endpoint already present (no changes).")
        return
    block = textwrap.dedent("""
    # --- Starforge SSE: recent donations stream ---
    from flask import Response, stream_with_context
    import json, time

    @app.route("/sse/donations")
    def sse_donations():
        def gen():
            # Replace this with your real queue/broker.
            # You can yield "event: donation\\n" + f"data: {{...}}\\n\\n" to push updates.
            while True:
                yield "event: ping\\n" + "data: {}\\n\\n"
                time.sleep(15)
        return Response(stream_with_context(gen()), mimetype="text/event-stream")
    """).strip()

    new_text = text + "\n\n" + block + "\n"
    if args.apply:
        upsert_file(app_file, new_text)
        ok("SSE endpoint added.")
    else:
        info("Preview (use --apply to write):\n")
        print(new_text)

def cmd_partial(args):
    path = Path(args.path)
    tpl = textwrap.dedent("""\
    {# Starforge partial placeholder.
       Put your FC HERO — SV-Elite 6.1 block here (HTML+CSS+JS) exactly as provided.
       This file exists so your code can {% include "partials/_fc_hero.html.jinja" %}.
       Keeps upgrades isolated and lets this script manage assets/CSP/SSE around it.
    #}
    """)
    wrote = write_if_missing(path, tpl)
    if wrote:
        info("Paste your full hero snippet into this partial and save.")
    else:
        info("Partial already exists. No changes.")

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

def cmd_audit(args):
    problems = 0

    # 1) Assets
    hero_dir = ROOT / "static" / "images" / "hero"
    needed = [hero_dir / f"hero-{w}.webp" for w in (1920, 1280, 960)]
    missing = [p for p in needed if not p.exists()]
    if missing:
        problems += 1
        warn("Missing WEBP hero derivatives:")
        for p in missing: info(str(p))
        info("Run: python starforge_polish.py assets --source-image /path/to/team.jpg")
    else:
        ok("Hero WEBP assets present.")

    # 2) CSP/nonce
    if args.app_file:
        app_file = Path(args.app_file)
        text = _read(app_file)
        if "def set_nonce(" in text and "def add_starforge_csp(" in text:
            ok("CSP/nonce wiring found in app.")
        else:
            problems += 1
            warn("CSP/nonce not detected in app.")
            info("Run: python starforge_polish.py csp --app-file app.py --apply")

    # 3) Partial include
    if args.home_template:
        home = Path(args.home_template)
        ht = _read(home)
        if '_fc_hero.html.jinja' in ht:
            ok("Hero partial appears included on home template.")
        else:
            problems += 1
            warn(f"Hero include not found in {home}.")
            info('Add: {% include "partials/_fc_hero.html.jinja" %} where your hero should render.')

    # 4) Fallback image
    fallback = ROOT / "static" / "images" / "connect-atx-team.jpg"
    if fallback.exists():
        ok("Fallback JPEG present.")
    else:
        problems += 1
        warn(f"Fallback JPEG missing: {fallback}")
        info("This is optional, but recommended. It’s created by the assets command.")

    if problems == 0:
        ok("Audit clean. You’re Starforge-ready.")
    else:
        warn("Audit finished with items above. Fixes noted per section.")

# ---------- Main ----------
def main():
    p = argparse.ArgumentParser(description="Starforge Polish for Flask/Jinja")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_assets = sub.add_parser("assets", help="Generate AVIF/WEBP hero assets")
    s_assets.add_argument("--source-image", required=True, help="Source image (large, high quality)")
    s_assets.set_defaults(func=cmd_assets)

    s_csp = sub.add_parser("csp", help="Inject nonce + CSP headers into Flask app")
    s_csp.add_argument("--app-file", required=True, help="Path to app.py")
    s_csp.add_argument("--apply", action="store_true", help="Write changes instead of preview")
    s_csp.set_defaults(func=cmd_csp)

    s_sse = sub.add_parser("sse", help="Append a simple SSE endpoint for donor ticker")
    s_sse.add_argument("--app-file", required=True, help="Path to app.py")
    s_sse.add_argument("--apply", action="store_true", help="Write changes instead of preview")
    s_sse.set_defaults(func=cmd_sse)

    s_partial = sub.add_parser("partial", help="Create the hero partial file if missing")
    s_partial.add_argument("--path", default="templates/partials/_fc_hero.html.jinja")
    s_partial.set_defaults(func=cmd_partial)

    s_audit = sub.add_parser("audit", help="Check assets, CSP, and template include")
    s_audit.add_argument("--app-file", help="Path to app.py")
    s_audit.add_argument("--home-template", help="Path to home.html.jinja (to verify include)")
    s_audit.set_defaults(func=cmd_audit)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

