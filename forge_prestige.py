#!/usr/bin/env python3
"""
forge_prestige.py — FundChamps SV‑Elite Autopatcher
====================================================
Purpose:
  • Auto‑inject a Silicon Valley–level UI/UX layer + architecture conventions
    into your Flask + Jinja project (FundChamps / Connect ATX Elite style).
  • Idempotent patches: safe to re‑run. Creates timestamped backups.
  • Drops in premium micro‑UX (sticky header, metric count‑ups, reveal, VIP
    confetti), CSP‑safe scripts, and a prestige CSS layer that doesn't require
    Tailwind rebuilds (pure CSS progressive enhancement).

What it touches (by default paths):
  app/templates/base.html                        (ensures structure & assets)
  app/templates/index.html                       (ensures sections/partials)
  app/templates/partials/ui_bootstrap.html       (ensures include present)
  app/static/css/fc_prestige.css                 (new progressive CSS)
  app/static/js/fc_prestige.js                   (new micro‑UX)
  app/static/js/fc_confetti.min.js               (tiny confetti helper)

Run:
  cd <your-project-root>
  python3 forge_prestige.py --apply

Options:
  --apply           Apply patches (default dry-run).
  --root PATH       Project root (defaults to cwd).
  --force           Overwrite/repair even if validations fail.
  --stats-url URL   Endpoint that returns fundraiser stats (default: /demo/stats).
  --poll-ms N       Poll stats every N ms (default: 15000).
  --autostats 0/1   Enable/disable autostats (default: 1).
  --verbose         Print patch details.

Exit codes: 0 = success, 2 = dry-run success, 3 = validation error, 4 = patch error.
"""
import argparse, re, sys, shutil
from datetime import datetime
from pathlib import Path

# ------------------------------ Helpers ------------------------------

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if not p.exists(): 
        return None
    b = p.with_suffix(p.suffix + f".bak.{stamp()}")
    shutil.copy2(p, b)
    return b

def write_file(p: Path, content: str, apply: bool, verbose: bool):
    if apply:
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            backup(p)
        p.write_text(content, encoding="utf-8")
        if verbose: print(f"  → Wrote {p}")
    else:
        if verbose: 
            print(f"  (dry-run) would write {p} with {len(content)} bytes")

def replace_or_append(path: Path, pattern: str, repl: str, apply: bool, verbose: bool):
    """
    Regex replace once; if no match, append near </body> or EOF.
    Returns (changed: bool, how: str)
    """
    if not path.exists():
        return False, "missing"
    txt = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, txt, flags=re.S)
    if n > 0:
        if apply:
            backup(path)
            path.write_text(new, encoding="utf-8")
        if verbose: print(f"  → Patched {path.name} ({n} replacement)")
        return True, "replaced"
    # append before </body>
    insert = repl if repl.endswith("\n") else repl + "\n"
    if "</body>" in txt:
        new = txt.replace("</body>", insert + "</body>")
    else:
        new = txt + "\n" + insert
    if apply:
        backup(path); path.write_text(new, encoding="utf-8")
    if verbose: print(f"  → Appended to {path.name}")
    return True, "appended"

def ensure_include(path: Path, include_line: str, where="top", apply=False, verbose=False):
    """
    Guarantee a Jinja include line exists. 'where' = top|bottom.
    """
    if not path.exists(): return False
    txt = path.read_text(encoding="utf-8")
    if include_line in txt:
        return False
    if apply:
        backup(path)
    if where == "top":
        new = include_line + "\n" + txt
    else:
        new = txt + "\n" + include_line + "\n"
    if apply:
        path.write_text(new, encoding="utf-8")
    if verbose: print(f"  → Inserted include into {path.name}: {include_line.strip()}")
    return True

# ------------------------------ Assets ------------------------------

