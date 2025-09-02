#!/usr/bin/env python3
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEARCH_DIRS = ["app", "templates", "static"]

patterns = {
    "import_stripe_bp": re.compile(r"from\s+app\.routes(?:\.stripe)?\s+import\s+stripe_bp"),
    "use_stripe_bp": re.compile(r"\bstripe_bp\b"),
    "legacy_routes_mod": re.compile(r"from\s+app\.routes\.routes\s+import\b|\bapp\.routes\.routes\b"),
    "direct_stripe_routes": re.compile(r"/stripe/(checkout|webhook)"),
}

hits = []
for base in SEARCH_DIRS:
    root = os.path.join(ROOT, base)
    if not os.path.isdir(root):
        continue
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith((".py", ".html", ".js", ".ts", ".jinja", ".j2")):
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, "r", encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for key, rx in patterns.items():
                for m in rx.finditer(text):
                    line_no = text[:m.start()].count("\n")+1
                    hits.append((key, path, line_no, m.group(0)[:120]))

if not hits:
    print("✅ No legacy references found.")
    sys.exit(0)

print("⚠️ Found possible legacy references:")
for key, path, ln, frag in hits:
    print(f" - [{key}] {path}:{ln}: {frag}")
sys.exit(1)
