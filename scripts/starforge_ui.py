
#!/usr/bin/env python3
"""
starforge_ui.py — FundChamps/Connect ATX Elite
Pro UI/UX polish helper.

Features
- Generate brand token CSS from a hex color (with RGB var for Tailwind)
- Sanitize Jinja/CSS conflicts: fixes "{#" inside <style> blocks
- Create a dev styleguide page to preview buttons/cards/forms
- Optimize images (optional) to webp/avif if Pillow is available
- Safe by default: backups every file it modifies

Usage
  python starforge_ui.py tokens --brand "#facc15" --out app/static/css/brand.tokens.css
  python starforge_ui.py sanitize --root app/templates
  python starforge_ui.py styleguide --out app/templates/dev/styleguide.html
  python starforge_ui.py images --root app/static/images
  python starforge_ui.py all      # run tokens+sanitize+styleguide

"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    s = hex_color.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join(ch*2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return r, g, b


def write_brand_tokens(brand: str, out_path: Path) -> str:
    r, g, b = hex_to_rgb(brand)
    css = f""":root{{
  --fc-brand: {brand};
  --fc-brand-rgb: {r} {g} {b};
  --fc-brand-50:  color-mix(in srgb, var(--fc-brand) 12%, transparent);
  --fc-brand-100: color-mix(in srgb, var(--fc-brand) 18%, transparent);
  --fc-brand-200: color-mix(in srgb, var(--fc-brand) 26%, transparent);
  --fc-brand-300: color-mix(in srgb, var(--fc-brand) 42%, #000);
}}
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(css, encoding="utf-8")
    return css


STYLE_OPEN_RE = re.compile(r"<style\b[^>]*>", re.IGNORECASE)
STYLE_CLOSE_RE = re.compile(r"</style>", re.IGNORECASE)


def _sanitize_css_block(css_text: str) -> Tuple[str, int]:
    """
    Replace any '{#' with '{ #' to avoid Jinja comment open in CSS.
    Keep changes minimal; whitespace is CSS-safe.
    """
    count = css_text.count("{#")
    if count:
        css_text = css_text.replace("{#", "{ #")
    return css_text, count


def sanitize_template_comments(path: Path) -> int:
    """
    Scan a single template. Only alter contents inside <style>...</style>.
    Create a .bak alongside before writing changes.
    Return number of replacements.
    """
    text = path.read_text(encoding="utf-8")
    idx = 0
    total = 0
    pieces = []
    while True:
        m_open = STYLE_OPEN_RE.search(text, idx)
        if not m_open:
            pieces.append(text[idx:])
            break
        start = m_open.end()
        pieces.append(text[idx:start])
        m_close = STYLE_CLOSE_RE.search(text, start)
        if not m_close:
            # malformed; skip sanitizing
            pieces.append(text[start:])
            break
        css_block = text[start:m_close.start()]
        fixed, n = _sanitize_css_block(css_block)
        total += n
        pieces.append(fixed)
        idx = m_close.start()
    if total:
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(text, encoding="utf-8")
        path.write_text("".join(pieces), encoding="utf-8")
    return total


def walk_templates(root: Path) -> Iterable[Path]:
    for ext in ("*.html", "*.jinja", "*.jinja2"):
        yield from root.rglob(ext)


STYLEGUIDE_TEMPLATE = """{% extends "base.html" %}
{% set page_description = "Developer styleguide — components & tokens preview." %}
{% block head_title %}Styleguide — {{ super() }}{% endblock %}

{% block hero %}
<section class="relative fc-band fc-band--tint">
  <div class="hero-aura"></div>
  <div class="container mx-auto px-4">
    <p class="eyebrow">Developer</p>
    <h1 class="display mb-2">Styleguide</h1>
    <p class="lede max-w-2xl">Buttons, cards, forms, and brand tokens preview. Use this page during UI polish only.</p>
  </div>
</section>
{% endblock %}

{% block content %}
<section class="container mx-auto px-4 fc-band grid gap-8">
  <div class="grid md:grid-cols-2 gap-6">
    <div class="card p-5">
      <h2 class="text-xl font-extrabold mb-3">Buttons</h2>
      <div class="flex flex-wrap gap-3">
        <button class="btn btn-primary">Primary</button>
        <button class="btn btn-ghost">Ghost</button>
        <a href="#" class="btn btn-primary">Link Button</a>
      </div>
    </div>
    <div class="card p-5">
      <h2 class="text-xl font-extrabold mb-3">Badges & Chips</h2>
      <div class="flex flex-wrap gap-2">
        <span class="badge">Badge</span>
        <span class="chip">Chip</span>
        <span class="badge">Trusted</span>
      </div>
    </div>
  </div>

  <div class="card p-5">
    <h2 class="text-xl font-extrabold mb-3">Form (floating labels)</h2>
    <form class="max-w-md">
      <div class="input-group">
        <input id="sg-email" type="email" placeholder=" " required />
        <label for="sg-email">Email</label>
        <small class="input-helper">We never share your email.</small>
      </div>
      <div class="input-group">
        <textarea id="sg-msg" placeholder=" " rows="3"></textarea>
        <label for="sg-msg">Message</label>
      </div>
      <button class="btn btn-primary">Submit</button>
    </form>
  </div>

  <div class="card p-5">
    <h2 class="text-xl font-extrabold mb-3">Tokens</h2>
    <pre class="text-sm opacity-80"><code>:root { --fc-brand: var(--fc-brand); }</code></pre>
  </div>
</section>
{% endblock %}
"""


def write_styleguide(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(STYLEGUIDE_TEMPLATE, encoding="utf-8")


def optimize_images(root: Path) -> int:
    """
    Convert PNG/JPEG to WebP (and AVIF if Pillow has plugin). Skips if Pillow missing.
    Returns number of files written.
    """
    try:
        from PIL import Image
    except Exception:
        return 0

    written = 0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        try:
            im = Image.open(p).convert("RGBA")
            webp = p.with_suffix(".webp")
            im.save(webp, "WEBP", quality=86, method=6)
            written += 1
            # AVIF if available
            try:
                avif = p.with_suffix(".avif")
                im.save(avif, "AVIF", quality=60)
                written += 1
            except Exception:
                pass
        except Exception:
            pass
    return written


def main():
    ap = argparse.ArgumentParser(prog="starforge_ui", description="Pro polish helpers for UI/UX.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_tokens = sub.add_parser("tokens", help="Write brand token CSS")
    ap_tokens.add_argument("--brand", default="#facc15", help="Hex brand color")
    ap_tokens.add_argument("--out", default="app/static/css/brand.tokens.css")

    ap_san = sub.add_parser("sanitize", help="Fix '{#' inside <style> in templates")
    ap_san.add_argument("--root", default="app/templates", help="Templates root")

    ap_sg = sub.add_parser("styleguide", help="Create dev styleguide page")
    ap_sg.add_argument("--out", default="app/templates/dev/styleguide.html")

    ap_img = sub.add_parser("images", help="Optimize images to webp/avif")
    ap_img.add_argument("--root", default="app/static/images")

    sub.add_parser("all", help="Run tokens + sanitize + styleguide")

    args = ap.parse_args()

    if args.cmd == "tokens":
        css = write_brand_tokens(args.brand, Path(args.out))
        print(f"Wrote tokens → {args.out}\n{css}")
        return

    if args.cmd == "sanitize":
        root = Path(args.root)
        total = 0
        for f in walk_templates(root):
            total += sanitize_template_comments(f)
        print(f"Sanitized {total} occurrence(s) across templates under {root}")
        return

    if args.cmd == "styleguide":
        write_styleguide(Path(args.out))
        print(f"Wrote styleguide → {args.out}")
        return

    if args.cmd == "images":
        root = Path(args.root)
        n = optimize_images(root)
        print(f"Optimized {n} file(s) under {root}")
        return

    if args.cmd == "all":
        css = write_brand_tokens("#facc15", Path("app/static/css/brand.tokens.css"))
        print("✓ tokens → app/static/css/brand.tokens.css")
        total = 0
        for f in walk_templates(Path("app/templates")):
            total += sanitize_template_comments(f)
        print(f"✓ sanitized {total} occurrence(s)")
        write_styleguide(Path("app/templates/dev/styleguide.html"))
        print("✓ styleguide → app/templates/dev/styleguide.html")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
