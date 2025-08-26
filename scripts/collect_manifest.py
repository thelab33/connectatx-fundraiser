# scripts/collect_manifest.py
import os, sys, json, subprocess, pathlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manifest"
OUT.mkdir(exist_ok=True, parents=True)

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return f"ERROR({e.returncode}):\n{e.output}"

def write(name, content):
    p = OUT / name
    p.write_text(content if isinstance(content, str) else json.dumps(content, indent=2), encoding="utf-8")
    print("wrote", p)

# Basic environment
write("env.json", {
    "python": run("python3 -V").strip(),
    "node":   run("node -v").strip(),
    "npm":    run("npm -v").strip(),
})

# Python deps
write("pip_freeze.txt", run("python3 -m pip freeze"))

# Try Flask routes (best effort; ignore errors)
write("flask_routes.txt", run("FLASK_APP=app:create_app flask routes"))

# File tree (Python-only, avoids 'tree' dependency)
def list_tree(base: Path, depth=3, ignore=None):
    ignore = ignore or {".git","node_modules",".venv","__pycache__","app/data","migrations/versions/__pycache__"}
    items = []
    for p in base.rglob("*"):
        rel = p.relative_to(base)
        if any(str(rel).split("/")[0] in ignore for _ in [0]):
            continue
        if len(rel.parts) > depth: 
            continue
        items.append(str(rel))
    return sorted(items)

write("tree.json", list_tree(ROOT))

# Look for app factory + common files
hints = {}
for guess in ["app/__init__.py","app/factory.py","wsgi.py"]:
    p = ROOT / guess
    hints[guess] = p.exists()
write("hints.json", hints)

print("Manifest collected in ./manifest/")

