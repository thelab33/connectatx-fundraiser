#!/usr/bin/env python3
"""
Move inline <script> tags in Jinja templates to static JS files and rewrite the templates.
- Extracts to: app/static/js/extracted/<template_path>__<index>.js
- Rewrites to: <script type="module" src="{{ url_for('static', filename='js/extracted/…') }}"></script>
- Skips JSON-LD (keeps inline) but adds nonce="{{ csp_nonce }}" to them.
- Backs up edited files once (.bak).
Usage:
  python tools/move_inline_js.py --root app --apply
"""
import argparse
import re
from pathlib import Path
import shutil

SCRIPT_RE = re.compile(
    r"(?s)<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>"
)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_once(path: Path, content: str):
    if path.exists():
        existing = path.read_text(encoding="utf-8", errors="ignore")
        if existing == content:
            return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True

def backup_once(path: Path):
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(path, bak)

def should_extract(attrs: str):
    # Extract if it’s regular JS; keep inline if JSON-LD
    a = attrs.lower()
    if 'type=' in a:
        # normalize
        m = re.search(r'type\s*=\s*["\']([^"\']+)["\']', a)
        if m:
            t = m.group(1).strip()
            if t == "application/ld+json":
                return False
            # extract for classic, module, text/javascript, etc.
            return True
    # no type => likely JS, extract
    return True

def add_nonce(attrs: str):
    # If nonce already present, leave it
    if re.search(r'\bnonce\s*=\s*["\']', attrs): return attrs
    # insert nonce attribute before closing bracket
    return attrs.strip() + ' nonce="{{ csp_nonce }}"'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="app", help="Your Flask app folder (with templates/, static/)")
    ap.add_argument("--apply", action="store_true", help="Write changes (otherwise dry-run)")
    ap.add_argument("--v", default="1.0.0", help="Static version param")
    args = ap.parse_args()

    app_root = Path(args.root).resolve()
    tpl_root = app_root / "templates"
    js_out_root = app_root / "static" / "js" / "extracted"
    ensure_dir(js_out_root)

    edited = 0
    created = 0
    skipped_jsonld = 0

    for tpl in tpl_root.rglob("*.html"):
        text = tpl.read_text(encoding="utf-8", errors="ignore")
        changed = False
        new_text_parts = []
        last_idx = 0
        idx = 0

        for m in SCRIPT_RE.finditer(text):
            idx += 1
            attrs = m.group("attrs") or ""
            body = m.group("body") or ""
            # Jinja templates often include whitespace-only scripts—skip empty
            if not body.strip():
                continue

            # append text before this script
            new_text_parts.append(text[last_idx:m.start()])

            if should_extract(attrs):
                # Build a deterministic filename: templates path with slashes -> double underscore
                tpl_rel = tpl.relative_to(tpl_root)
                stem = str(tpl_rel).replace("/", "__").replace("\\", "__")
                out_name = f"{stem}__{idx}.js"
                out_path = js_out_root / out_name

                if not out_path.exists():
                    if args.apply:
                        write_once(out_path, body.strip() + "\n")
                        created += 1
                    print(f"+ JS  : {out_path}")

                # replacement tag
                src = "{{ url_for('static', filename='js/extracted/%s', v='%s') }}" % (out_name, args.v)
                repl = f'<script type="module" src="{src}"></script>'
                new_text_parts.append(repl)
                changed = True
            else:
                # JSON-LD: keep inline, add nonce
                new_attrs = add_nonce(attrs)
                new_text_parts.append(f"<script{new_attrs}>{body}</script>")
                skipped_jsonld += 1

            last_idx = m.end()

        new_text_parts.append(text[last_idx:])
        new_text = "".join(new_text_parts)

        if changed and new_text != text:
            print(f"* TPL : {tpl}")
            if args.apply:
                backup_once(tpl)
                tpl.write_text(new_text, encoding="utf-8")
                edited += 1
        elif changed:
            print(f"= TPL unchanged (no diff): {tpl}")

    print("\nSummary:")
    print(f" - Templates edited : {edited}")
    print(f" - JS files created : {created}")
    print(f" - JSON-LD kept inline (nonce added): {skipped_jsonld}")
    print("\nNext:")
    print(" 1) Add nonce context to your app (once):")
    print("""
# app/__init__.py (or app factory)
import secrets
from flask import g

@app.context_processor
def inject_csp_nonce():
    if not hasattr(g, "csp_nonce"):
        g.csp_nonce = secrets.token_urlsafe(16)
    return {"csp_nonce": g.csp_nonce}
""")
    print(" 2) In your CSP, allow the nonce:")
    print("""
# with Flask-Talisman or your own headers:
# script-src should include the runtime nonce value; with Talisman you can pass a callable.
from flask import g
csp = {
  "default-src": ["'self'"],
  "script-src": ["'self'", lambda: f"'nonce-{g.csp_nonce}'"],
  "style-src": ["'self'"],
  "img-src": ["'self'", "data:"],
  "connect-src": ["'self'"],
}
""")

if __name__ == "__main__":
    main()
