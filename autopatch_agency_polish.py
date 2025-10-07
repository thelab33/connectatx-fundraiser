import re
import glob
from pathlib import Path

def patch_file(path, pattern, repl, desc=""):
    src = Path(path).read_text(encoding="utf-8")
    out = re.sub(pattern, repl, src, flags=re.MULTILINE | re.DOTALL)
    if out != src:
        Path(path).write_text(out, encoding="utf-8")
        print(f"✅ Patched: {desc} in {path}")

# 1. Patch all .tile-title to better font/white/shadow
tile_title_css = r"\.tile-title\s*\{[^}]+\}"
tile_title_new = """.tile-title {
    font-family: 'Poppins', 'Inter', sans-serif;
    font-size: 1.32rem;
    font-weight: 900;
    color: #fff;
    letter-spacing: .01em;
    line-height: 1.13;
    margin-bottom: .36em;
    text-shadow: 0 2px 10px #0004, 0 1px 0 #facc1527;
}"""
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, tile_title_css, tile_title_new, ".tile-title CSS")

# 2. Patch .badge to gold-bg/dark text/stronger
badge_css = r"\.badge\s*\{[^}]+\}"
badge_new = """.badge {
    display: inline-block;
    font: 800 0.8rem/1 'Inter',sans-serif;
    background: linear-gradient(90deg,#ffe97a,#facc15 90%);
    border-radius: 12px;
    color: #18181b;
    padding: 0.36em 1.1em;
    margin-bottom: 0.7em;
    box-shadow: 0 2px 10px #facc1521;
    letter-spacing: 0.08em;
    text-shadow: 0 1px 1.5px #fff9;
    border: 1.5px solid #fff2;
    filter: blur(0.1px);
}"""
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, badge_css, badge_new, ".badge CSS")

# 3. Remove any color: #facc15 from .tile-title/.tile-copy
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, r"(\.tile-title[^{]*\{[^}]+)color:\s*#facc15;?", r"\1color: #fff;", ".tile-title gold→white")
    patch_file(f, r"(\.tile-copy[^{]*\{[^}]+)color:\s*#facc15;?", r"\1color: #e0e6ed;", ".tile-copy gold→offwhite")

# 4. Patch tile-copy for bigger, friendlier body
tile_copy_css = r"\.tile-copy\s*\{[^}]+\}"
tile_copy_new = """.tile-copy {
    font-size: 1.09rem;
    font-weight: 500;
    color: #e0e6ed;
    line-height: 1.62;
    margin-bottom: 1.13rem;
    letter-spacing: 0.01em;
    font-family: 'Inter',sans-serif;
}"""
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, tile_copy_css, tile_copy_new, ".tile-copy CSS")

# 5. Patch feature-tile for padding & shadow
tile_css = r"\.feature-tile\s*\{[^}]+\}"
tile_new = """.feature-tile {
    position:relative;
    border-radius:1.5rem;
    background:linear-gradient(140deg,rgba(28,28,40,.97),rgba(15,15,22,.92) 96%);
    backdrop-filter:blur(18px) saturate(1.2);
    padding:2.35rem 1.7rem 2.25rem;
    box-shadow:0 14px 36px rgba(0,0,0,.39);
    transition:box-shadow .25s,transform .25s;
    min-height: 338px;
    opacity:0;
    transform:translateY(20px);
}"""
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, tile_css, tile_new, ".feature-tile CSS")

# 6. Only allow gold text in: .badge, .accent, .btn.gold
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, r"color:\s*#facc15;(\s*\/\*[^*]*\*\/)?", "", "Remove accidental gold text")

# 7. Patch .feature-tiles-wrap for larger desktop gap
ftile_wrap_css = r"\.feature-tiles-wrap\s*\{[^}]+\}"
ftile_wrap_new = """.feature-tiles-wrap{
    display:grid;
    gap:2.2rem;
    grid-template-columns:1fr;
    align-items:stretch;
}
@media(min-width:700px){
    .feature-tiles-wrap{grid-template-columns:repeat(2,1fr);}
}
@media(min-width:1024px){
    .feature-tiles-wrap{grid-template-columns:repeat(3,1fr);gap:2.55rem;}
}"""
for f in glob.glob("app/static/css/*.css"):
    patch_file(f, ftile_wrap_css, ftile_wrap_new, ".feature-tiles-wrap CSS")

# 8. Add stronger hero title text-shadow (hero_and_fundraiser.html)
hero_title_html = r'class="fc-hero-title"([^>]*)>'
hero_title_new = 'class="fc-hero-title" style="text-shadow:0 3px 18px #0008,0 1px 0 #facc1525;"\\1>'
for f in glob.glob("app/templates/partials/hero_and_fundraiser.html"):
    patch_file(f, hero_title_html, hero_title_new, "hero title text-shadow")

print("✨ Agency patch complete! Review your site for polish ✨")
