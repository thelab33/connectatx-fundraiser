
#!/usr/bin/env python3
"""
FundChamps Repo Auditor (MVP)
- Scans your repo for required partials, CSS pipeline sanity, Stripe config,
  and common pitfalls (duplicate header styles, missing hero glass/meter).
- Outputs: fundchamps_audit_report.md (markdown)

Usage:
  python3 fundchamps_audit.py --root .
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime

CHECKS = []

def record(title, ok, details=None, files=None, advice=None):
    CHECKS.append({
        "title": title,
        "ok": bool(ok),
        "details": details or "",
        "files": files or [],
        "advice": advice or ""
    })

def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def find_files(root: Path, patterns):
    out = []
    for pat in patterns:
        out.extend(root.rglob(pat))
    return out

def rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

def check_templates(root: Path):
    tpl_root = root / "app" / "templates"
    if not tpl_root.exists():
        record("Templates folder", False, f"Missing: {rel(root, tpl_root)}",
               advice="Expected Flask templates under app/templates/. Adjust --root if your structure differs.")
        return
    # Required partials
    required = [
        "partials/hero_and_fundraiser.html",
        "partials/about_section.html",
        "partials/footer.html",
    ]
    missing = [p for p in required if not (tpl_root / p).exists()]
    ok = len(missing) == 0
    record("Required partials exist", ok,
           details=("All present" if ok else "Missing: " + ", ".join(missing)),
           advice=("Create/restore the missing partials or update includes to match existing filenames"))
    # Includes resolve
    include_re = re.compile(r'{%\s*include\s*["\']([^"\']+)["\']')
    includes = []
    for f in tpl_root.rglob("*.html"):
        text = read_text(f)
        for m in include_re.finditer(text):
            includes.append((f, m.group(1)))
    unresolved = []
    for src, inc in includes:
        if inc.startswith(("http://","https://")): 
            continue
        if not (tpl_root / inc).exists():
            unresolved.append((src, inc))
    record("Template include paths resolve", len(unresolved) == 0,
           details=("Resolved {} includes".format(len(includes)) if not unresolved else
                    "Unresolved includes:\n" + "\n".join(f"- {rel(tpl_root, s)} → {inc}" for s,inc in unresolved)),
           advice=("Rename or fix the include paths; or ensure those partials exist under app/templates/"))
    # Macro import
    macro_path = tpl_root / "shared" / "components" / "about_section.html"
    record("About macro file present", macro_path.exists(),
           details=(rel(tpl_root, macro_path)),
           advice="Place your about_section macro at shared/components/about_section.html or update import paths.")

    # Hero has hero-glass + meter ids
    hero = tpl_root / "partials" / "hero_and_fundraiser.html"
    if hero.exists():
        t = read_text(hero)
        has_glass = "hero-glass" in t
        has_meter = 'id="fundraiser-meter"' in t and 'id="fc-bar"' in t
        record("Hero glass class present", has_glass, files=[rel(tpl_root, hero)],
               advice='Add class="hero-glass" to the main hero card wrapper.')
        record("Hero meter elements present", has_meter, files=[rel(tpl_root, hero)],
               advice='Ensure the progress bar uses id="fundraiser-meter" and inner fill id="fc-bar".')
    else:
        record("Hero partial present", False, details=rel(tpl_root, hero))

def check_base_css_link(root: Path):
    base = root / "app" / "templates" / "base.html"
    if not base.exists():
        record("base.html exists", False, rel(root, base))
        return
    t = read_text(base)
    css_hrefs = re.findall(r'href=["\']([^"\']+\.css[^"\']*)["\']', t, flags=re.I)
    single = len(css_hrefs) == 1 and ("dist/app" in css_hrefs[0] or css_hrefs[0].endswith(".min.css"))
    record("Single CSS stylesheet loaded in base.html", single,
           details=f"Found {len(css_hrefs)} CSS links: {css_hrefs}",
           advice="Load only one built stylesheet, e.g., css/dist/app.min.css with cache-busting.")

def check_css_pipeline(root: Path):
    css_root = root / "app" / "static" / "css"
    if not css_root.exists():
        record("Static CSS folder", False, f"Missing: {rel(root, css_root)}")
        return
    index = css_root / "src" / "index.css"
    has_index = index.exists()
    record("Tailwind entry exists (src/index.css)", has_index, rel(css_root, index),
           advice="Create src/index.css importing tokens + components; build to dist/app.min.css.")
    # imports in index.css resolve
    if has_index:
        t = read_text(index)
        imports = re.findall(r'@import\s+["\']([^"\']+)["\'];', t)
        unresolved = []
        for imp in imports:
            p = (index.parent / imp).resolve()
            if not p.exists():
                unresolved.append(imp)
        record("index.css @import files resolve", len(unresolved)==0,
               details=("All imports present" if not unresolved else "Missing: "+", ".join(unresolved)))
    # orphan CSS (not referenced by index.css or dist)
    all_css = list(css_root.rglob("*.css"))
    referenced = set()
    if has_index:
        referenced.add(index.resolve())
        for imp in re.findall(r'@import\s+["\']([^"\']+)["\'];', read_text(index)):
            referenced.add((index.parent / imp).resolve())
    # dist is allowed
    dist_dir = css_root / "dist"
    if dist_dir.exists():
        for p in dist_dir.rglob("*.css"):
            referenced.add(p.resolve())
    orphans = [p for p in all_css if p.resolve() not in referenced and "/dist/" not in str(p)]
    record("Orphan CSS files (ok to delete/move)", len(orphans)==0,
           details=("None" if not orphans else "\n".join("- "+rel(css_root,p) for p in orphans)),
           advice="Move needed rules into src/ and remove legacy outputs (output.css, tailwind.min.css, backups).")
    # duplicate :focus-visible rules across header css
    candidates = ["fc_prestige-header.css","header-safe.css","src/components/header.css"]
    found = []
    for c in candidates:
        p = css_root / c
        if p.exists() and "focus-visible" in read_text(p):
            found.append(rel(css_root, p))
    record(":focus-visible duplicated across header styles", len(found)<=1,
           details=("Found in: "+", ".join(found) if found else "Not found"),
           advice="Keep a single authoritative focus-visible block in src/components/header.css")
    # hero module present
    hero_css = css_root / "src" / "components" / "hero.css"
    record("Hero CSS module present", hero_css.exists(),
           details=rel(css_root, hero_css),
           advice="Add src/components/hero.css to restore glass overlay & proportional meters.")

def check_api_endpoints(root: Path):
    api = {"payments_config": False, "checkout": False, "thanks": False, "stats": False}
    app_dir = root / "app"
    if not app_dir.exists():
        record("App folder exists", False, rel(root, app_dir),
               advice="Expected Flask app under app/. Adjust --root if needed.")
        return
    py_files = list(app_dir.rglob("*.py"))
    pattern_map = {
        "payments_config": re.compile(r'@bp\.route\(["\']/payments/config'),
        "checkout": re.compile(r'@bp\.route\(["\']/checkout'),
        "thanks": re.compile(r'@bp\.route\(["\']/thanks'),
        "stats": re.compile(r'@bp\.route\(["\']/stats')
    }
    for f in py_files:
        txt = read_text(f)
        for key, pat in pattern_map.items():
            if pat.search(txt):
                api[key] = True
    ok = all(api.values())
    record("Payments API blueprint endpoints", ok,
           details="; ".join([f"{k}: {'OK' if v else 'MISSING'}" for k,v in api.items()]),
           advice="Add app/blueprints/payments.py with /api/payments/config, /api/checkout, /api/thanks, /api/stats.")

def check_env(root: Path):
    env = root / ".env"
    if not env.exists():
        record(".env present", False, rel(root, env),
               advice="Create .env with STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, FUNDRAISING_GOAL, TEAM_NAME.")
        return
    t = read_text(env)
    req = ["STRIPE_SECRET_KEY","STRIPE_PUBLISHABLE_KEY","FUNDRAISING_GOAL","TEAM_NAME"]
    missing = [k for k in req if re.search(rf'^\s*{re.escape(k)}\s*=', t, flags=re.M) is None]
    record(".env contains required keys", len(missing)==0,
           details=("All present" if not missing else "Missing: " + ", ".join(missing)),
           advice="Add the missing keys; use live keys in production.")
    has_link = re.search(r'^\s*STRIPE_PAYMENT_LINK\s*=', t, flags=re.M) is not None
    record("Optional STRIPE_PAYMENT_LINK set", has_link or False,
           details=("Set" if has_link else "Not set"),
           advice="If set, Quick Donate can redirect instantly to Stripe hosted page.")

def check_header_meter(root: Path):
    css_root = root / "app" / "static" / "css"
    hdr_css_candidates = [
        css_root/"src/components/header.css",
        css_root/"fc_prestige-header.css",
        css_root/"header-safe.css",
    ]
    found = []
    for p in hdr_css_candidates:
        if p.exists() and "#hdr-meter" in read_text(p):
            found.append(rel(css_root, p))
    record("Header mini meter styles present", len(found) >= 1,
           details=("Found in: "+", ".join(found) if found else "Not found"),
           advice="Ensure #hdr-meter .track and .fill are defined (responsive width/height).")

def main():
    ap = argparse.ArgumentParser(description="FundChamps Repo Auditor")
    ap.add_argument("--root", default=".", help="repo root (default: .)")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    check_templates(root)
    check_base_css_link(root)
    check_css_pipeline(root)
    check_api_endpoints(root)
    check_env(root)
    check_header_meter(root)

    # Write report
    report = Path("fundchamps_audit_report.md")
    lines = []
    lines.append(f"# FundChamps Audit Report\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_\n")
    passed = sum(1 for c in CHECKS if c["ok"])
    total = len(CHECKS)
    lines.append(f"**Summary:** {passed}/{total} checks passed.\n")
    for c in CHECKS:
        status = "✅ PASS" if c["ok"] else "❌ FAIL"
        lines.append(f"## {status} — {c['title']}\n")
        if c["details"]:
            lines.append(f"{c['details']}\n")
        if c["files"]:
            lines.append("**Files:**\n" + "\n".join(f"- `{f}`" for f in c["files"]) + "\n")
        if c["advice"]:
            lines.append(f"**Advice:** {c['advice']}\n")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {report.resolve()}")

if __name__ == "__main__":
    main()
