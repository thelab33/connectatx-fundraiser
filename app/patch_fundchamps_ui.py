#!/usr/bin/env python3
"""
FundChamps UI Patcher (Design/UX)
- Adds: custom amount, message, fee cover inputs
- Adds: trust copy ("Secured by Stripe")
- Adds: progress bar & leaderboard blocks
- Ensures: responsive meta
- Adds: light/dark theming toggle wired to existing .light styles

Usage:
  python patch_fundchamps_ui.py \
      --templates templates/base.html templates/index.html \
      --tiers-file templates/index.html \
      --progress-file templates/index.html \
      --leaderboard-file templates/index.html

Tips:
- You can pass the same file to multiple flags if sections live together.
- Creates .bak backups before patching.
"""

import argparse, re, shutil, sys, pathlib

def read(p): return p.read_text(encoding="utf-8")
def write(p, s): p.write_text(s, encoding="utf-8")

def backup(path: pathlib.Path):
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(path, bak)

def insert_once(text: str, marker_start: str, snippet: str) -> str:
    """Idempotent insertion of a snippet with a unique start marker."""
    if marker_start in text:
        return text
    return text + "\n\n" + snippet.strip() + "\n"

def insert_after_anchor(text: str, anchor_regex: str, snippet: str, marker_start: str) -> str:
    if marker_start in text:
        return text
    m = re.search(anchor_regex, text, flags=re.I|re.S)
    if not m:
        return text  # quietly skip if not found
    insert_at = m.end()
    return text[:insert_at] + "\n" + snippet.strip() + "\n" + text[insert_at:]

def ensure_meta_viewport(text: str) -> str:
    if re.search(r'<meta[^>]*name=["\']viewport["\']', text, re.I):
        return text
    head_match = re.search(r"<head[^>]*>", text, re.I)
    if not head_match:
        return text
    viewport = (
        '\n  <!-- FCX: responsive meta -->\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
    )
    return text[:head_match.end()] + viewport + text[head_match.end():]

def add_theme_toggle(text: str) -> str:
    # Button in header/nav area (after opening <body> or inside a nav)
    btn_marker = "<!-- FCX:THEME-TOGGLE:BTN -->"
    js_marker  = "<!-- FCX:THEME-TOGGLE:JS -->"
    if btn_marker in text and js_marker in text:
        return text

    # Try to place button after <body>
    body_open = re.search(r"<body[^>]*>", text, re.I)
    if not body_open:
        return text
    btn_html = f"""
{btn_marker}
<div style="position:fixed; right:10px; bottom:10px; z-index:9999;">
  <button id="fcx-theme" aria-label="Toggle theme"
          style="padding:.55rem .8rem; border-radius:999px; font-weight:900;
                 border:1px solid rgba(0,0,0,.25); backdrop-filter:saturate(1.2) blur(6px);">
    Toggle Theme
  </button>
</div>
"""

    text = text[:body_open.end()] + "\n" + btn_html + text[body_open.end():]

    # Append JS before closing body
    end_body = re.search(r"</body>", text, re.I)
    if not end_body:
        return text

    js = f"""
{js_marker}
<script>
(function(){
  const KEY='fcx_theme';
  const root=document.documentElement;
  const btn=document.getElementById('fcx-theme');
  function apply(mode){{
    if(mode==='light') root.classList.add('light'); else root.classList.remove('light');
  }}
  let mode=localStorage.getItem(KEY)||'dark';
  apply(mode);
  btn&&btn.addEventListener('click',()=>{{
    mode = (mode==='dark') ? 'light' : 'dark';
    localStorage.setItem(KEY,mode); apply(mode);
  }});
})();
</script>
"""
    return text[:end_body.start()] + js + text[end_body.start():]

# --- Snippets ---

INPUTS_SNIPPET = """
<!-- FCX:INPUTS:START -->
<div class="fcx-section" style="display:grid; gap:.6rem; margin-block:1rem;">
  <label style="display:flex; gap:.5rem; align-items:center; font-weight:800;">
    <input id="fundraiser-hero-monthly" type="checkbox" /> Make it monthly
  </label>
  <label>
    <span class="sr-only">Custom amount</span>
    <input id="fcx-custom-amount" inputmode="decimal" placeholder="Or enter custom amount"
      style="width:100%; padding:.8rem; border-radius:12px; border:1px solid rgba(255,255,255,.14);" />
  </label>
  <label style="display:flex; gap:.5rem; align-items:center;">
    <input id="fcx-fee-cover" type="checkbox" /> Add a little to cover fees
  </label>
  <textarea id="fcx-message" maxlength="240" placeholder="Optional message (dedication, athlete number, etc.)"
    style="width:100%; padding:.8rem; border-radius:12px; border:1px solid rgba(255,255,255,.14);"></textarea>

  <!-- FCX trust copy -->
  <p style="opacity:.85; font-size:.9rem; display:flex; gap:.45rem; align-items:center;">
    <span aria-hidden="true">🔒</span> Secured by Stripe — your payment is encrypted.
  </p>
</div>
<!-- FCX:INPUTS:END -->
"""

