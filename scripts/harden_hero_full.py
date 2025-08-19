#!/usr/bin/env python3
"""
FundChamps — Harden Hero Partial (SV-Prestige)
- Idempotently hardens app/templates/partials/hero_and_fundraiser.html
- Fixes invisible hero (removes opacity-0), injects CSS fallback, ARIA safeguards
- Adds #sr-live aria-live region for share() feedback
- Adds prefers-reduced-motion guard to confetti
- Backs up the original file with a timestamp
"""
from __future__ import annotations
import re, sys, shutil
from pathlib import Path
from datetime import datetime

HERO_PATH = Path("app/templates/partials/hero_and_fundraiser.html")
SENTINEL  = r"<!-- FC:HERO_SV_ELITE -->"

def backup(p: Path):
    if not p.exists(): return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = p.with_suffix(p.suffix + f".bak.{ts}")
    shutil.copy2(p, bak)
    print(f"• Backup → {bak}")

def ensure_visible_hero_img(html: str) -> tuple[str,bool]:
    """Remove brittle opacity-0 and ensure CSS fallback exists."""
    changed = False
    # 1) remove opacity-0 on hero image
    html2, n = re.subn(r'(<img[^>]*id="fc-hero-img"[^>]*class="[^"]*)\bopacity-0\b', r'\1', html, flags=re.I)
    if n: changed = True

    # 2) ensure style nonce block exists; then ensure fallback css is present
    style_pat = re.compile(r'(<style[^>]*nonce="{{\s*NONCE\s*}}".*?>\s*)(.*?)(\s*</style>)', re.S|re.I)
    m = style_pat.search(html2)
    if m:
        head, body, tail = m.groups()
        if "/* FC: hero fallback */" not in body:
            fallback_css = """
    /* FC: hero fallback */
    #fc-hero #fc-hero-img{ opacity:1 !important; }
    @media (prefers-reduced-motion:no-preference){
      #fc-hero #fc-hero-img{ transition: opacity .45s ease; }
    }
"""
            html2 = html2[:m.start()] + head + body.rstrip() + fallback_css + "\n  " + tail + html2[m.end():]
            changed = True
    else:
        # Add a minimal style block before closing </section> if none found
        inject = """
  <style nonce="{{ NONCE }}">
    /* FC: hero fallback */
    #fc-hero #fc-hero-img{ opacity:1 !important; }
    @media (prefers-reduced-motion:no-preference){
      #fc-hero #fc-hero-img{ transition: opacity .45s ease; }
    }
  </style>
"""
        html2, n2 = re.subn(r'</section>\s*$', inject + r'</section>', html2, flags=re.S|re.I)
        if n2: changed = True
    return html2, changed

def ensure_sr_live_region(html: str) -> tuple[str,bool]:
    """Insert a screen-reader live region (#sr-live) used by share() fallback."""
    if re.search(r'id="sr-live"', html): 
        return html, False
    # Insert just inside the hero card container
    card_pat = re.compile(r'(<div class="mx-auto[^"]*fc-hero-card[^"]*"[^>]*>\s*)', re.I)
    if card_pat.search(html):
        html2 = card_pat.sub(r'\1<p id="sr-live" class="sr-only" aria-live="polite"></p>\n', html, count=1)
        return html2, True
    # fallback: insert near top of section
    html2 = re.sub(r'(<section[^>]*id="fc-hero"[^>]*>\s*)', r'\1<p id="sr-live" class="sr-only" aria-live="polite"></p>\n', html, count=1, flags=re.I)
    return html2, True

def ensure_aria_progressbar(html: str) -> tuple[str,bool]:
    """Guarantee role=progressbar has aria attributes."""
    changed = False
    # add aria-valuemin/max if missing
    def add_minmax(m):
        nonlocal changed
        tag = m.group(0)
        if 'aria-valuemin' not in tag:
            tag = tag.replace('role="progressbar"', 'role="progressbar" aria-valuemin="0"')
            changed = True
        if 'aria-valuemax' not in tag:
            tag = tag.replace('aria-valuemin="0"', 'aria-valuemin="0" aria-valuemax="100"')
            changed = True
        if 'aria-label' not in tag:
            tag = tag.replace('aria-valuemax="100"', 'aria-valuemax="100" aria-label="Fundraising progress toward goal"')
            changed = True
        return tag
    html2 = re.sub(r'<div[^>]*role="progressbar"[^>]*>', add_minmax, html, count=1, flags=re.I)
    return html2, changed

def add_prm_guard_to_confetti(html: str) -> tuple[str,bool]:
    """Add prefers-reduced-motion guard into burstConfetti()."""
    if "prefers-reduced-motion" in html:
        return html, False
    # Inject after 'try{' inside burstConfetti IIFE
    html2, n = re.subn(
        r'(const\s+burstConfetti\s*=\s*\(function\)\(\)\{\s*return\s*function\([^)]+\)\{\s*try\{)',
        r"\1 const _prm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');"
        r" if (_prm && _prm.matches) { return; }",
        html
    )
    return html2, bool(n)

def ensure_sentinel(html: str) -> tuple[str,bool]:
    if SENTINEL in html: return html, False
    html2 = SENTINEL + "\n" + html
    return html2, True

def ensure_section_labelledby(html: str) -> tuple[str,bool]:
    """Ensure the hero section has aria-labelledby pointing at fc-hero-title."""
    if re.search(r'<section[^>]*id="fc-hero"[^>]*aria-labelledby="fc-hero-title"', html, flags=re.I):
        return html, False
    html2, n = re.subn(
        r'(<section[^>]*id="fc-hero"[^>]*)(>)',
        r'\1 aria-labelledby="fc-hero-title"\2',
        html, count=1, flags=re.I
    )
    return html2, bool(n)

def main():
    p = HERO_PATH
    if not p.exists():
        print(f"❌ Not found: {p}. Run from your project root.")
        sys.exit(1)

    src = p.read_text(encoding="utf-8")
    orig = src

    # Apply all hardening passes
    passes = [
        ensure_sentinel,
        ensure_visible_hero_img,
        ensure_sr_live_region,
        ensure_aria_progressbar,
        ensure_section_labelledby,
        add_prm_guard_to_confetti,
    ]

    changed_any = False
    for fn in passes:
        src, changed = fn(src)
        changed_any |= changed
        print(f"• {fn.__name__}: {'changed' if changed else 'ok'}")

    if not changed_any:
        print("✓ Hero already hardened. No changes written.")
        return

    backup(p)
    p.write_text(src, encoding="utf-8")
    print(f"✅ Hardened hero saved → {p}")

    # Quick sanity hints
    for candidate in [
        "app/static/images/connect-atx-team.jpg",
        "app/static/images/logo.webp",
        "app/static/images/logo.avif",
    ]:
        fp = Path(candidate)
        print(f"• Exists? {fp}: {'YES' if fp.exists() else 'no'}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)
