# scripts/starforge_template_hardener.py
#!/usr/bin/env python3
import re, sys, json
from pathlib import Path

ROOTS = ["app/templates"]
INCLUDE_RX = re.compile(r'{%\s*include\s+([\'"][^\'"]+[\'"])([^%}]*)%}')
UI_IMPORT_RX = re.compile(
    r'{%\s*(from|import)\s+["\']partials/ui_bootstrap\.html["\'][^%]*%}'
)

def patch_include(m):
    path, tail = m.group(1), m.group(2) or ""
    t = tail
    if "ignore missing" not in t:
        t = (t + " ignore missing").rstrip()
    if "with context" not in t:
        t = (t + " with context").rstrip()
    # normalize spaces
    t = " " + " ".join(t.split())
    return "{% include " + path + t + " %}"

def process_file(p: Path, apply: bool):
    src = p.read_text(encoding="utf-8")
    orig = src

    # 1) Harden includes
    src = INCLUDE_RX.sub(patch_include, src)

    # 2) Detect fragile ui_bootstrap imports
    ui_hits = bool(UI_IMPORT_RX.search(src))

    changed = (src != orig)
    if apply and changed:
        p.write_text(src, encoding="utf-8")

    return {
        "file": str(p),
        "changed": changed,
        "ui_bootstrap_import_found": ui_hits
    }

def main():
    apply = "--apply" in sys.argv
    files = []
    for root in ROOTS:
        for p in Path(root).rglob("*.html"):
            files.append(process_file(p, apply))

    report = {
        "mode": "apply" if apply else "check",
        "summary": {
            "scanned": len(files),
            "changed": sum(1 for f in files if f["changed"]),
            "ui_bootstrap_imports": [
                f["file"] for f in files if f["ui_bootstrap_import_found"]
            ]
        },
        "files": files
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