# Place under a #tiers / .tiers region if found
TIERS_ANCHOR = r'<section[^>]+id=["\']tiers["\'][^>]*>'

PROGRESS_SNIPPET = """
<!-- FCX:PROGRESS:START -->
<section id="progress" aria-live="polite" class="fcx-section" style="margin-block:1rem;">
  <div class="bar" style="background:rgba(255,255,255,.12); border-radius:12px; overflow:hidden;">
    <div class="fill" style="height:12px; width: {{ pct|default(0) }}%;
         background: linear-gradient(90deg,#fffbe6,var(--accent));"></div>
  </div>
  <div class="nums" style="display:flex; justify-content:space-between; font-weight:900; margin-top:.4rem;">
    <span>${{ '{:,.0f}'.format(raised or 0) }} raised</span>
    <span>Goal: ${{ '{:,.0f}'.format(goal or 0) }} ({{ pct|default(0) }}%)</span>
  </div>
</section>
<!-- FCX:PROGRESS:END -->
"""

LEADERBOARD_SNIPPET = """
<!-- FCX:LEADERBOARD:START -->
<section id="leaderboard" class="fcx-section" aria-labelledby="leaderboard-h" style="margin-block:1rem;">
  <h3 id="leaderboard-h" style="margin:0 0 .6rem; font-weight:1000;">Leaderboard</h3>
  <ol style="display:grid; gap:.35rem; padding-left:1.25rem; margin:0;">
    {% for row in leaderboard or [] %}
      <li><strong>{{ row.name }}</strong> — ${{ '{:,.0f}'.format(row.raised_usd or 0) }}</li>
    {% else %}
      <li>Be the first to appear on the leaderboard.</li>
    {% endfor %}
  </ol>
</section>
<!-- FCX:LEADERBOARD:END -->
"""

RESPONSIVE_NOTE = """
<!-- FCX:RESPONSIVE:CHECKS -->
<!-- Test targets: iPhone SE (375px), Pixel 5 (393px), iPad (768px), 1440px desktop -->
"""

def patch_file(path: pathlib.Path, ops):
    print(f"Patch: {path}")
    backup(path)
    txt = read(path)

    for op in ops:
        txt = op(txt)

    write(path, txt)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates", nargs="+", default=[], help="Files to ensure meta viewport + theme toggle")
    ap.add_argument("--tiers-file", default=None, help="File that contains the #tiers section to append inputs under")
    ap.add_argument("--progress-file", default=None, help="File to append progress block")
    ap.add_argument("--leaderboard-file", default=None, help="File to append leaderboard block")
    args = ap.parse_args()

    # 1) Base templates: responsive meta + theme toggle + note
    for f in args.templates:
        p = pathlib.Path(f)
        if not p.exists(): 
            print(f"Skip (missing): {p}")
            continue

        def do_ops(text):
            text = ensure_meta_viewport(text)
            text = add_theme_toggle(text)
            text = insert_once(text, "<!-- FCX:RESPONSIVE:CHECKS -->", RESPONSIVE_NOTE)
            return text

        patch_file(p, [do_ops])

    # 2) Inputs under tiers
    if args.tiers_file:
        p = pathlib.Path(args.tiers_file)
        if p.exists():
            def add_inputs(text):
                return insert_after_anchor(text, TIERS_ANCHOR, INPUTS_SNIPPET, "<!-- FCX:INPUTS:START -->")
            patch_file(p, [add_inputs])
        else:
            print(f"Skip (missing tiers file): {p}")

    # 3) Progress block
    if args.progress_file:
        p = pathlib.Path(args.progress_file)
        if p.exists():
            def add_progress(text):
                return insert_once(text, "<!-- FCX:PROGRESS:START -->", PROGRESS_SNIPPET)
            patch_file(p, [add_progress])
        else:
            print(f"Skip (missing progress file): {p}")

    # 4) Leaderboard block
    if args.leaderboard_file:
        p = pathlib.Path(args.leaderboard_file)
        if p.exists():
            def add_lb(text):
                return insert_once(text, "<!-- FCX:LEADERBOARD:START -->", LEADERBOARD_SNIPPET)
            patch_file(p, [add_lb])
        else:
            print(f"Skip (missing leaderboard file): {p}")

if __name__ == "__main__":
    sys.exit(main())