PRESTIGE_CSS = r"""
/* app/static/css/fc_prestige.css — Progressive enhancement, Tailwind-agnostic */
:root {
  --fc-amber: #facc15;
  --fc-amber-600: #d1a90d;
  --fc-bg-900: #0b0b0c;
  --fc-bg-800: #111113;
  --fc-card: rgba(255,255,255,0.04);
  --fc-ring: rgba(250, 204, 21, 0.65);
}

html { scroll-behavior: smooth; }
body { background: radial-gradient(80% 60% at 50% 0%, #1a1a1a 0%, #0b0b0c 60%) fixed; }

/* Card glow */
.fc-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03)) padding-box,
              radial-gradient(120% 120% at 0% 0%, rgba(250, 204, 21, 0.35), rgba(250, 204, 21, 0)) border-box;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  backdrop-filter: blur(6px);
  box-shadow: 0 10px 30px rgba(250, 204, 21, 0.08);
}

/* Focus ring & accessibility */
a:focus-visible, button:focus-visible, [tabindex]:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--fc-ring);
  border-radius: 12px;
}

/* Sticky header shadow */
.fc-sticky-shadow {
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
/* Progress meter enhancements */
.fc-meter-track{height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden}
.fc-meter-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--fc-amber),#fffbe6)}

/* Small badges */
.fc-badge{display:inline-flex;align-items:center;gap:.4rem;padding:.15rem .5rem;border-radius:999px;background:rgba(250,204,21,.12);border:1px solid rgba(250,204,21,.35);font-weight:600;font-size:.75rem}

/* Reveal animation */
.fc-reveal{opacity:0;transform:translateY(16px);transition:opacity .6s ease,transform .6s ease}
.fc-reveal.is-visible{opacity:1;transform:none}

/* Buttons */
.fc-btn{position:relative;display:inline-flex;align-items:center;gap:.55rem;border-radius:999px;padding:.7rem 1.1rem;font-weight:700}
.fc-btn-primary{background:linear-gradient(180deg,var(--fc-amber),var(--fc-amber-600));color:#0b0b0c}
.fc-btn-primary:hover{filter:brightness(1.08)}
.fc-btn-ghost{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#fff}
.fc-btn-ghost:hover{background:rgba(255,255,255,.12)}

/* Mini header meter */
#hdr-meter{display:flex;align-items:center;gap:.55rem}
#hdr-meter .track{width:160px}
#hdr-meter .sr{position:absolute;left:-9999px;top:auto;width:1px;height:1px;overflow:hidden}
"""

PRESTIGE_JS = r"""
/* app/static/js/fc_prestige.js — micro‑UX & live sync (no dependencies) */
(function () {
  const bus = (window.fc = window.fc || {});
  bus.emit = (n, d={}) => document.dispatchEvent(new CustomEvent(n, { detail:d }));
  bus.on   = (n, fn) => document.addEventListener(n, fn);

  // Sticky header shadow
  const header = document.querySelector('header.header, header[data-fc="hdr"]') || document.querySelector('header');
  if (header) {
    const sticky = () => header.classList.toggle('fc-sticky-shadow', window.scrollY > 4);
    sticky(); window.addEventListener('scroll', sticky, { passive:true });
  }

  // Reveal on view
  const io = new IntersectionObserver((ents)=>{
    ents.forEach(e => e.isIntersecting && e.target.classList.add('is-visible'));
  }, { threshold: 0.12 });
  document.querySelectorAll('.fc-reveal').forEach(el => io.observe(el));

  // CountUp for metrics
  function countUp(el) {
    const end = parseFloat(el.getAttribute('data-countup') || '0');
    const dur = parseInt(el.getAttribute('data-countup-ms') || '1100', 10);
    const start = performance.now();
    function tick(t){
      const p = Math.min(1, (t - start) / dur);
      const v = Math.floor(end * (0.5 - Math.cos(Math.PI*p)/2)); // easeInOut
      el.textContent = Number.isFinite(end) ? v.toLocaleString() : end;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  document.querySelectorAll('[data-countup]').forEach(countUp);

  // Mini header fundraiser meter
  function updateHeaderMeter(data) {
    const raised = Number(data.raised || data.funds_raised || 0);
    const goal   = Number(data.goal || data.fundraising_goal || 1);
    const pct    = Math.max(0, Math.min(100, (raised/goal)*100));
    const elBar  = document.querySelector('#hdr-meter .fill');
    const elPct  = document.querySelector('#hdr-pct');
    const elR    = document.querySelector('#hdr-raised');
    const elG    = document.querySelector('#hdr-goal');
    if (elBar) elBar.style.width = pct.toFixed(1) + '%';
    if (elPct) elPct.textContent = pct.toFixed(1) + '%';
    if (elR) elR.textContent = '$' + Math.round(raised).toLocaleString();
    if (elG) elG.textContent = '$' + Math.round(goal).toLocaleString();
  }

  window.fc = window.fc || {};
  window.fc.on = (n, fn) => document.addEventListener(n, fn);
  document.addEventListener('fc:funds:update', (e) => updateHeaderMeter(e.detail || {}));

  // Optional autostats
  const cfg = (window.FC_CONFIG || {});
  const STATS_URL = cfg.stats_url || '/demo/stats';
  const POLL_MS   = cfg.poll_ms || 15000;
  const AUTOSTATS = ('autostats' in cfg) ? !!cfg.autostats : true;

  async function fetchStats() {
    try {
      const res = await fetch(STATS_URL, { credentials: 'same-origin' });
      const j = await res.json();
      document.dispatchEvent(new CustomEvent('fc:funds:update', { detail: j }));
    } catch (err) { /* no-op */ }
  }
  if (AUTOSTATS) {
    fetchStats();
    setInterval(fetchStats, POLL_MS);
  }

  // VIP confetti (lightweight)
  window.fcConfetti = function fireConfetti () {
    if (!window.confetti) return;
    window.confetti({ particleCount: 120, spread: 70, origin: { y: 0.6 } });
  };
})();
"""

