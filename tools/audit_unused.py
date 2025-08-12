import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL_DIR = ROOT / "app" / "templates"
STATIC_DIR = ROOT / "app" / "static"

tpl_pat = re.compile(r"""{%\s*(?:include|extends|import|from)\s+['"]([^'"]+)['"]""")
render_pat = re.compile(r"""render_template\s*\(\s*['"]([^'"]+)['"]""")
gettpl_pat = re.compile(r"""get_template\s*\(\s*['"]([^'"]+)['"]""")
url_for_static_pat = re.compile(r"""url_for\(\s*['"]static['"]\s*,\s*filename\s*=\s*['"]([^'"]+)['"]""")
literal_static_pat = re.compile(r"""['"](/?static/[^'"]+)['"]""")

def rel_tpl(p: Path) -> str:
    return str(p.relative_to(TPL_DIR).as_posix())

# 1) Collect all templates
all_tpls = {rel_tpl(p) for p in TPL_DIR.rglob("*.html")}

# 2) Build edges from templates → referenced templates
edges = {t: set() for t in all_tpls}
missing_refs = set()
for p in TPL_DIR.rglob("*.html"):
    src = p.read_text(encoding="utf-8", errors="ignore")
    for m in tpl_pat.findall(src):
        edges[rel_tpl(p)].add(m)
        if m not in all_tpls:
            missing_refs.add((rel_tpl(p), m))

# 3) Entry points from python: render_template(...) / env.get_template(...)
roots = set()
for py in (ROOT / "app").rglob("*.py"):
    s = py.read_text(encoding="utf-8", errors="ignore")
    roots.update(render_pat.findall(s))
    roots.update(gettpl_pat.findall(s))

# 4) Reachability
seen = set()
stack = [*roots]
while stack:
    t = stack.pop()
    if t in seen: 
        continue
    seen.add(t)
    stack.extend([r for r in edges.get(t, []) if r not in seen])

# 5) Unused templates (especially partials/)
unused_all = sorted(all_tpls - seen)
unused_partials = [u for u in unused_all if u.startswith("partials/")]

# 6) Static assets: referenced vs on disk
ref_static = set()
for p in TPL_DIR.rglob("*.html"):
    s = p.read_text(encoding="utf-8", errors="ignore")
    ref_static.update(url_for_static_pat.findall(s))
    # allow literal /static/... too
    for lit in literal_static_pat.findall(s):
        if lit.startswith("/static/"):
            ref_static.add(lit[len("/static/"):])

for py in (ROOT / "app").rglob("*.py"):
    s = py.read_text(encoding="utf-8", errors="ignore")
    ref_static.update(url_for_static_pat.findall(s))

disk_static = {str(p.relative_to(STATIC_DIR).as_posix()) for p in STATIC_DIR.rglob("*") if p.is_file()}
unused_static = sorted(disk_static - ref_static)

# 7) Report
print("=== TEMPLATE AUDIT ===")
print(f"Total templates: {len(all_tpls)} | Roots in Python: {len(roots)} | Reachable: {len(seen)}")
if missing_refs:
    print("\nMissing references (template includes that don't exist):")
    for src, miss in sorted(missing_refs):
        print(f"  - {src} → {miss}")

print("\nUnused templates (not reachable from any render_template):")
for t in unused_all:
    print("  ", t)

print("\nUnused partials/:")
for t in unused_partials:
    print("  ", t)

print("\n=== STATIC ASSETS AUDIT ===")
print(f"On disk: {len(disk_static)} | Referenced: {len(ref_static)} | Unused: {len(unused_static)}")
for s in unused_static:
    print("  ", s)

# Exit non-zero if we found anything, good for CI
if missing_refs or unused_partials or unused_static:
    sys.exit(1)
