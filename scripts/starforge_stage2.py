#!/usr/bin/env python3
"""
Starforge Stage 2 — JS wiring + polished error page
- Writes app/static/js/starforge_enhancements.js (idempotent)
- Injects <script> into base.html after your main bundle (idempotent)
- Replaces templates/error.html with a premium template (backs up .bak once)
Usage:
  python scripts/starforge_stage2.py dry-run
  python scripts/starforge_stage2.py patch
  python scripts/starforge_stage2.py revert
"""
from __future__ import annotations
import sys, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_PATH = ROOT / "app/static/js/starforge_enhancements.js"
BASE = ROOT / "app/templates/base.html"
ERROR_TPL = ROOT / "app/templates/error.html"

INJECT_SENTINEL = "<!-- STARFORGE-JS -->"
SCRIPT_TAG = (
    '\n    <!-- STARFORGE-JS -->\n'
    '    <script src="{{ url_for(\'static\', filename=\'js/starforge_enhancements.js\', v=asset_version) }}" defer></script>\n'
)

JS_CODE = r"""/* app/static/js/starforge_enhancements.js */
/* Vanilla, CSP-safe, no dependencies. */
(() => {
  'use strict';
  if (window.__STARFORGE_READY__) return; window.__STARFORGE_READY__ = true;

  const $ = (s, ctx=document)=>ctx.querySelector(s);
  const $$ = (s, ctx=document)=>Array.from(ctx.querySelectorAll(s));
  const clamp = (n, a, b)=>Math.min(b, Math.max(a, n));

  /* 1) Reveal-on-scroll (cards, stats, rows) */
  const reveal = () => {
    if (!('IntersectionObserver' in window)) { $$('.reveal').forEach(el=>el.classList.add('is-in')); return; }
    const io = new IntersectionObserver((entries) => {
      for (const en of entries) if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
    }, { rootMargin: '0px 0px -8% 0px', threshold: .12 });
    $$('.reveal').forEach(el => io.observe(el));
  };

  /* 2) Subtle hover lift on .card/.glass */
  const hoverLift = () => {
    const els = $$('.card, .glass');
    els.forEach(el => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = clamp((e.clientX - r.left) / r.width - .5, -1, 1);
        const dy = clamp((e.clientY - r.top) / r.height - .5, -1, 1);
        el.style.setProperty('--sf-tilt-x', (dy * -2).toFixed(3));
        el.style.setProperty('--sf-tilt-y', (dx *  2).toFixed(3));
        el.style.transform = `perspective(900px) rotateX(var(--sf-tilt-x,0deg)) rotateY(var(--sf-tilt-y,0deg)) translateY(-2px)`;
      }, { passive: true });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; }, { passive: true });
    });
  };

  /* 3) CTA haptics (buttons feel “alive” without being flashy) */
  const ctaHaptics = () => {
    const ctas = $$("[data-open-donate-modal], [data-analytics='cta:sponsor'], [data-analytics='cta:vip'], .btn, .sf-btn");
    ctas.forEach(b => {
      b.addEventListener('pointerdown', () => {
        b.style.transform = 'translateY(1px) scale(.995)';
      }, { passive: true });
      b.addEventListener('pointerup', () => {
        b.style.transform = '';
      }, { passive: true });
    });
  };

  /* 4) Sticky Quick Donate visibility (only if header leaves viewport) */
  const quickDonate = () => {
    const floater = document.querySelector('[data-analytics="cta:quick-donate"]');
    const sentinel = document.getElementById('fc-header-sentinel');
    if (!floater || !sentinel || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver(([en]) => { floater.hidden = en.isIntersecting; }, { threshold: 0 });
    io.observe(sentinel);
  };

  /* 5) Safe copy-link buttons */
  const copyLinks = () => {
    $$('[data-copy-link]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const url = btn.getAttribute('data-copy-link') || location.href;
        try { await navigator.clipboard.writeText(url); btn.classList.add('copied'); setTimeout(()=>btn.classList.remove('copied'), 1600); } catch {}
      });
    });
  };

  /* 6) Auto-mark external links */
  const hardenExternal = () => {
    $$('a[target="_blank"]').forEach(a => {
      if (!/noopener|noreferrer/.test(a.rel||'')) a.rel = (a.rel ? a.rel + ' ' : '') + 'noopener noreferrer';
    });
  };

  /* 7) Auto lazyload/decoding for images without attrs (defensive) */
  const lazyImages = () => {
    $$('img:not([loading])').forEach(img => img.loading = 'lazy');
    $$('img:not([decoding])').forEach(img => img.decoding = 'async');
  };

  /* Kickoff when DOM is ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { reveal(); hoverLift(); ctaHaptics(); quickDonate(); copyLinks(); hardenExternal(); lazyImages(); }, { once: true });
  } else {
    reveal(); hoverLift(); ctaHaptics(); quickDonate(); copyLinks(); hardenExternal(); lazyImages();
  }
})();
"""