CONFETTI_MIN = r"""
/*! fc_confetti.min.js (micro build) */
!function(){function r(r){return Math.random()*r}var t=document.createElement("canvas");t.style.position="fixed",t.style.top=0,t.style.left=0,t.style.width="100%",t.style.height="100%",t.style.pointerEvents="none",t.style.zIndex=9999;var e=t.getContext("2d"),n=[],i=!1;function o(){e.clearRect(0,0,t.width,t.height),n.forEach(function(r){r.y+=r.vy,r.x+=r.vx,r.vy+=.05,r.a-=.01,e.globalAlpha=Math.max(r.a,0),e.fillStyle=r.c,e.fillRect(r.x,r.y,r.s,r.s)}),n=n.filter(function(r){return r.a>0&&r.y<t.height+20}),i&&requestAnimationFrame(o)}window.addEventListener("resize",function(){t.width=innerWidth,t.height=innerHeight}),t.width=innerWidth,t.height=innerHeight;window.confetti=function(a){a=a||{};var h=a.particleCount||80,s=a.spread||60,d=(a.origin&&a.origin.x||.5)*t.width,l=(a.origin&&a.origin.y||.5)*t.height;document.body.contains(t)||document.body.appendChild(t),i||(i=!0,requestAnimationFrame(o));for(var c=0;c<h;c++)n.push({x:d+r(20)-10,y:l+r(20)-10,vx:r(6)-3,vy:r(4)-2,s:r(6)+2,c:"hsl("+Math.floor(r(360))+",100%,60%)",a:1})}}();
"""

def ensure_base_structure(base_path: Path, apply: bool, verbose: bool):
    if not base_path.exists():
        raise FileNotFoundError(f"Missing {base_path}")
    # 1) Ensure ui_bootstrap include at top
    ensure_include(
        base_path,
        '{% include "partials/ui_bootstrap.html" ignore missing with context %}',
        where="top", apply=apply, verbose=verbose
    )
    # 2) Ensure prestige assets before </body>
    prestige_assets = r'''
  {# --- FundChamps Prestige Assets (progressive) --- #}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/fc_prestige.css') }}?v={{ asset_version|default(0) }}" />
  <script nonce="{{ (csp_nonce() if csp_nonce is defined else (NONCE if NONCE is defined else '')) }}" >
    window.FC_CONFIG = Object.assign({}, window.FC_CONFIG||{}, {
      stats_url: "{{ _stats_url|default('/demo/stats') }}",
      poll_ms: {{ _poll_ms|default(15000) }},
      autostats: {{ _autostats|default(true)|tojson }}
    });
  </script>
  <script defer src="{{ url_for('static', filename='js/fc_confetti.min.js') }}?v={{ asset_version|default(0) }}" nonce="{{ (csp_nonce() if csp_nonce is defined else (NONCE if NONCE is defined else '')) }}"></script>
  <script defer src="{{ url_for('static', filename='js/fc_prestige.js') }}?v={{ asset_version|default(0) }}" nonce="{{ (csp_nonce() if csp_nonce is defined else (NONCE if NONCE is defined else '')) }}"></script>
'''
    replace_or_append(base_path, r"\{\# --- FundChamps Prestige Assets.*?\#\}.*?fc_prestige\.js.*?\n", prestige_assets, apply, verbose)
    return True

def ensure_index_sections(index_path: Path, apply: bool, verbose: bool):
    """Make sure index.html extends base and includes key sections in order."""
    if not index_path.exists():
        raise FileNotFoundError(f"Missing {index_path}")
    txt = index_path.read_text(encoding="utf-8")

    # Ensure it extends base
    if "{% extends" not in txt:
        if apply: backup(index_path)
        txt = '{% extends "base.html" %}\n' + txt
        if apply: index_path.write_text(txt, encoding="utf-8")
        if verbose: print("  → Ensured `{% extends 'base.html' %}` in index.html")

    # Ensure the main block exists
    if "{% block content %}" not in txt:
        if apply: backup(index_path)
        txt += "\n{% block content %}\n  <!-- home content injected by forge -->\n{% endblock %}\n"
        if apply: index_path.write_text(txt, encoding="utf-8")
        if verbose: print("  → Added content block to index.html")

    # Ensure curated partials order inside content
    want = [
        'partials/hero_and_fundraiser.html',
        'partials/sponsor_tiers.html',
        'partials/program_stats_and_calendar.html',
        'partials/budget_cards.html',
        'partials/about_and_mission.html',
        'partials/testimonials.html',
        'partials/newsletter.html'
    ]
    txt = index_path.read_text(encoding="utf-8")
    m = re.search(r"(\{% block content %\})(.*?)(\{% endblock %\})", txt, flags=re.S)
    if m:
        inside = m.group(2)
        lines = []
        for inc in want:
            tag = f"{{% include \"{inc}\" ignore missing with context %}}"
            if inc in inside or tag in inside:
                lines.append(None)
            else:
                lines.append(tag)
        inject = "\n".join([l for l in lines if l])
        if inject:
            patched = txt.replace(m.group(0), f"{m.group(1)}{inside.strip()}\n{inject}\n{m.group(3)}")
            if apply:
                backup(index_path)
                index_path.write_text(patched, encoding="utf-8")
            if verbose: print(f"  → Inserted {inject.count('include')} missing home sections")
    return True

def ensure_files_static(static_dir: Path, apply: bool, verbose: bool):
    css = static_dir / "css/fc_prestige.css"
    js  = static_dir / "js/fc_prestige.js"
    j2  = static_dir / "js/fc_confetti.min.js"
    write_file(css, PRESTIGE_CSS, apply, verbose)
    write_file(js,  PRESTIGE_JS,  apply, verbose)
    write_file(j2,  CONFETTI_MIN, apply, verbose)
    return True

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default dry-run)")
    ap.add_argument("--root", default=".", help="project root (defaults to cwd)")
    ap.add_argument("--force", action="store_true", help="force even if validations fail")
    ap.add_argument("--stats-url", default="/demo/stats")
    ap.add_argument("--poll-ms", type=int, default=15000)
    ap.add_argument("--autostats", type=int, default=1)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    tpl  = root / "app" / "templates"
    static = root / "app" / "static"
    base = tpl / "base.html"
    index = tpl / "index.html"

    if not base.exists() or not index.exists():
        if not args.force:
            print(f"❌ Validation failed. Expecting {base} and {index}. Use --force to continue.", file=sys.stderr)
            return sys.exit(3)

    # Ensure static assets
    ensure_files_static(static, args.apply, args.verbose)

    # Ensure base structure + asset hooks
    if base.exists():
        ensure_base_structure(base, args.apply, args.verbose)

    # Ensure index sections
    if index.exists():
        ensure_index_sections(index, args.apply, args.verbose)

    # Best‑effort: ensure ui_bootstrap default vars are accessible
    uib = tpl / "partials" / "ui_bootstrap.html"
    if not uib.exists():
        shim = "{# ui_bootstrap shim (autogenerated by forge_prestige.py) #}\n"                "{% set NONCE = NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') %}\n"                "{% set _stats_url = stats_url|default('/demo/stats') %}\n"                "{% set _poll_ms   = poll_ms|default(15000) %}\n"                "{% set _autostats = autostats if autostats is defined else true %}\n"
        write_file(uib, shim, args.apply, args.verbose)

    if args.apply:
        print("✅ Forge complete (apply mode). Restart your dev server and hard‑refresh.")
        print("   Injected: static/css/fc_prestige.css, static/js/fc_prestige.js, fc_confetti.min.js")
        print("   base.html hooked with 'FundChamps Prestige Assets'.")
        print("   index.html ensured with core sections (missing ones appended).")
        sys.exit(0)
    else:
        print("ℹ️  Dry‑run complete. Re‑run with --apply to write changes.")
        sys.exit(2)

if __name__ == "__main__":
    main()