ERROR_HTML = r"""{% extends "base.html" %}
{% block head_title %}Something went wrong — {{ super() }}{% endblock %}
{% block content %}
<section class="relative fc-band fc-band--tint">
  <div class="hero-aura" aria-hidden="true"></div>
  <div class="container mx-auto max-w-5xl px-6">
    <div class="card p-8 md:p-10 reveal">
      <div class="eyebrow mb-2">Error</div>
      <h1 class="display mb-3" style="font-size:clamp(1.6rem,4vw,2.4rem)">Oops! Something went wrong.</h1>
      <p class="lede mb-6">Our homepage is temporarily unavailable. You can still explore, donate, or contact us below.</p>
      <div class="flex flex-wrap gap-3">
        <a href="{{ url_for('main.home') if url_for is defined else '/' }}" class="btn btn-primary">Go back home</a>
        <a href="#tiers" class="btn btn-ghost">See Sponsorship Tiers</a>
        <button class="btn btn-ghost" data-open-donate-modal>💸 Quick Donate</button>
      </div>
    </div>
  </div>
</section>

<section class="fc-band">
  <div class="container mx-auto max-w-6xl px-6 grid gap-6 md:grid-cols-2">
    <div class="card p-6 reveal">
      <h2 class="font-extrabold text-yellow-300 mb-2">Stay in the Loop</h2>
      {% include 'partials/newsletter.html' ignore missing with context %}
    </div>
    <div class="card p-6 reveal">
      <h2 class="font-extrabold text-yellow-300 mb-2">Share the Love</h2>
      <div class="flex flex-wrap gap-2">
        <a class="chip" target="_blank" href="https://twitter.com/intent/tweet?text={{ 'Support ' ~ (team.team_name if team else 'our team') ~ ' — donate or sponsor!'|urlencode }}&url={{ request.url_root if request is defined else '/'|urlencode }}">🐦 X/Twitter</a>
        <a class="chip" target="_blank" href="https://www.facebook.com/sharer/sharer.php?u={{ request.url_root if request is defined else '/'|urlencode }}">📘 Facebook</a>
        <button class="chip" data-copy-link="{{ request.url_root if request is defined else '/' }}">🔗 Copy Link</button>
      </div>
    </div>
  </div>
</section>
{% endblock %}
"""

def backup_once(p: Path) -> Path | None:
  if not p.exists(): return None
  bak = p.with_suffix(p.suffix + ".bak")
  if bak.exists(): return bak
  shutil.copy2(p, bak)
  return bak

def write_js():
  JS_PATH.parent.mkdir(parents=True, exist_ok=True)
  if not JS_PATH.exists() or JS_PATH.read_text(encoding='utf-8') != JS_CODE:
    JS_PATH.write_text(JS_CODE, encoding='utf-8')
    return True
  return False

def inject_script():
  if not BASE.exists(): return {"changed": False, "note": "base.html not found"}
  txt = BASE.read_text(encoding='utf-8')
  if INJECT_SENTINEL in txt:
    return {"changed": False, "note": "already injected"}
  # Find the main bundle script include and place after it
  anchor = 'src="{{ url_for(\'static\', filename=__js_path, v=asset_version) }}"'
  idx = txt.find(anchor)
  if idx == -1:
    # fallback: inject before {% block scripts_extra %}
    anchor2 = "{% block scripts_extra %}"
    idx2 = txt.find(anchor2)
    if idx2 == -1:
      return {"changed": False, "note": "no anchor found"}
    new = txt[:idx2] + SCRIPT_TAG + txt[idx2:]
  else:
    # find the closing </script> after the anchor
    end = txt.find("</script>", idx)
    if end == -1: return {"changed": False, "note": "could not locate closing </script>"}
    end += len("</script>")
    new = txt[:end] + SCRIPT_TAG + txt[end:]
  backup_once(BASE)
  BASE.write_text(new, encoding='utf-8')
  return {"changed": True, "note": "script injected"}

def patch_error():
  # replace entire error.html with premium template
  backup_once(ERROR_TPL)
  ERROR_TPL.parent.mkdir(parents=True, exist_ok=True)
  ERROR_TPL.write_text(ERROR_HTML, encoding='utf-8')
  return True

def revert():
  changes = []
  for p in [BASE, ERROR_TPL]:
    bak = p.with_suffix(p.suffix + ".bak")
    if bak.exists():
      shutil.copy2(bak, p)
      changes.append(str(p))
  return {"restored": changes}

def main():
  mode = (sys.argv[1] if len(sys.argv) > 1 else "dry-run").lower()
  if mode == "revert":
    print(json.dumps({"mode": "revert", **revert()}, indent=2)); return

  created_js = write_js()
  inject = inject_script()
  err = False if mode == "dry-run" else patch_error()

  out = {
    "mode": mode,
    "js": {"path": str(JS_PATH), "updated": created_js},
    "base_script": inject,
    "error_template": {"path": str(ERROR_TPL), "would_write": True} if mode=="dry-run" else {"path": str(ERROR_TPL), "written": err},
  }
  print(json.dumps(out, indent=2))

if __name__ == "__main__":
  main()

